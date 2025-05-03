#!/usr/bin/env python
# coding: utf-8

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression  # Import Logistic Regression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, precision_score, recall_score, f1_score
import pandas as pd
import sys
import os

# Function to train the model (Random Forest or Logistic Regression)
def train_model(**args):
    df = args['trainningData']
    
    if len(df.columns) < 2:
        raise Exception("DataFrame contains less than 2 columns and can't be used for training")

    if len(df) < 10:
        raise Exception("DataFrame contains less than 10 rows and can't be used for training")
    
    # Remove 'id' column if present
    if 'id' in df.columns:
        df = df.drop(['id'], axis=1)

    num_cols = df.select_dtypes(include=['int64', 'float64']).columns
    cat_cols = df.select_dtypes(include=['object']).columns

    try: 
        label_encoder = LabelEncoder()
        for col in cat_cols:
            df[col] = label_encoder.fit_transform(df[col])
        
        x = df.drop([args['targetMeasure']], axis=1)
        y = df[args['targetMeasure']]
        
    except Exception as e:
        print(str(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        raise Exception("Exception in label encoding: " + repr(e))

    try:
        # Convert DataFrame to a list of dictionaries
        df_dict = df.to_dict(orient='records')
        X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=args['testSize'], random_state=args['randomState'])

        # Standardize the features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
    except Exception as e: 
        print(str(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        raise Exception("Exception when reformatting Dataframe to training/test data: " + repr(e))
    
    try:
        # Choose model type (RandomForest or LogisticRegression)
        model_type = args['model_type'].lower()  # 'random_forest' or 'logistic_regression'
        
        if model_type == 'random_forest':
            model = RandomForestClassifier(n_estimators=args['estimators'], random_state=args['randomState'])
        elif model_type == 'logistic_regression':
            model = LogisticRegression(random_state=args['randomState'], max_iter=1000)  # Added max_iter for convergence
        else:
            raise Exception("Unsupported model type provided. Use 'random_forest' or 'logistic_regression'.")

        model.fit(X_train_scaled, y_train)

        # Predict using the trained model
        model_pred = model.predict(X_test_scaled)

        # Evaluate the model
        precision = precision_score(y_test, model_pred, average='binary')
        recall = recall_score(y_test, model_pred, average='binary')
        f1 = f1_score(y_test, model_pred, average='binary')

        # Package info to an array
        msg = [
            f'Accuracy Score: {accuracy_score(y_test, model_pred)}',
            f'Precision: {precision}',
            f'Recall: {recall}',
            f'F1-score: {f1}',
        ]
    except Exception as e:
        print(str(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        raise Exception("Exception in training model: " + repr(e))

    return [model, msg]

