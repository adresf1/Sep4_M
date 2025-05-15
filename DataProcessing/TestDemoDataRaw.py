import pytest
from unittest.mock import patch, MagicMock
from DataProcessing import app

print("Starting pytest.fixture.....")
@pytest.fixture
def client():
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

    with patch('DataProcessing.create_plant_model') as mock_create_model, \
         patch('DataProcessing.get_engine_and_session') as mock_get_engine_session:

        # Mock SQLAlchemy model
        MockPlantModel = MagicMock()
        mock_create_model.return_value = MockPlantModel

        # Mock session and query
        mock_session = MagicMock()
        mock_session.query.return_value.all.return_value = []

        # Return mocked engine and session
        mock_get_engine_session.return_value = (MagicMock(), mock_session)

        # Call endpoint
        response = client.get('/DemoDataRaw')

        # Assertions
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) == 0
        print("✅ test_get_plant_data_empty passed.")

#Test Get function One 
def test_get_plant_data_success(client):
    print("\n🔍 Running test_get_plant_data_success...")

    mock_model_instance = MagicMock()
    mock_model_instance.configure_mock(
        id=1,
        soil_type="Loamy",
        sunlight_hours=6,
        water_frequency="Weekly",
        fertilizer_type="Organic",
        temperature=22.0,
        humidity=55,
        growth_milestone=1      
    )

    with patch('DataProcessing.create_plant_model') as mock_create_model, \
         patch('DataProcessing.db.session.query') as mock_query:
        print("✅ Patching create_plant_model and db.session.query")
        mock_create_model.return_value = MagicMock()
        mock_query.return_value.all.return_value = [mock_model_instance]

        response = client.get('/DemoDataRaw')
        print(f"📥 Response status code: {response.status_code}")
        print(f"📦 Response data: {response.get_json()}")

        assert response.status_code == 200
        data = response.get_json()

        assert isinstance(data, list)
        assert data[0]['soil_type'] == "Loamy"
        assert data[0]['Growth_Milestone'] == 1
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

    with patch('DataProcessing.create_plant_model') as mock_create_model, \
         patch('DataProcessing.db.session.query') as mock_query:
        print("✅ Patching create_plant_model and db.session.query")
        mock_create_model.return_value = MagicMock()
        mock_query.return_value.all.return_value = mock_entries

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

def test_get_plant_data_failure(client):
    print("\n🔍 Running test_get_plant_data_failure...")

    with patch('DataProcessing.create_plant_model', side_effect=Exception("DB failure")):
        response = client.get('/DemoDataRaw')
        print(f"📥 Response status code: {response.status_code}")
        print(f"📦 Response data: {response.get_json()}")

        assert response.status_code == 500
        json_data = response.get_json()
        assert 'error' in json_data
        assert json_data['error'] == "DB failure"
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

    with patch('DataProcessing.create_plant_model') as mock_create_model, \
         patch('DataProcessing.db.session.get') as mock_db_get:
        mock_create_model.return_value = MagicMock()
        mock_db_get.return_value = mock_entry

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
    with patch('DataProcessing.create_plant_model'), \
         patch('DataProcessing.db.session.get', return_value=None):
        response = client.get('/DemoDataRaw/9001')
        assert response.status_code == 404
        data = response.get_json()
        print(f"📥 Response status code: {response.status_code}")
        print(f"📦 Response data: {data}")
        assert 'error' in data
        assert 'not found' in data['error']
        print("✅ test_get_single_plant_data_not_found passed.")


def test_get_single_plant_data_invalid_id_negative(client):
    print("Running: test_get_single_plant_data_invalid_id_negative (id=-10)")
    with patch('DataProcessing.create_plant_model'), \
         patch('DataProcessing.db.session.get', side_effect=Exception("Invalid ID")):
        response = client.get('/DemoDataRaw/-10')
        assert response.status_code == 404
        print("✅ test_get_single_plant_data_invalid_id_negative passed.")

def test_get_single_plant_data_zero_id(client):
    print("Running: test_get_single_plant_data_zero_id (id=0)")
    with patch('DataProcessing.create_plant_model'), \
         patch('DataProcessing.db.session.get', return_value=None):
        response = client.get('/DemoDataRaw/0')
        assert response.status_code == 400
        data = response.get_json()
        print(f"📥 Response status code: {response.status_code}")
        print(f"📦 Response data: {data}")
        assert 'error' in data  # Ensures 'error' key is present
        assert 'Invalid ID' in data['error']  # Make sure 'Invalid ID' is part of the error message
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

    with patch('DataProcessing.create_plant_model') as mock_create_model, \
         patch('DataProcessing.db.session.get') as mock_db_get, \
         patch('DataProcessing.db.session.commit') as mock_commit:

        mock_create_model.return_value = MagicMock()
        mock_entry = MagicMock(id=id)
        mock_db_get.return_value = mock_entry if id != 9001 else None

        # Send the POST request
        response = client.post(f'/DemoDataRaw/{id}', json=data)

        # Check the response status code
        assert response.status_code == expected_status

        if expected_status == 200:
            mock_commit.assert_called_once()
            print(f"✅ Entry {id} updated successfully.")
        else:
            # Handle case when no JSON is returned
            try:
                json_data = response.get_json(force=True, silent=True)
            except Exception:
                json_data = None

            assert json_data is not None, f"❌ Expected JSON error response but got none for id={id}"
            assert 'error' in json_data, f"❌ Expected 'error' key in response JSON: {json_data}"
            assert expected_error in json_data['error']
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

    data = {
        "soil_type": "Loamy",
        "sunlight_hours": 6,
        "growth_milestone": 1
    }
    data[field] = value

    with patch('DataProcessing.create_plant_model') as mock_create_model, \
         patch('DataProcessing.db.session.get') as mock_db_get, \
         patch('DataProcessing.db.session.commit') as mock_commit:

        mock_create_model.return_value = MagicMock()
        mock_entry = MagicMock(id=1)
        mock_db_get.return_value = mock_entry

        response = client.post('/DemoDataRaw/1', json=data)
        assert response.status_code == expected_status

        if expected_status == 400:
            data = response.get_json()
            assert 'error' in data
            assert expected_error in data['error']
            print(f"❌ Error: {data['error']}")
        else:
            mock_commit.assert_called_once()
            print(f"✅ Entry updated successfully.")

        print(f"✅ test_update_plant_data_invalid_types ({field}={value}) passed.")