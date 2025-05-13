import pytest
import json
import os
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
    def predict_proba(self, X): return [self.probas]
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

def test_train_no_json(client):
    resp = client.post('/train', data='', content_type='application/json')
    assert resp.status_code == 400

    data = resp.get_json(silent=True)
    assert data is not None, "Forventede JSON‐fejlbesked, ikke HTML‐side"
    assert data["error"] == "No JSON data provided"

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
    assert "No data found in the table." in data["error"]


#def test_predict_missing_fields(client):
    # Send an empty JSON payload with proper content-type
#    response = client.post('/rfc_predict', json={})
    
#    assert response.status_code == 400
#   response_data = response.get_json()
#   assert response_data is not None
#    assert "error" in response_data
#    assert "Missing required top-level keys" in response_data["error"]

#def test_train_no_json(client):
    # Send an empty body with Content-Type: application/json
#    response = client.post('/train', data="", content_type="application/json")
    
    #Added this comment to test pull request
    # Assert that the status code is 415 (Unsupported Media Type) if no body is provided
    #will return bad request(400) becuase the underlying python cant connect to database  
 #   assert response.status_code == 400  # 415 because empty JSON content is unsupported

    # Check if the error message is returned in the response text
    #response_data = response.get_data(as_text=True)
    #assert "Unsupported Media Type" in response_data  # You can customize this depending on your actual response
