#!/usr/bin/env python
# coding: utf-8

# In[1]:


from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder , StandardScaler

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report , confusion_matrix, precision_score,recall_score, f1_score
import pandas as pd



# In[2]:


#Using Arbitrary Kword Arguments
#    try:
#      print(x)
#    except:
#      print("An exception occurred")

#args['targetMeasure'] = 'Growth_Milestone' in demo set
# currentSignature (string targetMeasure,dataframe trainningData,float testSize, int estimators, int randomState)
def train_RFC_model(**args):
    df = args['trainningData']
    
    if len(df.columns) < 2:
        raise Exception("DataFrame contains less than 2 columns and cant be used for training")

    if len(df) < 10:
        raise Exception("DataFrame contains less than 10 rows and cant be used for training")
    # Remove 'id' column if present
    if 'id' in df.columns:
        df = df.drop(['id'], axis=1)
        
    num_cols = df.select_dtypes(include = ['int64','float64']).columns
    cat_cols = df.select_dtypes(include = ['object']).columns

    try: 
        label_encoder = LabelEncoder()
        for col in cat_cols:
            df[col] = label_encoder.fit_transform(df[col])
        
        x= df.drop([args['targetMeasure']],axis=1)
        y= df[args['targetMeasure']]
        
    except Exception as e:
        print(str(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        raise Exception("Exception in label encoding: " + repr(e))
        

    try:
        # Convert DataFrame to a list of dictionaries
        df_dict = df.to_dict(orient='records')
        #store og små bogstaver ved variablerne 
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
        #create and train classifier
        rfc = RandomForestClassifier(n_estimators = args['estimators'] , random_state=args['randomState'])
        rfc.fit(X_train,y_train)
        
        #create precisson variables
        rfc_pred = rfc.predict(X_test)
        precision = precision_score(rfc_pred, y_test)
        recall = recall_score(rfc_pred,y_test)
        f1 = f1_score(y_test,rfc_pred)
        
        #Package info to an array 
        msg = [
            f'Accuracy Score: {accuracy_score(rfc_pred,y_test)}',
            f'Precision: {precision}',
            f'Recall: {recall}',
            f'F1-score: {f1}',
        ]
    except Exception as e:
        print(str(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        raise Exception("Exception in calculation of precission: " + repr(e))
    
    return [rfc,msg]
    





