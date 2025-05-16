#!/usr/bin/env python
# coding: utf-8

import sys, os
from flask import Flask, request, jsonify, abort
from werkzeug.exceptions import HTTPException
import pandas as pd
from TrainRFCModel import train_model
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
from dotenv import load_dotenv
load_dotenv()


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
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "No JSON data provided"}), 400
    
    session = None #Session bliver oprettet i try-blokken
    try:
        model_name = data.get('model_name')
        table_name = data.get('table_name')
        target_measure = data.get('target_measure')
        test_size = float(data.get('test_size', 0.2))
        estimators = int(data.get('estimators', 100))
        random_state = int(data.get('random_state', 42))
        model_type = data.get('model_type') 

        if not table_name or not target_measure or not model_name:
            return jsonify({"error": "Missing required fields: 'table_name', 'model_name' and 'target_measure'"}), 400

        #DATABASE_URL = data.get('DATABASE_URL', os.getenv('DATABASE_URL'))
        DATABASE_URL = os.getenv('DATABASE_URL')
        if not DATABASE_URL:
            return jsonify({"error": "DATABASE_URL not provided and not found in environment variables."}), 400
        
        
        PlantModel = get_model_for_table(table_name, DATABASE_URL)
        engine = create_engine(DATABASE_URL)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Query all data from the table
        data = session.query(PlantModel).all()
        if not data:
            return jsonify({"error":f"No data found in the table. '{table_name}'."}), 404
        # Convert the queried data to a DataFrame
        df = pd.DataFrame([plant.to_dict() for plant in data])
        
        # Train the RandomForest model
        rfc, msg = train_model(targetMeasure=target_measure, trainningData=df, testSize=test_size, estimators=42, randomState=random_state,  model_type=model_type)

        # Save the trained RandomForest model to a binary file
        model_name = save_model_to_folder(rfc, model_name, "TrainedModels")
        
        # Return a success response with the model filename and evaluation metrics
        response = {
            "status": "success",
            "message": "RandomForest model trained successfully.",
            "model_filename": model_name,
            "evaluation_metrics": msg
        }

        return jsonify(response), 200

    except HTTPException: 
        raise

    except Exception as e:
        print(str(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        return jsonify({"error": f"Failed to process request: {str(e)}"}), 500

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