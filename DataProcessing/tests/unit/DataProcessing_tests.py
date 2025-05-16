import unittest
from unittest.mock import Mock
import sys
import os
import flask_sqlalchemy.extension
import pytest
from flask_sqlalchemy import SQLAlchemy
from mock_alchemy.mocking import UnifiedAlchemyMagicMock
# Add the DataProcessing/ directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from DataProcessing import DataProcessing
from DemoData import get_model_for_table, create_plant_model, create_preprocessed_plant_model, create_sensor_data_model
import json

class TestDataProcessing():

    @pytest.fixture()
    def app(self):
        app = DataProcessing.app
        app.config.update({
            "TESTING": True,
        })
        yield app

    @pytest.fixture()
    def client(app):
        return DataProcessing.app.test_client()

    @pytest.fixture()
    def runner(app):
        return DataProcessing.app.test_cli_runner()

    def test_DataProcessing_fetch_sensor_data(self, client, monkeypatch, app, mocker):
        data = \
            [ \
                { \
                    'air_humidity': 65.4,
                    'air_temperature': 22.5,
                    'artificial_light': True,
                    'distance_to_height': 5.5,
                    'experiment_number': 1,
                    'fertilizer_type': 'NPK',
                    'id': 1,
                    'light': 120.5,
                    'light_avg': 150.0,
                    'light_max': 200.0,
                    'light_min': 80.0,
                    'light_type': 'LED',
                    'light_variation': 120.0,
                    'soil_moisture': 45.2,
                    'soil_type': 'Loamy',
                    'time_since_last_watering': 12.0,
                    'timestamp': '2025-04-10T10:30:00Z',
                    'water': 2.0,
                    'water_amount': 1.0,
                    'water_need_score': 27.4,
                    'watering_frequency': 10.0
                } \
            ]
        data = DataProcessing.SensorData(air_humidity=65.4,air_temperature=22.5,artificial_light=True,distance_to_height=5.5,experiment_number=1,fertilizer_type='NPK',id=1,light=120.5,light_avg=150.0,light_max=200.0,light_min=80.0,light_type='LED',light_variation=120.0,soil_moisture=45.2,soil_type='Loamy',time_since_last_watering=12.0,timestamp='2025-04-10T10:30:00Z',water=2.0,water_amount=1.0,water_need_score=27.4,watering_frequency=10.0)
        datajson = "[{'air_humidity': 65.4, 'air_temperature': 22.5, 'artificial_light': True, 'distance_to_height': 5.5, 'experiment_number': 1, 'fertilizer_type': 'NPK', 'id': 1, 'light': 120.5, 'light_avg': 150.0, 'light_max': 200.0, 'light_min': 80.0, 'light_type': 'LED', 'light_variation': 120.0, 'soil_moisture': 45.2, 'soil_type': 'Loamy', 'time_since_last_watering': 12.0, 'timestamp': '2025-04-10T10:30:00Z', 'water': 2.0, 'water_amount': 1.0, 'water_need_score': 27.4, 'watering_frequency': 10.0}]"
        session = UnifiedAlchemyMagicMock(data = [
            ([mock.call.query(),
             mock.call.filter(),
              mock.call.all()],
            data),
        ])
        session.query.return_value.all.return_value = [data]
        session.query.call.all().return_value = [data]
        session.query.all.call.return_value = [data]

        #monkeypatch.setattr(flask_sqlalchemy.extension, 'Session', session)
        with app.app_context():
            #monkeypatch.setattr(DataProcessing.SensorData, 'query', session)
            u = UnifiedAlchemyMagicMock(data = [
                ([mock.call.query(DataProcessing.SensorData),
                 mock.call.filter(),
                  mock.call.all(),
                  mock.call.query(DataProcessing.SensorData).all()],
                [data]),
            ])
            #monkeypatch.setattr(DataProcessing, 'SensorData', u)
            #monkeypatch.setattr(DataProcessing.SensorData, 'query')
            #monkeypatch.setattr(DataProcessing.SensorData.query.all, Mock([data]))
            mocker.patch('flask_sqlalchemy.query.Query.all', return_value=[data])
            #dp = DataProcessing.fetch_sensor_data()
            dp = client.get('/fetch-sensor-data')
            assert str(dp.json) == datajson

    def test_DataProcessing_post_sensor_data(self, client, monkeypatch, app, mocker):
        data = \
            [ \
                { \
                    'air_humidity': 65.4,
                    'air_temperature': 22.5,
                    'artificial_light': True,
                    'distance_to_height': 5.5,
                    'experiment_number': 1,
                    'fertilizer_type': 'NPK',
                    'id': 1,
                    'light': 120.5,
                    'light_avg': 150.0,
                    'light_max': 200.0,
                    'light_min': 80.0,
                    'light_type': 'LED',
                    'light_variation': 120.0,
                    'soil_moisture': 45.2,
                    'soil_type': 'Loamy',
                    'time_since_last_watering': 12.0,
                    'timestamp': '2025-04-10T10:30:00Z',
                    'water': 2.0,
                    'water_amount': 1.0,
                    'water_need_score': 27.4,
                    'watering_frequency': 10.0
                } \
                ]
        with app.app_context():
            dbMock = UnifiedAlchemyMagicMock()
            monkeypatch.setattr(DataProcessing, 'db', dbMock)
            dp = client.post('/fetch-sensor-data', json=data)
            assert dbMock.session.add.call_count == 1
            assert dbMock.session.commit.call_count == 1
            dataset = dbMock.session.query(DataProcessing.SensorData).all()
            assert dataset.__len__() == 1
            assert dataset[0].air_humidity == 65.4