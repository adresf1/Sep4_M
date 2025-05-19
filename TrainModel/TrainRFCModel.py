#!/usr/bin/env python
# coding: utf-8

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression  # Import Logistic Regression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, precision_score, recall_score, f1_score
from sklearn.pipeline import Pipeline
import pandas as pd
import sys
import os

# Function to train the model (Random Forest or Logistic Regression)
def train_model(X_train,X_test,y_train, y_test, model_type, estimators=100, max_depth=None, solver='lbfgs', penalty='l2', C=1.0, max_iter=1000, random_state=None):
   ##Dispatch to train_rfc or train_lr based on args['model_type'].
#    df = args.get('trainningData')
#    target_measure = args.get('targetMeasure')
#    test_size = args.get('testSize')
#    random_state = args.get('randomState')
#    model_type = args.get('model_type')

   if model_type == 'random_forest':
     clf = build_rfc_pipeline(estimators=estimators, max_depth=max_depth)
   elif model_type == 'logistic_regression':
       clf = LogisticRegression(solver=solver, penalty=penalty, C=C, max_iter=max_iter, random_state=random_state)
   else:
       raise ValueError(f"Unsupported model type: {model_type}. Supported types are 'random_forest' and 'logistic_regression'.")
   
   # Fit the model
   clf.fit(X_train, y_train)
   # Make predictions
   pred = clf.predict(X_test)
   
   # Calculate metrics
   metrics = {
        'accuracy': accuracy_score(y_test, pred),
        'precision': precision_score(y_test, pred, zero_division=0),
        'recall': recall_score(y_test, pred, zero_division=0),
        'f1': f1_score(y_test, pred, zero_division=0),
    }
   return clf, metrics

# Function to train the model (Random Forest or Logistic Regression)

def _common_preprocessing(df,target_measure, test_size, random_state):
    #Delt preprocessing: fjernet 'id', label-encoding og standardisering
    #Split data into train/test, and stadardize numeric features
    #returns X_train, X_test, y_train, y_test.

    df = df.copy()
    df.columns = df.columns.str.strip()  # Strip whitespace from column names
    #validate dataframe
    if len(df.columns) < 2:
        raise Exception("DataFrame contains less than 2 columns and can't be used for training")
    if( len(df) < 10):
        raise Exception("DataFrame contains less than 10 rows and can't be used for training")
    #drop 'id' column if present
    if 'id' in df.columns:
        df = df.drop(['id'], axis=1)

    #check target kolonne
    if target_measure not in df.columns:
        raise KeyError(f"Target measure columns '{target_measure}' not found in DataFrame columns")    

    #split X/y
    X = df.drop([target_measure], axis=1)
    y = df[target_measure]

    #  #Find kolonner
    # cat_columns = df.select_dtypes(include=['object', 'category']).columns.tolist()
    # num_columns = [c for c in df.columns if c not in cat_columns + [target_measure]]

    
    # #ColumnTransformer: OneHotEncoder for categorical features, StandardScaler for numeric features
    # preprocessor = ColumnTransformer([
    #     ('cat', OneHotEncoder(drop='first', handle_unknown='ignore'), cat_columns),
    #     ('num', StandardScaler(), num_columns),
    # ])

    # #Pipeline med preprocessor + identitet
    # pipeline = Pipeline([
    #     ('preprocessor', preprocessor),
    # ])

    #Split data into train/test
    X_train,X_test,y_train,y_test = train_test_split(X,y,test_size=test_size,random_state=random_state)

    #Fit preprocessor to training data
    # X_train = pipeline.fit_transform(X_train)
    # X_test = pipeline.transform(X_test)

    return X_train, X_test, y_train, y_test    

def train_rfc(df,target_measure,test_size,random_state,n_estimators=100, max_depth=None):
    #Train a Random Forest Classifier and return the model and metrics
    #df: DataFrame with training data
    #target_measure: name of the target measure column
    #test_size: size of the test set (0-1)
    #random_state: random state for reproducibility
    #n_estimators: number of trees in the forest (default=100)
    #max_depth: maximum depth of the trees (default=None)

    X_train, X_test, y_train, y_test = _common_preprocessing(df,target_measure,test_size,random_state)

    return train_model(X_train,X_test,y_train, y_test, 'random_forest', estimators=n_estimators, max_depth=max_depth, random_state=random_state)

def train_lr(df,target_measure, test_size,random_state,solver='lbfgs',penalty='l2',C=1.0,max_iter=1000):
    #Train a Logistic Regression model and return the model and metrics
    #df: DataFrame with training data
    #target_measure: name of the target measure column
    #test_size: size of the test set (0-1)
    #random_state: random state for reproducibility
    #solver: solver to use (default='lbfgs')
    #penalty: penalty to use (default='l2')
    #C: inverse of regularization strength (default=1.0)
    #max_iter: maximum number of iterations (default=1000)

    X_train, X_test, y_train, y_test = _common_preprocessing(df,target_measure,test_size,random_state)

    return train_model(X_train,X_test,y_train, y_test, 'logistic_regression', solver=solver, penalty=penalty, C=C, max_iter=max_iter, random_state=random_state)

#Ny Pipeline-builder og save-funktion

def build_lr_pipeline():
    """Bygger en pipeline med OneHotEncoder og kategoriske features
    og standardiserer numeriske features, og til sidst en LogisticRegression-model.
    """
    cat_features = ['soil_type','water_frequency','fertilizer_type']
    num_features = ['sunlight_hours', 'temperature', 'humidity']

    # Preprocessing pipeline
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore'), cat_features),
            ('num', StandardScaler(), num_features)
        ]
    )

    # Full pipeline
    pipeline = Pipeline(steps=[
        ('pre', preprocessor),
        ('clf', LogisticRegression(max_iter=1000,random_state=42))
    ])

    return pipeline

## RFC-pipeline
def build_rfc_pipeline(estimators=100, max_depth=None):
    """Bygger en pipeline med OneHotEncoder og kategoriske features
    og standardiserer numeriske features, og til sidst en RandomForestClassifier-model.
    """
    cat_features = ['soil_type','water_frequency','fertilizer_type']
    num_features = ['sunlight_hours', 'temperature', 'humidity']

    # Preprocessing pipeline
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore'), cat_features),
            ('num', StandardScaler(), num_features)
        ]
    )

    # Full pipeline
    pipeline = Pipeline(steps=[
        ('pre', preprocessor),
        ('clf', RandomForestClassifier(n_estimators=estimators, max_depth=max_depth, random_state=42))
    ])
    return pipeline

def train_and_save_lr_model(X_train,y_train,model_name):
    pipeline = build_lr_pipeline()
    pipeline.fit(X_train, y_train)
    #Genbruger 'save_model_to_folder' fra ModelTrainingAPI
    from ModelTrainingAPI import save_model_to_folder
    filename = save_model_to_folder(pipeline, model_name, "TrainedModels")
    print("Saved LR model as:", filename)
    return filename
