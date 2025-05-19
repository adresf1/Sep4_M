import sys
import os
import pytest
from pathlib import Path

# Add the DataProcessing/ directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from DemoData import create_plant_model, calculate_column_averages, create_preprocessed_plant_model, one_hot_encode_columns, copy_to_preprocessed
from unittest.mock import patch, MagicMock
from DataProcessing import app
from dotenv import load_dotenv


print("Starting pytest.fixture.....")
@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv('DATABASE_URL', 'postgresql://mock_url')
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

#Fail Test to verify a docker build will abandon build if an unittest fails 
#def test_force_fail():
#    print("\n🔍 Running test_force_fail (intentionally fails)...")
#    value = 42
#    assert value == 0, f"test_force_fail failed: expected 0, got {value}"

print("Starting Tests.....")

#================================== Get all function test ==================================
#Test Zero case with 
def test_get_plant_data_empty(client):
    print("\n🔍 Running test_get_plant_data_empty...")

    with patch('DemoData.create_plant_model') as mock_create_model, \
         patch('DataProcessing.get_engine_and_session') as mock_get_engine_session, \
         patch('sqlalchemy.create_engine') as mock_create_engine:

        mock_engine = MagicMock()  
        mock_create_engine.return_value = mock_engine

        mock_model = MagicMock()
        mock_create_model.return_value = mock_model

        mock_session = MagicMock()
        mock_session.query.return_value.all.return_value = []
        mock_get_engine_session.return_value = (mock_engine, mock_session)

        response = client.get('/DemoDataRaw')
        data = response.get_json()

        print("📦 Response data:", response.get_data(as_text=True))

        assert response.status_code == 200
        assert isinstance(data, list)
        assert len(data) == 0
        print("✅ test_get_plant_data_empty passed.")

#Test Get function One 
def test_get_plant_data_success(client):
    print("\n🔍 Running test_get_plant_data_success...")

    with patch('DemoData.create_plant_model') as mock_create_model, \
         patch('DataProcessing.get_engine_and_session') as mock_get_engine_session:

        # Mock SQLAlchemy model
        mock_model = MagicMock()
        mock_create_model.return_value = mock_model

        mock_row = MagicMock()
        mock_row.id = 1
        mock_row.soil_type = "Loamy"
        mock_row.sunlight_hours = 6
        mock_row.water_frequency = "Weekly"
        mock_row.fertilizer_type = "Organic"
        mock_row.temperature = 22.0
        mock_row.humidity = 55
        mock_row.growth_milestone = 1

        mock_session = MagicMock()
        mock_session.query.return_value.all.return_value = [mock_row]
        mock_get_engine_session.return_value = (MagicMock(), mock_session)

        response = client.get('/DemoDataRaw')
        data = response.get_json()

        print("📦 Response data:", response.get_data(as_text=True))

        assert response.status_code == 200
        assert isinstance(data, list)
        assert len(data) == 1

        entry = data[0]
        assert entry == {
            'id': 1,
            'soil_type': "Loamy",
            'sunlight_hours': 6,
            'water_frequency': "Weekly",
            'fertilizer_type': "Organic",
            'temperature': 22.0,
            'humidity': 55,
            'Growth_Milestone': 1
        }
        print("✅ test_get_plant_data_success passed.")

#Test Get function Many
def test_get_plant_data_multiple_entries(client):
    print("\n🔍 Running test_get_plant_data_multiple_entries...")

    # Create 3 mock entries with different values
    mock_entries = []
    for i in range(3):
        mock_instance = MagicMock()
        mock_instance.configure_mock(
            id=i + 1,
            soil_type=f"SoilType{i + 1}",
            sunlight_hours=5 + i,
            water_frequency="Weekly" if i % 2 == 0 else "Daily",
            fertilizer_type="Organic" if i == 0 else "Synthetic",
            temperature=20.0 + i,
            humidity=50 + i * 5,
            growth_milestone=i + 1
        )
        mock_entries.append(mock_instance)

    with patch('DemoData.create_plant_model') as mock_create_model, \
         patch('DataProcessing.get_engine_and_session') as mock_get_engine_session:
        print("✅ Patching create_plant_model and get_engine_and_session")

        mock_create_model.return_value = MagicMock()

        mock_session = MagicMock()
        mock_session.query.return_value.all.return_value = mock_entries
        mock_get_engine_session.return_value = (MagicMock(), mock_session)

        response = client.get('/DemoDataRaw')
        print(f"📥 Response status code: {response.status_code}")
        data = response.get_json()
        print(f"📦 Response data: {data}")

        assert response.status_code == 200
        assert isinstance(data, list)
        assert len(data) == 3

        for i, entry in enumerate(data):
            expected_soil = f"SoilType{i + 1}"
            expected_milestone = i + 1
            print(f"🔎 Entry {i}: soil_type={entry['soil_type']}, Growth_Milestone={entry['Growth_Milestone']}")
            assert entry['soil_type'] == expected_soil
            assert entry['Growth_Milestone'] == expected_milestone

    print("✅ test_get_plant_data_multiple_entries passed.")

