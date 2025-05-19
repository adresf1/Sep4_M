#!/usr/bin/env python
# coding: utf-8

import sys, os
from flask import Flask, request, jsonify, abort
from werkzeug.exceptions import HTTPException
import pandas as pd
from TrainRFCModel import train_model, _common_preprocessing, train_and_save_lr_model
from Predict import unpack_model, makePrediction, REQUIRED_FIELDS_RFC
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.automap import automap_base
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression  # Import Logistic Regression
from datetime import datetime
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.model_selection import train_test_split
from dotenv import load_dotenv
load_dotenv()

ALLOWED_MODEL_TYPES ={'random_forest', 'logistic_regression'}
SHORTCUT_MAP = {
    'rfc': 'random_forrest',
    'rf': 'random_forest',
    'lr': 'logistic_regression',
    'logistic': 'logistic_regression',
}


app = Flask(__name__)
_model_cache = {}

def save_model_to_folder(model, model_name, folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    model_filename = f"{model_name}.joblib"
    model_path = os.path.join(os.getcwd(), folder_name, model_filename)
    if os.path.exists(model_path):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_filename = f"{model_name}_{timestamp}.joblib"
        model_path = os.path.join(os.getcwd(), folder_name, model_filename)
    joblib.dump(model, model_path)
    print(f"Model saved to {model_path}")
    return model_filename

#Hjælpefunktion til at klasser bliver oprettet med automap_base
def add_to_dict(cls):
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in cls.__table__.columns}
    cls.to_dict = to_dict
    return cls

def create_plant_data_class(table_name: str, engine):
    Base = automap_base()
    Base.prepare(engine, reflect=True)

    try:
        cls = getattr(Base.classes, table_name)
        return add_to_dict(cls)
    except AttributeError:
        raise RuntimeError(f"Table '{table_name}' not found in the database.")

def get_model_for_table(table_name, DATABASE_URL):
    if table_name not in _model_cache:
        engine = create_engine(DATABASE_URL)
        _model_cache[table_name] = create_plant_data_class(table_name, engine)
    return _model_cache[table_name]

