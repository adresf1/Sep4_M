import pytest
import json
import os
from unittest.mock import patch
from pathlib import Path
# Importér modulet under test
from ModelTrainingAPI import app, save_model_to_folder, get_model_for_table
from Predict import unpack_model, makePrediction, REQUIRED_FIELDS_RFC
# --- Dummy-klasser ----------------------------------------------------------

class DummyPlant:
    def __init__(self, data): self.data = data
    def to_dict(self):       return self.data

class DummyModel:
    def __init__(self, probas): self.probas = probas
    def predict_proba(self, X): return [[0.2,0.8]]
    def predict(self, X):       return [int(self.probas[1] > 0.5)]

# --- Flask-client-fixture ---------------------------------------------------

@pytest.fixture
def client(monkeypatch):
    app.config['TESTING'] = True

    # Stub create_plant_data_class to DummyPlant
    monkeypatch.setattr(
        'ModelTrainingAPI.create_plant_data_class',
        lambda table_name: DummyPlant,
        raising=False
    )


    # Stub sessionmaker to tom liste
    class FakeSession:
        def __init__(self, items): self._items = items
        def query(self, model):   return type('Q', (), {'all': lambda s: self._items})()
        def close(self):          pass

    monkeypatch.setattr(
        'ModelTrainingAPI.sessionmaker',
        lambda bind: FakeSession([DummyPlant({'a':1,'b':2})])
    )

    # Stub train_model til DummyModel + metrics
    monkeypatch.setattr(
        'ModelTrainingAPI.train_model',
        lambda targetMeasure, trainningData, testSize, estimatilrs, randomState:
            (DummyModel([0.1, 0.9]), {'accuracy': 0.9})
    )

    # Stub Predict-funktioner
    monkeypatch.setattr('Predict.unpack_model',    lambda name, folder: DummyModel([0.3, 0.7]))
    monkeypatch.setattr('Predict.makePrediction',  lambda model, data: [0.3, 0.7])

    # Stub joblib.load i logistic endpoint
    monkeypatch.setattr('ModelTrainingAPI.joblib.load', lambda path: DummyModel([0.4, 0.6]))

    with app.test_client() as c:
        yield c

# --- Utils-tests ------------------------------------------------------------

def test_save_model_to_folder_creates_file(tmp_path, monkeypatch):
    import ModelTrainingAPI
    # 1) Stub joblib.dump til kun at skrive en tom fil
    def fake_dump(obj, path):
        Path(path).write_bytes(b"")
    monkeypatch.setattr(ModelTrainingAPI.joblib, 'dump', fake_dump)

    # 2) Arrange
    model      = object()
    model_name = "foo_model"
    folder     = tmp_path / "models"

    # 3) Act
    filename   = save_model_to_folder(model, model_name, str(folder))
    saved_path = folder / filename

    # 4) Assert
    assert saved_path.exists()
    assert filename.startswith(model_name)
    assert filename.endswith(".joblib")

def test_unpack_model_loads_correct_file(tmp_path, monkeypatch):
    # 1) Opret TrainedModels folder + dummy-fil
    folder = tmp_path / "TrainedModels"
    folder.mkdir()
    dummy = folder / "bar.joblib"
    dummy.write_bytes(b"")

    # 2) Stub Predict.load — fang stien og returnér "OK"
    import Predict
    called = {}
    def fake_load(path):
        called['path'] = path
        return "OK"
    monkeypatch.setattr(Predict, 'load', fake_load)

    # 3) Kald unpack_model
    from Predict import unpack_model
    result = unpack_model("bar.joblib", str(folder))

    # 4) Assert
    assert result == "OK"
    assert called['path'].endswith("/TrainedModels/bar.joblib")

