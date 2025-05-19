from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
import pytest
from bs4 import BeautifulSoup
import json
from seleniumrequests import Firefox as srFirefox
import os
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base


class TestAPII:
    endpoint = "http://localhost:5019/api/Sensor";  # "http://Sep4-API-Service:8080/api/Sensor";
    options = FirefoxOptions()
    options.add_argument("--headless")
    options.set_preference('devtools.jsonview.enabled', False)

    def test_setup(self):
        DATABASE_URL = os.getenv('DATABASE_URL_TEST')
        # Defining the Engine
        engine = sqlalchemy.create_engine(os.getenv('DATABASE_URL_TEST'), echo=False)

        # Create the Metadata Object
        metadata_obj = sqlalchemy.MetaData()

        # Database
        PlantData = sqlalchemy.Table('sensor_data', metadata_obj,
            sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True, autoincrement=True),
            sqlalchemy.Column('experiment_number', sqlalchemy.Integer),
            sqlalchemy.Column('soil_type', sqlalchemy.String),
            sqlalchemy.Column('sunlight_hours', sqlalchemy.Float),
            sqlalchemy.Column('light', sqlalchemy.Float),
            sqlalchemy.Column('light_type', sqlalchemy.String),
            sqlalchemy.Column('light_max', sqlalchemy.Float),
            sqlalchemy.Column('light_min', sqlalchemy.Float),
            sqlalchemy.Column('light_avg', sqlalchemy.Float),
            sqlalchemy.Column('light_variation', sqlalchemy.Float),
            sqlalchemy.Column('artificial_light', sqlalchemy.Boolean),
            sqlalchemy.Column('watering_frequency', sqlalchemy.Float),
            sqlalchemy.Column('time_since_last_watering', sqlalchemy.Float),
            sqlalchemy.Column('water_amount', sqlalchemy.Float),
            sqlalchemy.Column('water', sqlalchemy.Float),
            sqlalchemy.Column('water_need_score', sqlalchemy.Float),
            sqlalchemy.Column('fertilizer_type', sqlalchemy.String),
            sqlalchemy.Column('air_temperature', sqlalchemy.Float),
            sqlalchemy.Column('air_humidity', sqlalchemy.Float),
            sqlalchemy.Column('soil_moisture', sqlalchemy.Float),
            sqlalchemy.Column('distance_to_height', sqlalchemy.Float),
            sqlalchemy.Column('timestamp', sqlalchemy.String),
            sqlalchemy.Column('growth_milestone', sqlalchemy.Integer),
        )
        # Create session
        session = sqlalchemy.orm.Session(engine)

        # Create inspector
        inspector = sqlalchemy.inspect(engine)
        if inspector.has_table('sensor_data'):
            PlantData.drop(engine)
            session.commit()
        PlantData.create(engine)
        session.commit()
        session.close()
        engine.dispose()


    def test_PostSensor(self):
        payload = '{"experimentNumber": 1,"airTemperature": 22.5,"airHumidity": 65.4,"soilMoisture": 45.2,"light": 120.5,"lightType": "LED","lightMax": 200,"lightMin": 80,"artificialLight": true,"lightAvg": 150,"distanceToHeight": 5.5,"water": 2,"timeSinceLastWatering": 12,"waterAmount": 1,"wateringFrequency": 10,"timestamp": "2025-04-10T10:30:00Z","soilType": "Loamy","fertilizerType": "NPK"}'

        driver = srFirefox(options=self.options, service=FirefoxService(executable_path=GeckoDriverManager().install()))
        headers = {'Content-type': 'application/json'}
        res = driver.request('POST', self.endpoint, headers=headers, data=payload)
        assert res.status_code == 200
        assert res.text == 'Sensor data sent successfully.'

    def test_GetSensors(self):
        expectedresult = '[{"experimentNumber":1,"airTemperature":22.5,"airHumidity":65.4,"soilMoisture":45.2,"light":120.5,"lightType":"LED","lightMax":200,"lightMin":80,"artificialLight":true,"lightAvg":150,"distanceToHeight":5.5,"water":2,"timeSinceLastWatering":12,"waterAmount":1,"wateringFrequency":10,"timestamp":"2025-04-10T10:30:00Z","soilType":"Loamy","fertilizerType":"NPK","lightVariation":120,"waterNeedScore":27.4}]'

        driver = webdriver.Firefox(options=self.options, service=FirefoxService(executable_path=GeckoDriverManager().install()))

        driver.get(self.endpoint)

        result = driver.find_element(By.TAG_NAME, 'body').text

        assert expectedresult == result

    def test_GetModels(self):
        expectedresult = '[{"TypeOfModel":"rfc","NameOfModel":"RandomForestRegressor.joblib"}]'

        driver = webdriver.Firefox(options=self.options, service=FirefoxService(executable_path=GeckoDriverManager().install()))

        driver.get(self.endpoint + '/model')

        result = driver.find_element(By.TAG_NAME, 'body').text

        assert expectedresult == result


    def test_PredictUnified(self):
        payload = '{"TypeofModel": "rfc","NameOfModel": "RandomForestRegressor.joblib","Data": {"soil_type": 1,"sunlight_hours": 6,"water_frequency": 3,"fertilizer_type": 1,"temperature": 22,"humidity": 60}}'
        expectedresult = '{\n  "message": "Random Forest prediction completed successfully.",\n  "model_used": "RandomForestRegressor.joblib",\n  "result": [\n    0.5952380952380952,\n    0.40476190476190477\n  ],\n  "status": "success"\n}\n'
        driver = srFirefox(options=self.options, service=FirefoxService(executable_path=GeckoDriverManager().install()))
        headers = {'Content-type': 'application/json'}
        res = driver.request('POST', self.endpoint + '/predict', headers=headers, data=payload)

        assert res.status_code == 200
        assert res.text == expectedresult

    def test_GetTables(self):
        expectedresult = '["sensor_data"]'

        driver = webdriver.Firefox(options=self.options, service=FirefoxService(executable_path=GeckoDriverManager().install()))

        driver.get(self.endpoint + '/get-tables')

        result = driver.find_element(By.TAG_NAME, 'body').text

        assert expectedresult == result

    def test_APII_DBSessionLeak(self):
        payload = '{"TypeofModel": "rfc","NameOfModel": "RandomForestRegressor.joblib","Data": {"soil_type": 1,"sunlight_hours": 6,"water_frequency": 3,"fertilizer_type": 1,"temperature": 22,"humidity": 60}}'
        driver = srFirefox(options=self.options, service=FirefoxService(executable_path=GeckoDriverManager().install()))
        headers = {'Content-type': 'application/json'}
        for x in range(20):
            res = driver.request('POST', self.endpoint + '/predict', headers=headers, data=payload)
            assert res.status_code == 200