# API endpoint to train the model
@app.route('/train', methods=['POST'])
def train():
    data = request.get_json(force=True)

    if not data:
        return jsonify({"error": "No JSON data provided"}), 400

    # Tvangsfelter: model_name, table_name, target_measure (understøtter camelCase og snake_case)
    model_name = data.get('model_name')
    table_name = data.get('table_name')
    target_measure = data.get('targetMeasure') or data.get('target_measure')
    model_type = data.get('model_type', 'random_forest')  # default til random_forest

    # Brug eksplicit kontrol i stedet for locals()[k] for at undgå KeyError
    missing_fields = []
    if not model_name:
        missing_fields.append('model_name')
    if not table_name:
        missing_fields.append('table_name')
    if not target_measure:
        missing_fields.append('target_measure')

    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400


    # Model-type validering + mapping
    model_type = model_type.lower()
    model_type = SHORTCUT_MAP.get(model_type, model_type)
    if model_type not in ALLOWED_MODEL_TYPES:
        return jsonify({"error": f"Invalid model type '{model_type}'. Allowed types are: {', '.join(ALLOWED_MODEL_TYPES)}"}), 400

    # Hent parametre fra payload
    test_size = float(data.get('testSize', 0.2))
    random_state = int(data.get('randomState', 42))

    # RFC parametre
    estimators = int(data.get('estimators', 100))
    max_depth = data.get('max_depth')
    if max_depth is not None:
        max_depth = int(max_depth)

    # LR parametre
    solver = data.get('solver', 'lbfgs')
    penalty = data.get('penalty', 'l2')
    C = float(data.get('C', 1.0))
    max_iter = int(data.get('max_iter', 1000))

    # Database URL
    DATABASE_URL = data.get('db_url') or os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        return jsonify({"error": "DATABASE_URL not set in environment variables"}), 500

    try:
        # ORM-model og data
        PlantModel = get_model_for_table(table_name, DATABASE_URL)
        engine = create_engine(DATABASE_URL)
        Session = sessionmaker(bind=engine)
        session = Session()

        records = session.query(PlantModel).all()
        if not records:
            return jsonify({"error": f"No records found in table '{table_name}'"}), 404

        # Konverter til DataFrame
        df = pd.DataFrame([record.to_dict() for record in records])
        #Fjern whitespace fra kolonnenavne
        df.columns = df.columns.str.strip()
        # print("DF COLUMNS:", df.columns.to_list())
        # print("DROPPING:", target_measure)

        #Split data i X og y
        #X = df.drop([target_measure], axis=1)
        #y = df[target_measure]

        print(">>> TYPE OF df:", type(df), " | VALUE:", df)
        print(">>> TARGET_MEASURE:", repr(target_measure))

        X_train, X_test, y_train, y_test = _common_preprocessing(df, target_measure, test_size, random_state)

        metrics = {}
        filename = None

        if model_type == 'logistic_regression':
            base_name = f"{model_name}_{model_type}"
            #træn og gem pipeline
            filename = train_and_save_lr_model(X_train,y_train, base_name)
            #Evaluering af pipeline:
            from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
            pipeline = joblib.load(os.path.join("TrainedModels", filename))
            prediction = pipeline.predict(X_test)
            metrics = {
                'accuracy': round(accuracy_score(y_test, prediction),4),
                'precision':round(precision_score(y_test, prediction, zero_division=0)),
                'recall': round(recall_score(y_test, prediction, zero_division=0),4),
                'f1': round(f1_score(y_test, prediction, zero_division=0),4),
            }
        else:
            #til train dispatcher
            clf, metrics = train_model(
            X_train=X_train,
            X_test=X_test,
            y_train=y_train,
            y_test=y_test,
            model_type=model_type,
            estimators=estimators,
            max_depth=max_depth,
            solver=solver,
            penalty=penalty,
            C=C,
            max_iter=max_iter,
            random_state=random_state
        )

            # Gem modellen
            filename = save_model_to_folder(clf, f"{model_name}_{model_type}", "TrainedModels")

        return jsonify({
            "status": "success",
            "message": f"{model_type.replace('_', ' ').title()} model trained successfully.",
            "model_name": filename,
            "evaluation_metrics": metrics
        }), 200

    except HTTPException:
        raise
    except Exception as e:
        app.logger.error(f"Error in /train: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        if session is not None:
            session.close()

@app.route('/predict', methods=['POST'])
def predict():
    try:
        payload = request.get_json(force=True)
        if not payload:
            return jsonify({"error": "No JSON data provided"}), 400
        if 'Data' not in payload or not isinstance(payload['Data'], dict):
            return jsonify({"error": "Invalid or missing 'Data' field"}), 400
        if 'NameOfModel' not in payload:
            return jsonify({"error": "Missing 'NameOfModel' field"}), 400

        # Identifikation af modeltype
        model_type = payload.get('TypeofModel') or 'logistic_regression'
        model_name = payload.get('NameOfModel') or payload.get('ModelName')
        data = payload.get('Data')
        #normaliser data
        data_dict = {}
        for k, v in data.items():
            key = ''.join(['_'+c.lower() if c.isupper()else c for c in k]).lstrip('_')
            data_dict[key.replace(' ', '_')] = v

        if not model_name or not data:
            return jsonify({"error": "Missing 'ModelName' or 'Data'"}), 400

        # RFC logik
        if model_type.lower() in ['rfc', 'random_forest']:
            # Valider påkrævede felter
            missing_fields = REQUIRED_FIELDS_RFC - data_dict.keys()
            if missing_fields:
                return jsonify({
                    "error": f"Missing fields for Random Forest model: {', '.join(missing_fields)}"
                }), 400

            # Grænseværdi-validering for RFC

            if not (1 <= data_dict['sunlight_hours'] <= 24):
                return jsonify({"error": "Sunlight_Hours must be between 1 and 24"}), 400
            if not (0 <= data_dict['temperature'] <= 50):
                return jsonify({"error": "Temperature must be between 0 and 50"}), 400
            if not (10 <= data_dict['humidity'] <= 100):
                return jsonify({"error": "Humidity must be between 10 and 100"}), 400

            model = unpack_model(model_name, "TrainedModels")
            result = makePrediction(model, data_dict)

            return jsonify({
                "status": "success",
                "message": "Random Forest prediction completed successfully.",
                "model_used": model_name,
                "result": result
            }), 200

        # Logistic Regression logik
        elif model_type.lower() in ['logistic', 'logistic_regression']:
            if not (1 <= data_dict['sunlight_hours'] <= 24):
                return jsonify({"error": "Sunlight_Hours must be between 1 and 24"}), 400
            if not (0 <= data_dict['temperature'] <= 50):
                return jsonify({"error": "Temperature must be between 0 and 50"}), 400
            if not (10 <= data_dict['humidity'] <= 100):
                return jsonify({"error": "Humidity must be between 10 and 100"}), 400

            model_path = os.path.join("TrainedModels", model_name)
            if not os.path.exists(model_path):
                return jsonify({"error": f"Model '{model_name}' not found in TrainedModels"}), 404

            pipeline_model = joblib.load(model_path)
            df_input = pd.DataFrame([data_dict])

            prediction = pipeline_model.predict(df_input)[0]
            probability = pipeline_model.predict_proba(df_input)[0].max()

            return jsonify({
                "status": "success",
                "message": "Logistic Regression prediction completed successfully.",
                "model_used": model_name,
                "prediction": int(prediction),
                "confidence": round(float(probability), 4)
            }), 200

        else:
            return jsonify({"error": f"Unsupported model type '{model_type}'"}), 400

    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except KeyError as e:
        return jsonify({"error": f"Missing key: {str(e)}"}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        import traceback
        return jsonify({
            "error": str(e),
            "trace": traceback.format_exc()
        }), 500
    


@app.route('/models', methods=['GET'])
def list_models():
    try:
        # Udgangspunkt i app.py's placering (TrainModel/)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        models_folder = os.path.join(current_dir, 'TrainedModels')  # kun ét trin ned

        if not os.path.exists(models_folder):
            return jsonify({"error": "Models folder not found."}), 404

        model_files = [
            f for f in os.listdir(models_folder)
            if os.path.isfile(os.path.join(models_folder, f)) and f.endswith('.joblib')
        ]


        return jsonify({
            "status": "success",
            "model_files": model_files
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)