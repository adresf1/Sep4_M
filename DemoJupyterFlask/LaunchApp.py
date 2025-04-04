from flask import Flask, request, jsonify
import pickle
import numpy as np
from sklearn.feature_extraction import DictVectorizer

with open('./model_GrowthPredict.bin', 'rb') as f_in:
    (dv, model) = pickle.load(f_in)

app = Flask('PredictedMilestoneSucces')


#Get data to predict on data 
newrecord = {
    'Soil_Type': 2.000000,
    'Sunlight_Hours': 6.822032,
    'Water_Frequency': 1.000000,
    'Fertilizer_Type': 1.000000,
    'Temperature': 15.509484,
    'Humidity': 35.940896 
}

print(newrecord)

import numpy as np
from sklearn.feature_extraction import DictVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
X=dv.transform(newrecord)
newArray=np.delete(X, 1, axis=1)
# Remove the last column (the last 0) from the array
#why in ever loving #%!%#% is there 7 features from the transform on an oject with 6 features....
#newArray = X[:, :-1]
print(newArray)

@app.route('/predict', methods=['POST'])
def predict():
    probabilities=model.predict_proba(newArray)
    print(f"Predicted Probability of reaching growth milestone: {probabilities[0,1]}")

    result = {
        'probability': probabilities[0,1]
    }
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0',port=9001)