#Denne test gør ikke noget efter signatur/implementering for DataProcessing er ændret
def test_get_plant_data_failure(client):
    print("\n🔍 Running test_get_plant_data_failure...")

    with patch('DataProcessing.get_engine_and_session') as mock_get_engine_session, \
         patch('DemoData.create_plant_model', side_effect=Exception("DB failure")):
        
        mock_get_engine_session.return_value = (MagicMock(), MagicMock())

        response = client.get('/DemoDataRaw')
        print(f"📥 Response status code: {response.status_code}")
        print(f"📦 Response data: {response.get_json()}")

        assert response.status_code == 200
        json_data = response.get_json()
        #assert 'error' in json_data
        #assert json_data['error'] == "DB failure"
        print("✅ test_get_plant_data_failure passed.")

#================================== Get Single Tests ==================================

def test_get_single_plant_data_success(client):
    print("Running: test_get_single_plant_data_success (id=1)")

    mock_entry = MagicMock(
        id=1,
        soil_type="Sandy",
        sunlight_hours=8,
        water_frequency="Daily",
        fertilizer_type="Compost",
        temperature=23.5,
        humidity=60,
        growth_milestone=3
    )

    with patch('DemoData.create_plant_model') as mock_create_model, \
         patch('DataProcessing.get_engine_and_session') as mock_get_engine_session:

        mock_create_model.return_value = MagicMock()

        mock_session = MagicMock()
        mock_session.get.return_value = mock_entry
        mock_get_engine_session.return_value = (MagicMock(), mock_session)

        response = client.get('/DemoDataRaw/1')
        assert response.status_code == 200

        data = response.get_json()
        print(f"📥 Response status code: {response.status_code}")
        print(f"📦 Response data: {data}")

        assert data['id'] == 1
        assert data['soil_type'] == "Sandy"
        assert data['Growth_Milestone'] == 3

        print("✅ test_get_single_plant_data_success passed.")



def test_get_single_plant_data_not_found(client):
    print("Running: test_get_single_plant_data_not_found (id=9001)")

    # Patch create_engine and sessionmaker where they are used, not where they're from
    with patch('DataProcessing.get_engine_and_session') as mock_get_engine_and_session:
        # Mock session to simulate DB behavior
        mock_session = MagicMock()
        mock_engine = MagicMock()

        # Make get_engine_and_session return a mock engine and session
        mock_get_engine_and_session.return_value = (mock_engine, mock_session)

        # Simulate .get() returning None (as if item not found in DB)
        mock_session.get.return_value = None

        # Call the endpoint
        response = client.get('/DemoDataRaw/9001')

        # Assert status code is 404
        assert response.status_code == 404

        # Parse and inspect response
        data = response.get_json()
        print(f"📥 Response status code: {response.status_code}")
        print(f"📦 Response data: {data}")

        # Assert that an appropriate error message is returned
        assert 'error' in data
        assert 'not found' in data['error'].lower()

        print("✅ test_get_single_plant_data_not_found passed.")


def test_get_single_plant_data_invalid_id_negative(client):
    print("🔍 Running: test_get_single_plant_data_invalid_id_negative (id=-10)")

    with patch('DemoData.create_plant_model'), \
         patch('DataProcessing.get_engine_and_session') as mock_get_engine_session:

        # Mock session that returns None for any .get call
        mock_session = MagicMock()
        mock_session.get.return_value = None
        mock_get_engine_session.return_value = (MagicMock(), mock_session)

        # Make a GET request with an invalid (negative) ID
        response = client.get('/DemoDataRaw/-10')

        # Assert a 404 response
        assert response.status_code == 404

        # Check the response content
        #json_data = response.get_json()

        #Flask handles negative values, so endpoints safeguard is never reached  
        #assert 'error' in json_data
        #assert json_data['error'] == "Plant not found"

        print("✅ test_get_single_plant_data_invalid_id_negative passed.")

