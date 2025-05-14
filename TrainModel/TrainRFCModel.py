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
   ##Dispatch to train_rfc or train_lr based on args['model_type'].
   df = args.get('trainning_data')
   target_measure = args.get('target_measure')
   test_size = args.get('test_size')
   random_state = args.get('random_state')
   model_type = args.get('model_type')

   if model_type == 'random_forest':
       return train_rfc(df, target_measure, test_size, random_state, n_estimators=args.get('n_estimators', 100), max_depth=args.get('max_depth'))
   elif model_type == 'logistic_regression':
         return train_lr(df, target_measure, test_size, random_state, solver=args.get('solver', 'lbfgs'), penalty=args.get('penalty', 'l2'), C=args.get('C', 1.0), max_iter=args.get('max_iter', 1000))
   else:
       raise ValueError(f"Unsupported model type: {model_type}. Supported types are 'random_forest' and 'logistic_regression'.")

# Function to train the model (Random Forest or Logistic Regression)

def _common_preprocessing(df,target_measure, test_size, random_state):
    #Delt preprocessing: fjernet 'id', label-encoding og standardisering
    #Split data into train/test, and stadardize numeric features
    #returns X_train, X_test, y_train, y_test.

    df = df.copy()
    #validate dataframe
    if len(df.columns) < 2:
        raise Exception("DataFrame contains less than 2 columns and can't be used for training")
    if( len(df) < 10):
        raise Exception("DataFrame contains less than 10 rows and can't be used for training")
    #drop 'id' column if present
    if 'id' in df.columns:
        df = df.drop(['id'], axis=1)
    
    #label-encoding of categorical columns
    cat_cols = df.select_dtypes(include=['object','category']).columns.tolist()
    le = LabelEncoder()
    for col in cat_cols:
        df[col] = le.fit_transform(df[col])
    
    #Seperate X and y
    if target_measure not in df.columns:
        raise KeyError(f"Target measure '{target_measure}' not found in DataFrame columns")
    X = df.drop([target_measure], axis=1)
    y = df[target_measure]
    #Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)
    #Standardize numeric features
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

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

    clf = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth, random_state=random_state)
    clf.fit(X_train, y_train)
    pred = clf.predict(X_test)

    #metrics
    metrics = {
        'accuraxy': accuracy_score(y_test, pred),
        'precesion': precision_score(y_test, pred,zero_division=0),
        'recall': recall_score(y_test, pred,zero_division=0),
        'f1': f1_score(y_test, pred,zero_division=0),
    }
    return clf, metrics

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

    clf = LogisticRegression(solver=solver, penalty=penalty, C=C, max_iter=max_iter, random_state=random_state)
    clf.fit(X_train, y_train)
    pred = clf.predict(X_test)

    #metrics
    metrics = {
        'accuraxy': accuracy_score(y_test, pred),
        'precesion': precision_score(y_test, pred,zero_division=0),
        'recall': recall_score(y_test, pred,zero_division=0),
        'f1': f1_score(y_test, pred,zero_division=0),
    }
    return clf, metrics


    