def test_get_model_for_table_caches(monkeypatch):
    import ModelTrainingAPI

    calls = []
    # Returnér en ny klasse per table_name
    def fake_create(name, engine):
        calls.append(name)
        return type(f"Plant_{name}", (), {})  # unik klasse for hver name

    monkeypatch.setattr(ModelTrainingAPI, 'create_plant_data_class', fake_create, raising=False)

    # Stub create_engine og sessionmaker så det ikke fejler
    monkeypatch.setattr(ModelTrainingAPI, 'create_engine', lambda url: object())
    monkeypatch.setattr(ModelTrainingAPI, 'sessionmaker', lambda *args, **kwargs: object())

    m1 = ModelTrainingAPI.get_model_for_table("A", "url")
    m2 = ModelTrainingAPI.get_model_for_table("A", "url")
    m3 = ModelTrainingAPI.get_model_for_table("B", "url")

    # Kald kun på første A og første B
    assert calls == ["A", "B"]
    assert m1 is m2
    assert m3 is not m1

# --- Endpoint-tests: /train -----------------------------------------------

# def test_train_no_json(client):
#     resp = client.post('/train', data='', content_type='application/json')
#     assert resp.status_code == 400

#     data = resp.get_json(force=True)
#     assert data is not None
#     assert data["error"] == "No JSON data provided"

@pytest.mark.parametrize('missing', ['model_name','table_name','target_measure'])
def test_train_missing_fields(client, missing):
    payload = {
        'model_name': 'm',
        'table_name': 't',
        'target_measure': 'y',
        'test_size': 0.2,
        'estimators': 100,
        'random_state': 42,
        'db_url': 'sqlite:///:memory:'
    }
    payload.pop(missing)
    resp = client.post('/train', json=payload)
    assert resp.status_code == 400
    assert "Missing required fields" in resp.get_json()["error"]

def test_train_no_data_found(client,monkeypatch):
    #Environment variable
    monkeypatch.setenv('DATABASE_URL', 'dummy://url')

    import ModelTrainingAPI

    #Stub get_model_for_table til at returnere en klasse uden data
    Dummy= type('Dummy', (), {})
    monkeypatch.setattr(ModelTrainingAPI, 'get_model_for_table', lambda table_name, url: Dummy, raising=True)

    #Dummy-session
    class EmptySession:
        def __init__(self,*args, **kwargs): pass
        def query(self,m):
            return type('Q', (), {'all': lambda self: []})()
        def close(self): pass
    
    #Stub create_engine og sessionmaker
    monkeypatch.setattr(ModelTrainingAPI, 'create_engine', lambda *args, **kwargs: object(), raising=True)
    monkeypatch.setattr(ModelTrainingAPI, 'sessionmaker', lambda *args, **kwargs: EmptySession, raising=True)

    #Kør POST på /train
    payload = {
        'model_name': 'm',
        'table_name': 't',
        'target_measure': 'y',
        'db_url': 'sqlite:///:memory:'
    }

    resp = client.post('/train', json=payload)

    #Assert at status er 404
    assert resp.status_code == 404
    data = resp.get_json()
    assert "No records found" in data["error"]


# --- Predict-tests ------------------------------------------------------------

# def test_predict_random_forest_success(client):
#     payload = {
#         "TypeofModel": "rfc",
#         "NameOfModel": "MyRFCModel_V6_random_forest.joblib",
#         "Data": {
#             "soil_type": 1,
#             "sunlight_hours": 6,
#             "water_frequency": 3,
#             "fertilizer_type": 1,
#             "temperature": 22,
#             "humidity": 60
#         }
#     }

#     response = client.post(
#         '/predict',
#         data=json.dumps(payload),
#         content_type='application/json'
#     )

#     assert response.status_code == 200
#     json_data = response.get_json()
#     assert json_data["status"] == "success"
#     assert "result" in json_data or "prediction" in json_data

# def test_predict_logistic_success(client):
#     payload = {
#         "TypeofModel": "logistic",
#         "NameOfModel": "MyLRModel_v6_logistic_regression.joblib",  
#         "Data": {
#             "soil_type": "Loamy",
#             "water_frequency": "Weekly",
#             "fertilizer_type": "Organic",
#             "sunlight_hours": 6,
#             "temperature": 24,
#             "humidity": 50
#         }
#     }

#     response = client.post(
#         '/predict',
#         data=json.dumps(payload),
#         content_type='application/json'
#     )

#     print("RESPONSE STATUS CODE:", response.status_code)
#     print("RESPONSE DATA:", response.data.decode())

#     assert response.status_code == 200