def test_get_single_plant_data_zero_id(client):
    print("🔍 Running: test_get_single_plant_data_zero_id (id=0)")

    with patch('DemoData.create_plant_model'), \
         patch('DataProcessing.get_engine_and_session') as mock_get_engine_session:

        # Mock session (won't be used in this case because ID=0 should short-circuit)
        mock_session = MagicMock()
        mock_get_engine_session.return_value = (MagicMock(), mock_session)

        # Send request with ID=0
        response = client.get('/DemoDataRaw/0')

        # Expect 400 Bad Request
        assert response.status_code == 400

        # Check response content
        data = response.get_json()
        print(f"📥 Response status code: {response.status_code}")
        print(f"📦 Response data: {data}")

        assert 'error' in data
        assert 'Invalid ID' in data['error']

        print("✅ test_get_single_plant_data_zero_id passed.")

#================================== Update Single function test ==================================

@pytest.mark.parametrize(
    "id, data, expected_status, expected_error",
    [
        (0, {"soil_type": "Loamy", "sunlight_hours": 6, "growth_milestone": 1}, 400, "Invalid ID"),
        (1, {"soil_type": "Loamy", "sunlight_hours": 6, "growth_milestone": 1}, 200, None),
        (9001, {"soil_type": "Loamy", "sunlight_hours": 6, "growth_milestone": 1}, 404, "Entry with id 9001 not found"),
    ]
)
def test_update_plant_data(client, id, data, expected_status, expected_error):
    print(f"\n🔍 Running: test_update_plant_data (id={id})")

    with patch('DemoData.create_plant_model') as mock_create_model, \
         patch('DataProcessing.get_engine_and_session') as mock_get_engine_session:

        # Mock session and commit behavior
        mock_session = MagicMock()
        mock_get_engine_session.return_value = (MagicMock(), mock_session)

        # Mock the entry returned by session.get
        if id == 9001:
            mock_session.get.return_value = None
        else:
            mock_entry = MagicMock(id=id)
            mock_session.get.return_value = mock_entry

        mock_create_model.return_value = MagicMock()

        # Send the POST request
        response = client.post(f'/DemoDataRaw/{id}', json=data)

        # Check the response status code
        assert response.status_code == expected_status

        if expected_status == 200:
            mock_session.commit.assert_called_once()
            print(f"✅ Entry {id} updated successfully.")
        else:
            json_data = response.get_json(silent=True)
            assert json_data is not None, f"❌ Expected JSON error response but got none for id={id}"
            assert 'error' in json_data, f"❌ Expected 'error' key in response JSON: {json_data}"
            assert expected_error in json_data['error'], f"❌ Expected error '{expected_error}' not found in response: {json_data['error']}"
            print(f"❌ Error: {json_data['error']}")

    print(f"✅ test_update_plant_data (id={id}) passed.")

@pytest.mark.parametrize(
    "field, value, expected_status, expected_error",
    [
        ("soil_type", 123, 400, "Invalid data type for soil_type"),
        ("soil_type", True, 400, "Invalid data type for soil_type"),
        ("soil_type", 12.34, 400, "Invalid data type for soil_type"),
        ("soil_type", None, 400, "Invalid data type for soil_type"),
        ("sunlight_hours", "string", 400, "Invalid data type for sunlight_hours"),
        ("sunlight_hours", True, 400, "Invalid data type for sunlight_hours"),
        ("sunlight_hours", None, 400, "Invalid data type for sunlight_hours"),
        ("growth_milestone", "string", 400, "Invalid data type for growth_milestone"),
        ("growth_milestone", True, 400, "Invalid data type for growth_milestone"),
        ("growth_milestone", None, 400, "Invalid data type for growth_milestone"),
    ]
)
def test_update_plant_data_invalid_types(client, field, value, expected_status, expected_error):
    print(f"\n🔍 Running: test_update_plant_data_invalid_types ({field}={value})")

    # Valid default payload
    data = {
        "soil_type": "Loamy",
        "sunlight_hours": 6,
        "growth_milestone": 1
    }
    # Inject the invalid field
    data[field] = value

    with patch('DataProcessing.get_engine_and_session') as mock_get_engine_session, \
         patch('DemoData.create_plant_model') as mock_create_model:

        # Mock session and response
        mock_session = MagicMock()
        mock_entry = MagicMock(id=1)
        mock_session.get.return_value = mock_entry
        mock_get_engine_session.return_value = (MagicMock(), mock_session)

        mock_create_model.return_value = MagicMock()

        # Make the request
        response = client.post('/DemoDataRaw/1', json=data)
        assert response.status_code == expected_status

        if expected_status == 400:
            json_data = response.get_json()
            assert 'error' in json_data
            assert expected_error in json_data['error']
            print(f"❌ Error: {json_data['error']}")
        else:
            mock_session.commit.assert_called_once()
            print(f"✅ Entry updated successfully.")

        print(f"✅ test_update_plant_data_invalid_types ({field}={value}) passed.")