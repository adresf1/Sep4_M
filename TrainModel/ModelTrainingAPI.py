#!/usr/bin/env python
# coding: utf-8

import sys, os
from flask import Flask, request, jsonify
import pandas as pd
from TrainRFCModel import train_model
from Predict import unpack_model, makePrediction, REQUIRED_FIELDS_RFC
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression  # Import Logistic Regression
from datetime import datetime
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder

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

def get_model_for_table(table_name, DATABASE_URL):
    if table_name not in _model_cache:
        engine = create_engine(DATABASE_URL)
        _model_cache[table_name] = create_plant_data_class(table_name)
    return _model_cache[table_name]

# API endpoint to train the model
@app.route('/train', methods=['POST'])
def train():
    # Get the incoming JSON data from the request
    data = request.get_json()

    if not data:
        return jsonify({"error": "No JSON data provided"}), 400

    try:
        model_name = data.get('model_name')
        table_name = data.get('table_name')
        target_measure = data.get('target_measure')
        test_size = float(data.get('test_size', 0.2))
        estimators = int(data.get('estimators', 100))
        random_state = int(data.get('random_state', 42))

        if not table_name or not target_measure or not model_name:
            return jsonify({"error": "Missing required fields: 'table_name', 'model_name' and 'target_measure'"}), 400

        DATABASE_URL = data.get('db_url')
        PlantModel = get_model_for_table(table_name, DATABASE_URL)

        engine = create_engine(DATABASE_URL)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Query all data from the table
        data = session.query(PlantModel).all()
        if not data:
            return jsonify({"error": f"No data found for table '{table_name}'"}), 404

        # Convert the queried data to a DataFrame
        df = pd.DataFrame([plant.to_dict() for plant in data])
        
        # Train the RandomForest model
        rfc, msg = train_model(targetMeasure=target_measure, trainningData=df, testSize=test_size, estimators=42, randomState=random_state)

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

    except Exception as e:
        print(str(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        return jsonify({"error": f"Failed to process request: {str(e)}"}), 500

    finally:
        session.close()

# API endpoint for RandomForest predictions
@app.route('/rfc_predict', methods=['POST'])
def rfc_predict():
    try:
        payload = request.get_json(force=True)

        # Check for required top-level keys
        if not all(k in payload for k in ['TypeofModel', 'NameOfModel', 'Data']):
            return jsonify({"error": "Missing required top-level keys"}), 400

        model_type = payload['TypeofModel']
        model_name = payload['NameOfModel']
        data = payload['Data']

        # If model is 'random_forest', validate data keys
        if model_type.lower() == 'random_forest':
            missing_fields = REQUIRED_FIELDS_RFC - data.keys()  # Adjust fields for RandomForest
            if missing_fields:
                return jsonify({
                    "error": f"Missing fields for 'random_forest' model: {', '.join(missing_fields)}"
                }), 400

        # Unpack and load the RandomForest model
        model = unpack_model(model_name, "TrainedModels")
        
        # Make prediction
        result = makePrediction(model, data)
        
        return jsonify({
            "status": "success",
            "message": "Random Forest prediction completed successfully.",
            "model_used": model_name,
            "result": result  # Return result
        })

    except Exception as e:
        print(str(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        return jsonify({"error": str(e), "ErrorInfo": str(exc_type) + str(fname) + str(exc_tb.tb_lineno)}), 500

@app.route('/logistic_predict', methods=['POST'])
def logistic_predict():
    try:
        # Get the incoming JSON data
        payload = request.get_json(force=True)

        # Check for required keys in the payload
        if not all(k in payload for k in ['ModelName', 'Data']):
            return jsonify({"error": "Missing required top-level keys"}), 400

        model_name = payload['ModelName']
        data = payload['Data']

        # Load the trained Logistic Regression model using the unpack_model function
        model = unpack_model(model_name, "TrainedModels")

        if model is None:
            return jsonify({"error": "Model not found"}), 404

        # Prepare the data for prediction (one-hot encode categorical features)
        df = pd.DataFrame([data])

        # One-hot encode the categorical features
        df_encoded = pd.get_dummies(df, columns=['Soil_Type', 'Water_Frequency', 'Fertilizer_Type'], drop_first=True)

        # Ensure the columns in df_encoded match the model's expected features
        expected_columns = model.feature_names_in_  # Columns the model expects

        # Add missing columns with 0 values if any
        missing_cols = set(expected_columns) - set(df_encoded.columns)
        for c in missing_cols:
            df_encoded[c] = 0  # Add missing columns as 0

        # Ensure the columns are in the same order as the model's training data
        df_encoded = df_encoded[expected_columns]

        # Make the prediction
        prediction = model.predict_proba(df_encoded)  # Get probability predictions

        # Return the prediction result
        return jsonify({
            "status": "success",
            "message": "Logistic Regression prediction completed successfully.",
            "result": prediction.tolist()[0]  # Convert to list for JSON serialization
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)