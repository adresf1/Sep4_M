#!/usr/bin/env python
# coding: utf-8

import sys, os
from flask import Flask, request, jsonify
import pandas as pd
from TrainRFCModel import train_RFC_model
from Predict import unpack_model, makePrediction, REQUIRED_FIELDS_RFC
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pandas as pd
import string

import joblib
from sklearn.ensemble import RandomForestClassifier
from datetime import datetime

app = Flask(__name__)
_model_cache = {}

def save_model_to_folder(rfc, model_name, folder_name):

    # Check if the folder exists, if not create it
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    
    # Generate the full file path
    model_filename = f"{model_name}.joblib"
    model_path = os.path.join(folder_name, model_filename)
    
    # Check if a model with the same name already exists
    if os.path.exists(model_path):
        # If conflict exists, append a timestamp to the file name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_filename = f"{model_name}_{timestamp}.joblib"
        model_path = os.path.join(folder_name, model_filename)
    
    # Save the model
    joblib.dump(rfc, model_path)
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
        # Extract metadata from the incoming JSON request
        model_name = data.get('model_name')
        table_name = data.get('table_name')
        target_measure = data.get('target_measure')
        test_size = float(data.get('test_size', 0.2))
        estimators = int(data.get('estimators', 100))
        random_state = int(data.get('random_state', 42))

        if not table_name or not target_measure or not model_name:
            return jsonify({"error": "Missing required fields: 'table_name', 'model_name' and 'target_measure'"}), 400

        DATABASE_URL = data.get('db_url')
        # Get the model class for the given table name
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
        #string targetMeasure,dataframe trainningData,float testSize, int estimators, int randomState
        # Train the model and get the evaluation metrics
        rfc, msg = train_RFC_model(targetMeasure=target_measure,trainningData=df, testSize=test_size, estimators=42, randomState=random_state)

        # Save the trained model to a binary file
        model_name = save_model_to_folder(rfc, model_name, "TrainedModels")
        # Return a success response with the model filename and evaluation metrics
        response = {
            "status": "success",
            "message": "Model trained successfully.",
            "model_filename": model_name,
            "evaluation_metrics": msg
        }

        return jsonify(response), 200

    except Exception as e:
        print("Hello before exception")
        print(str(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        return jsonify({"error": f"Failed to process request: {str(e)}"}), 500

    finally:
        session.close()

# API endpoint to train the model
@app.route('/predict', methods=['POST'])
def predict():
    try:
        payload = request.get_json(force=True)

        # Check for required top-level keys
        if not all(k in payload for k in ['TypeofModel', 'NameOfModel', 'Data']):
            return jsonify({"error": "Missing required top-level keys"}), 400

        model_type = payload['TypeofModel']
        model_name = payload['NameOfModel']
        data = payload['Data']

        # If model is 'rfc', validate data keys
        if model_type.lower() == 'rfc':
            missing_fields = REQUIRED_FIELDS_RFC - data.keys()
            if missing_fields:
                return jsonify({
                    "error": f"Missing fields for 'rfc' model: {', '.join(missing_fields)}"
                }), 400
        

        model = unpack_model(model_name,"TrainedModels")
        result = makePrediction(model, data)
        print(result)
        # Return detailed success response
        return jsonify({
            "status": "success",
            "message": "Prediction completed successfully.",
            "model_used": model_name,
            "result": result  # Cast to native type
        })

    except Exception as e:
        print(str(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print("Hello before exeption")    
        print(exc_type, fname, exc_tb.tb_lineno)
        return jsonify({"error": str(e),
                        "ErrorInfo": str(exc_type) + str(fname) + str(exc_tb.tb_lineno)
                        }), 500



# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0', port=5000)






