import unittest
from unittest.mock import Mock

import flask_sqlalchemy.extension
import pytest
import mock
from flask_sqlalchemy import SQLAlchemy
from mock_alchemy.mocking import UnifiedAlchemyMagicMock
from DataProcessing import DataProcessing
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

    def test_DataProcessing_fetch_sensor_data(self, client, monkeypatch, app):
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
            monkeypatch.setattr(DataProcessing, 'SensorData', u)
            dp = DataProcessing.fetch_sensor_data()
            assert dp[0].json == json.dumps(data)