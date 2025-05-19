using APII;
using APII.Controllers;
using APII.Models;
using System.Net;
using Microsoft.AspNetCore.Mvc;
using Newtonsoft.Json;
using RichardSzalay.MockHttp;
using System.Text;
using Microsoft.AspNetCore.Http;

namespace APII.UnitTests;

public class SensorControllerTest
{
    private HttpClient _mockedClient;
    private SensorController _sensorController;
    private MockHttpMessageHandler _mockedHandler;
    private SensorData _demoData;
    
    [SetUp]
    public void Setup()
    {
        _mockedHandler = new MockHttpMessageHandler();
        _sensorController = new SensorController(_mockedHandler.ToHttpClient());
        _demoData = new SensorData()
        {
            ExperimentNumber = 0,
            AirTemperature = 30.0f,
            AirHumidity = 40.0f,
            SoilMoisture = 25.0f,
            Light = 10.0f,
            LightType = "Fancy",
            LightMax = 12.5f,
            LightMin = 9.5f,
            ArtificialLight = true,
            LightAvg = 9.8f,
            DistanceToHeight = 100.3f,
            Water = 2.4f,
            TimeSinceLastWatering = 2001.3f,
            WaterAmount = 0.1f,
            WateringFrequency = 4000.0f,
            Timestamp = "2025-05-08 11:36:59.847108",
            SoilType = "Loam",
            FertilizerType = "Organic",
            LightVariation = 5.0f,
            WaterNeedScore = 24.2f
        };
    }

    [Test]
    public async Task TestGetSensors()
    {
        List<SensorData> sensors = new List<SensorData>()
        {
            _demoData
        };
        string resultPayload = JsonConvert.SerializeObject(sensors);

        var req = _mockedHandler.When(method: HttpMethod.Get, "http://Sep4-DataProcessing-Service:5000/fetch-sensor-data")
            .Respond("application/json", resultPayload);
        
        var response = await _sensorController.GetSensors();
        var result = ((OkObjectResult)response.Result).Value;
        Assert.That(_mockedHandler.GetMatchCount(req), Is.EqualTo(1));
        Assert.That(JsonConvert.SerializeObject(result), Is.EqualTo(resultPayload));
        _mockedHandler.Clear();
    }

    [Test]
    public async Task TestPostSensorData()
    {
        var payload = new PostSensorData()
        {
            ExperimentNumber = 0,
            AirTemperature = 30.0f,
            AirHumidity = 40.0f,
            SoilMoisture = 25.0f,
            Light = 10.0f,
            LightType = "Fancy",
            LightMax = 12.5f,
            LightMin = 9.5f,
            ArtificialLight = true,
            LightAvg = 9.8f,
            DistanceToHeight = 100.3f,
            Water = 2.4f,
            TimeSinceLastWatering = 2001.3f,
            WaterAmount = 0.1f,
            WateringFrequency = 4000.0f,
            Timestamp = "2025-05-08 11:36:59.847108",
            SoilType = "Loam",
            FertilizerType = "Organic"
        };
        
        var req = _mockedHandler.When(method: HttpMethod.Post, "http://Sep4-DataProcessing-Service:5000/fetch-sensor-data")
            .Respond("application/json", JsonConvert.SerializeObject("Sensor data sent successfully."));
        
        var response = await _sensorController.PostSensorData(payload);
        var result = ((OkObjectResult)response.Result).Value;
        Assert.That(_mockedHandler.GetMatchCount(req), Is.EqualTo(1));
        Assert.That(result, Is.EqualTo("Sensor data sent successfully."));
        
        // Cleanup
        _mockedHandler.Clear();
    }

    [Test]
    public async Task TestGetModel()
    {
        string json = "[{\"TypeOfModel\":\"rfc\",\"NameOfModel\":\"RandomForestRegressor.joblib\"}]";
        
        var req = _mockedHandler.When(method: HttpMethod.Get, "http://Sep4-ML-Service:8080/api/prediction")
            .Respond("application/json", json);
        
        var response = await _sensorController.GetModel();
        var result = ((OkObjectResult)response.Result).Value;
        
        Assert.That(_mockedHandler.GetMatchCount(req), Is.EqualTo(1));
        Assert.That(result, Is.EqualTo(json));
        
        // Cleanup
        _mockedHandler.Clear();
    }

    [Test]
    public async Task TestPostPrediction()
    {
        PredictionInput req = new PredictionInput()
        {
            TypeofModel = "rfc",
            NameOfModel = "RandomForestRegressor.joblib",
            Data = new PredictionData()
            {
                SoilType = 1,
                SunlightHours = 6,
                WaterFrequency = 3,
                FertilizerType = 1,
                Temperature = 22,
                Humidity = 60
            }
        };

        // Configure Mock
        string resultPayload = JsonConvert.SerializeObject(new double[] {50.2, 49.8});
        var request = _mockedHandler.When(method: HttpMethod.Post, "http://Sep4-ML-Service:8080/api/prediction/predict")
            .Respond("application/json", resultPayload);
        
        // Set request
        var requestMessage = new HttpRequestMessage();
        requestMessage.Method = HttpMethod.Post;
        requestMessage.Content = new StringContent(JsonConvert.SerializeObject(req));
        var stream = new MemoryStream(Encoding.UTF8.GetBytes(JsonConvert.SerializeObject(req)));
        var controllerContext = new ControllerContext()
        {
            HttpContext = new DefaultHttpContext()
            {
                Request = { Body = stream, ContentLength = stream.Length }
            }
        };
        _sensorController.ControllerContext = controllerContext;
        
        var response = await _sensorController.PredictUnified();
        var result = ((OkObjectResult)response.Result).Value;
        
        Assert.That(_mockedHandler.GetMatchCount(request), Is.EqualTo(1));
        Assert.That(result, Is.EqualTo(resultPayload));
        
        // Cleanup
        _mockedHandler.Clear();
    }

    [Test]
    public async Task TestGetTables()
    {
        List<string> tables = new List<string>()
        {
            "db1",
            "db2"
        };
        string resultPayload = JsonConvert.SerializeObject(tables);
        
        var req = _mockedHandler.When(method: HttpMethod.Get, "http://Sep4-DataProcessing-Service:5000/get-tables")
            .Respond("application/json", resultPayload);
        
        var response = await _sensorController.GetTables();
        var result = ((OkObjectResult)response.Result).Value;
        Assert.That(_mockedHandler.GetMatchCount(req), Is.EqualTo(1));
        Assert.That(JsonConvert.SerializeObject(result), Is.EqualTo(resultPayload));
        _mockedHandler.Clear();
    }
    
    [TearDown]
    public void TearDown()
    {
        _mockedHandler.Dispose();
    }
}