#!/usr/bin/env python
# coding: utf-8

from flask import jsonify
import os
import shutil
from joblib import load
import pandas as pd

# Expected fields for 'rfc' models
REQUIRED_FIELDS_RFC = {
    "soil_type",
    "sunlight_hours",
    "water_frequency",
    "fertilizer_type",
    "temperature",
    "humidity"
}

def unpack_model(model_filename, target_folder="TrainedModels"):
    print("Working directory:", os.getcwd())
    print("model_filename:", model_filename)

        # Create the folder if it doesn't exist
    os.makedirs(target_folder, exist_ok=True)
    
    # Get the base filename
    base_filename = os.path.basename(model_filename)
    
    # Build the target path
    target_path = os.path.join(os.getcwd(),target_folder, base_filename)
    print("target_path:", target_path)
    
    # Load and return the model
    model = load(target_path)
    return model

def makePrediction(model, data):
    # Prepare data for prediction
    input_df = pd.DataFrame([data])  # Single-row DataFrame

    # Run prediction
    prediction = model.predict_proba(input_df)

    # Return result
    return prediction.tolist()[0] 

    

