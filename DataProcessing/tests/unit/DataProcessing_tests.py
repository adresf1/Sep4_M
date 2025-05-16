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

from DataProcessing import app
from DemoData import get_model_for_table, create_plant_model, create_preprocessed_plant_model, create_sensor_data_model
import json

os.environ['DATABASE_URL'] = 'postgresql://dummy_url'

@pytest.fixture
def client():
    app.config['TESTING'] = True
    return app.test_client()

@pytest.fixture
def runner():
    return app.test_cli_runner()

def test_with_session_mock(monkeypatch):
    mock_session = UnifiedAlchemyMagicMock()
    
    def mock_get_engine_and_session(url):
        assert url == os.getenv("DATABASE_URL", "sqlite:///:memory:")
        return None, mock_session

    monkeypatch.setattr('DataProcessing.get_engine_and_session', mock_get_engine_and_session)

class TestDataProcessing:

    def test_fetch_sensor_data(self, client, monkeypatch):
        # Arrange
        SensorData = create_sensor_data_model()
    
        mock_row = SensorData(
            id=1,
            air_temperature=25.0,
            air_humidity=50.0,
            soil_moisture=40.0,
            light=200.0,
            light_type='LED',
            light_max=300.0,
            light_min=100.0,
            artificial_light=True,
            light_avg=200.0,
            distance_to_height=5.0,
            water=2.5,
            time_since_last_watering=24.0,
            water_amount=1.5,
            watering_frequency=12.0,
            timestamp='2025-05-10T12:00:00Z',
            soil_type='Loamy',
            fertilizer_type='Organic',
            experiment_number=3,
            light_variation=100.0,
            water_need_score=75.0
        )

        expected_json = [{
            'id': 1,
            'air_temperature': 25.0,
            'air_humidity': 50.0,
            'soil_moisture': 40.0,
            'light': 200.0,
            'light_type': 'LED',
            'light_max': 300.0,
            'light_min': 100.0,
            'artificial_light': True,
            'light_avg': 200.0,
            'distance_to_height': 5.0,
            'water': 2.5,
            'time_since_last_watering': 24.0,
            'water_amount': 1.5,
            'watering_frequency': 12.0,
            'timestamp': '2025-05-10T12:00:00Z',
            'soil_type': 'Loamy',
            'fertilizer_type': 'Organic',
            'experiment_number': 3,
            'light_variation': 100.0,
            'water_need_score': 75.0
        }]

        mock_session = UnifiedAlchemyMagicMock()
        mock_session.query.return_value.all.return_value = [mock_row]

        def mock_get_engine_and_session(url):
            assert url == os.getenv("DATABASE_URL", "sqlite:///:memory:")
            return None, mock_session

        monkeypatch.setattr('DataProcessing.get_engine_and_session', mock_get_engine_and_session)

        with app.app_context():
            response = client.get('/fetch-sensor-data')
            if response.status_code != 200:
                print("Error response data:", response.get_data(as_text=True))
            assert response.status_code == 200

    def test_post_sensor_data(self, client, monkeypatch):
        # Sample input data for the POST request (sensor data)
        sensor_data_payload = [{
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
        }]

        mock_session = UnifiedAlchemyMagicMock()

        def mock_get_engine_and_session(url):
            assert url == os.getenv("DATABASE_URL", "sqlite:///:memory:")
            return None, mock_session

        monkeypatch.setattr('DataProcessing.get_engine_and_session', mock_get_engine_and_session)

        with app.app_context():
            response = client.post('/fetch-sensor-data', json=sensor_data_payload)

        assert response.status_code in [200, 201]
        if response.status_code not in [200, 201]:
            print("Error response data:", response.get_data(as_text=True))
        assert mock_session.add.call_count == 1
        assert mock_session.commit.call_count == 1