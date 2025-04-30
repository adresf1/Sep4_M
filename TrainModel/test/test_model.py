import pytest
import json
from ModelTrainingAPI import app  # adjust import based on your setup

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_predict_missing_fields(client):
    # Send an empty JSON payload with proper content-type
    response = client.post('/predict', json={})
    
    assert response.status_code == 400
    response_data = response.get_json()
    assert response_data is not None
    assert "error" in response_data
    assert "Missing required top-level keys" in response_data["error"]

def test_train_no_json(client):
    # Send an empty body with Content-Type: application/json
    response = client.post('/train', data="", content_type="application/json")
    
    # Assert that the status code is 415 (Unsupported Media Type) if no body is provided
    assert response.status_code == 415  # 415 because empty JSON content is unsupported

    # Check if the error message is returned in the response text
    response_data = response.get_data(as_text=True)
    assert "Unsupported Media Type" in response_data  # You can customize this depending on your actual response
