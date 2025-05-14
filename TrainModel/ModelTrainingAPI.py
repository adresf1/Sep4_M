#!/usr/bin/env python
# coding: utf-8

import sys, os
from flask import Flask, request, jsonify, abort
from werkzeug.exceptions import HTTPException
import pandas as pd
from TrainRFCModel import train_model, train_rfc, train_lr
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
    # Get the incoming JSON data from the request
    data = request.get_json(silent=True) or {}

   #Validering af payload
    missing = [f for f in ['model_name','table_name','targetMeasure','model_type'] if not data.get(f)]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400
    #Model-type validering + mapping
    model_type = data.get('model_type', '').lower()
    model_type = SHORTCUT_MAP.get(model_type, model_type)
    if model_type not in ALLOWED_MODEL_TYPES:
        return jsonify({"error": f"invalid model type '{model_type}'. Allowed types are: {', '.join(ALLOWED_MODEL_TYPES)}"}), 400
    #Hent parametre fra payload
    model_name = data.get('model_name')
    table_name = data.get('table_name')
    target_measure = data.get('targetMeasure')
    test_size = float(data.get('testSize', 0.2))
    random_state = int(data.get('randomState', 42))
    #RFC parametre
    estimators = int(data.get('estimators', 100))
    max_depth = data.get('max_depth')
    if max_depth is not None:
        max_depth = int(max_depth)
    #LR parametre
    solver = data.get('solver', 'lbfgs')
    penalty = data.get('penalty', 'l2')
    C = float(data.get('C', 1.0))
    max_iter = int(data.get('max_iter', 1000))

    #Database URL
    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        return jsonify({"error": "DATABASE_URL not set in environment variables"}), 500
    #Indlæsning af ORM-model
    PlantModel = get_model_for_table(table_name, DATABASE_URL)
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    records = session.query(PlantModel).all()
    session.close()
    if not records:
        return jsonify({"error": f"No records found in table '{table_name}'"}), 404
    #Konvertering af records til DataFrame og split af data
    df = pd.DataFrame([record.to_dict() for record in records])
    x = df.drop([target_measure], axis=1)
    y = df[target_measure]
    X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=test_size, random_state=random_state)

    #bruger train_model til at dispatch til train_rfc eller train_lr
    args = {
        'trainningData': df,
        'targetMeasure': target_measure,
        'testSize': test_size,
        'randomState': random_state,
        'model_type': model_type,
        'estimators': estimators,
        'max_depth': max_depth,
        'solver': solver,
        'penalty': penalty,
        'C': C,
        'max_iter': max_iter
    }
    try:
        clf, metrics = train_model(**args)

        #Gem modellen med type i navnet
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
        return jsonify({
            "error": str(e)
        }), 500
    finally:
        if session is not None:
            session.close()
@app.route('/predict', methods=['POST'])
def predict():
    try:
        payload = request.get_json(force=True)

        # Identifikation af modeltype
        model_type = payload.get('TypeofModel') or 'logistic_regression'
        model_name = payload.get('NameOfModel') or payload.get('ModelName')
        data = payload.get('Data')

        if not model_name or not data:
            return jsonify({"error": "Missing 'ModelName' or 'Data'"}), 400

        # RFC logik
        if model_type.lower() in ['rfc', 'random_forest']:
            # Valider påkrævede felter
            missing_fields = REQUIRED_FIELDS_RFC - data.keys()
            if missing_fields:
                return jsonify({
                    "error": f"Missing fields for Random Forest model: {', '.join(missing_fields)}"
                }), 400

            # Grænseværdi-validering for RFC
            
            if not (1 <= data['sunlight_hours'] <= 24):
                return jsonify({"error": "Sunlight_Hours must be between 1 and 24"}), 400
            if not (0 <= data['temperature'] <= 50):
                return jsonify({"error": "Temperature must be between 0 and 50"}), 400
            if not (10 <= data['humidity'] <= 100):
                return jsonify({"error": "Humidity must be between 10 and 100"}), 400

            model = unpack_model(model_name, "TrainedModels")
            result = makePrediction(model, data)

            return jsonify({
                "status": "success",
                "message": "Random Forest prediction completed successfully.",
                "model_used": model_name,
                "result": result
            }), 200

        # Logistic Regression logik
        elif model_type.lower() in ['logistic', 'logistic_regression']:
            if not (1 <= data['Sunlight_Hours'] <= 24):
                return jsonify({"error": "Sunlight_Hours must be between 1 and 24"}), 400
            if not (0 <= data['Temperature'] <= 50):
                return jsonify({"error": "Temperature must be between 0 and 50"}), 400
            if not (10 <= data['Humidity'] <= 100):
                return jsonify({"error": "Humidity must be between 10 and 100"}), 400

            model_path = os.path.join(os.getcwd(), "TrainedModels", model_name)
            if not os.path.exists(model_path):
                return jsonify({"error": f"Model '{model_name}' not found in TrainedModels"}), 404

            pipeline_model = joblib.load(model_path)
            df_input = pd.DataFrame([data])

            prediction = pipeline_model.predict(df_input)[0]
            probability = max(pipeline_model.predict_proba(df_input)[0])

            return jsonify({
                "status": "success",
                "message": "Logistic Regression prediction completed successfully.",
                "model_used": model_name,
                "prediction": int(prediction),
                "confidence": round(float(probability), 4)
            }), 200

        else:
            return jsonify({"error": f"Unsupported model type '{model_type}'"}), 400

    except Exception as e:
        import traceback
        return jsonify({
            "error": str(e),
            "trace": traceback.format_exc()
        }), 500




if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)