class TestMLService:
    endpoint = "http://localhost:5249/api";  # "http://Sep4-ML-Service:8080/api";
    options = FirefoxOptions()
    options.add_argument("--headless")
    options.set_preference('devtools.jsonview.enabled', False)

    def test_Train(self):
        payload = '{"model_name": "E2E_test_RFC_model","table_name": "plant_data_test","target_measure": "growth_milestone","model_type": "random_forest","testSize": 0.2,"randomState": 42,"estimators": 100,"max_depth": 10}'

        driver = srFirefox(options=self.options, service=FirefoxService(executable_path=GeckoDriverManager().install()))
        headers = {'Content-type': 'application/json'}
        res = driver.request('POST', self.endpoint + '/Training', headers=headers, data=payload)
        assert res.status_code == 200
        assert res.text.__contains__('success')

    def test_GetModels(self):
        expectedresult = '[{"TypeOfModel":"rfc","NameOfModel":"RandomForestRegressor.joblib"}]'

        driver = webdriver.Firefox(options=self.options,
                                   service=FirefoxService(executable_path=GeckoDriverManager().install()))

        driver.get(self.endpoint + '/Prediction')

        result = driver.find_element(By.TAG_NAME, 'body').text

        assert expectedresult == result

    def test_Predict(self):
        payload = '{"TypeofModel": "rfc","NameOfModel": "RandomForestRegressor.joblib","Data": {"soil_type": 1,"sunlight_hours": 6,"water_frequency": 3,"fertilizer_type": 1,"temperature": 22,"humidity": 60}}'
        expectedresult = '{\n  "message": "Random Forest prediction completed successfully.",\n  "model_used": "RandomForestRegressor.joblib",\n  "result": [\n    0.5952380952380952,\n    0.40476190476190477\n  ],\n  "status": "success"\n}\n'
        driver = srFirefox(options=self.options, service=FirefoxService(executable_path=GeckoDriverManager().install()))
        headers = {'Content-type': 'application/json'}
        res = driver.request('POST', self.endpoint + '/Prediction/predict', headers=headers, data=payload)
        assert res.status_code == 200
        assert res.text == expectedresult

    def test_MLService_DBSessionLeak(self):
        payload = '{"TypeofModel": "rfc","NameOfModel": "RandomForestRegressor.joblib","Data": {"soil_type": 1,"sunlight_hours": 6,"water_frequency": 3,"fertilizer_type": 1,"temperature": 22,"humidity": 60}}'
        driver = srFirefox(options=self.options, service=FirefoxService(executable_path=GeckoDriverManager().install()))
        headers = {'Content-type': 'application/json'}
        for x in range(20):
            res = driver.request('POST', self.endpoint + '/Prediction/predict', headers=headers, data=payload)
            assert res.status_code == 200