def test_predict_logistic_invalid_input(client):
    payload = {
        "TypeofModel": "logistic",
        "NameOfModel": "log_reg_pipeline.joblib",
        "Data": {
            "Sunlight_Hours": 0,  # Invalid
            "Temperature": -5,    # Invalid
            "Humidity": 150       # Invalid
        }
    }
    response = client.post('/predict', data=json.dumps(payload), content_type='application/json')
    assert response.status_code == 400
    assert "error" in response.get_json()



def test_predict_empty_json(client):
    response = client.post('/predict', data=json.dumps({}), content_type='application/json')
    assert response.status_code == 400
    assert "error" in response.get_json()



def test_predict_logistic_invalid_types(client):
    payload = {
        "TypeofModel": "logistic",
        "NameOfModel": "log_reg_pipeline.joblib",
        "Data": {
            "Soil_Type": "Loamy",
            "Water_Frequency": "Weekly",
            "Fertilizer_Type": "Organic",
            "Sunlight_Hours": "six",   # Invalid type
            "Temperature": "twenty",   # Invalid type
            "Humidity": "high"         # Invalid type
        }
    }
    response = client.post('/predict', data=json.dumps(payload), content_type='application/json')
    assert response.status_code == 500 or response.status_code == 400
    assert "error" in response.get_json()





def test_predict_logistic_invalid_types(client):
    payload = {
        "TypeofModel": "logistic",
        "NameOfModel": "log_reg_pipeline.joblib",
        "Data": {
            "soil_Type": "Loamy",
            "water_Frequency": "Weekly",
            "fertilizer_Type": "Organic",
            "sunlight_hours": "six",   # Invalid type
            "temperature": "twenty",   # Invalid type
            "humidity": "high"         # Invalid type
        }
    }
    response = client.post('/predict', data=json.dumps(payload), content_type='application/json')
    assert response.status_code == 500 or response.status_code == 400
    assert "error" in response.get_json()



def test_predict_model_not_found(client):
    payload = {
        "TypeofModel": "logistic",
        "NameOfModel": "non_existing_model.joblib",  # Invalid model
        "Data": {
            "soil_type": "Loamy",
            "water_frequency": "Weekly",
            "fertilizer_type": "Organic",
            "sunlight_hours": 6,
            "temperature": 24,
            "humidity": 50
        }
    }
    response = client.post('/predict', data=json.dumps(payload), content_type='application/json')
    assert response.status_code == 404
    assert "error" in response.get_json()



def test_predict_unsupported_model_type(client):
    payload = {
        "TypeofModel": "unsupported_model",
        "NameOfModel": "log_reg_pipeline.joblib",
        "Data": {
            "soil_type": "Loamy",
            "water_frequency": "Weekly",
            "fertilizer_type": "Organic",
            "sunlight_hours": 6,
            "temperature": 24,
            "humidity": 50
        }
    }
    response = client.post('/predict', data=json.dumps(payload), content_type='application/json')
    assert response.status_code == 400
    assert "error" in response.get_json()

    
    # --- Test-getmodels ------------------------------------------------------------
 
def test_list_models_success(client):
    mock_files = ['model1.joblib', 'ignore.txt', 'model2.joblib']

    with patch('ModelTrainingAPI.os.path.exists', return_value=True), \
         patch('ModelTrainingAPI.os.listdir', return_value=mock_files), \
         patch('ModelTrainingAPI.os.path.isfile', return_value=True):

        response = client.get('/models')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert 'model1.joblib' in data['model_files']
        assert 'model2.joblib' in data['model_files']
        assert 'ignore.txt' not in data['model_files']

def test_list_models_folder_missing(client):
    with patch('ModelTrainingAPI.os.path.exists', return_value=False):
        response = client.get('/models')
        assert response.status_code == 404
        data = response.get_json()
        assert data['error'] == 'Models folder not found.'

def test_list_models_unexpected_error(client):
    with patch('ModelTrainingAPI.os.path.exists', side_effect=Exception("Simulated failure")):
        response = client.get('/models')
        assert response.status_code == 500
        data = response.get_json()
        assert 'error' in data
        assert 'Simulated failure' in data['error']


        