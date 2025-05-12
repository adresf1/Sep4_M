using APII;
using APII.Controllers;
using APII.Models;
using NSubstitute;
using System.Net;
using Newtonsoft.Json;
using NSubstitute.ClearExtensions;
using Moq;

namespace APII.UnitTests;

public class SensorControllerTest
{
    private HttpClient _mockedClient;
    private SensorController _sensorController;
    private Mock<HttpClient> _moqedClient;
    private SensorData _demoData;
    
    [SetUp]
    public void Setup()
    {
        _mockedClient = Substitute.For<HttpClient>();
        _moqedClient = new Mock<HttpClient>();
        _sensorController = new SensorController(_mockedClient);
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
    public void TestGetSensors()
    {
        List<SensorData> sensors = new List<SensorData>()
        {
            _demoData
        };
        string resultPayload = JsonConvert.SerializeObject(sensors);
        /*_moqedClient.Setup(x =>
            x.GetStringAsync("http://Sep4-DataProcessing-Service:5000/fetch-sensor-data"))
                .Returns(Task.FromResult(resultPayload));
        var response = _sensorController.GetSensors().Result;
        Assert.Equals(response, resultPayload);*/
        _mockedClient.GetStringAsync("").ReturnsForAnyArgs(Task.FromResult(resultPayload));
        var sensorResult = _sensorController.GetSensors().Result;

        _mockedClient.Received(1).GetStringAsync("http://Sep4-DataProcessing-Service:5000/fetch-sensor-data");
        Assert.That(_mockedClient.ReceivedCalls().Count(), Is.EqualTo(1));
        Assert.That(JsonConvert.SerializeObject(sensorResult.Value), Is.EqualTo(resultPayload));
        _mockedClient.ClearSubstitute();
    }

    [Test]
    public void TestPostSensorData()
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
        var mockResult = new HttpResponseMessage() {StatusCode = HttpStatusCode.OK, Content = new StringContent("")};
        _mockedClient.PostAsync((string)default, default).ReturnsForAnyArgs(mockResult);

        var result = _sensorController.PostSensorData(payload).Result;
        Assert.That(_mockedClient.ReceivedCalls().Count(), Is.EqualTo(1));
        Assert.That(result.Value, Is.EqualTo("Sensor data sent successfully."));
        
        // Cleanup
        _mockedClient.ClearSubstitute();
    }

    [Test]
    public void TestGetModel()
    {
        string json = "[{\"TypeOfModel\":\"rfc\",\"NameOfModel\":\"RandomForestRegressor.joblib\"}]";
        
        var models = _sensorController.GetModel().Result;
        
        Assert.That(_mockedClient.ReceivedCalls().Count(), Is.EqualTo(0));
        Assert.That(models.Value == json);
        
        // Cleanup
        _mockedClient.ClearSubstitute();
    }

    [Test]
    public void TestPostPrediction()
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
        var mockResult = new HttpResponseMessage() {StatusCode = HttpStatusCode.OK, Content = new StringContent(resultPayload)};
        _mockedClient.PostAsync((string?)default, default).ReturnsForAnyArgs(mockResult);
        
        var prediction = _sensorController.PredictUnified().Result;
        
        Assert.That(_mockedClient.ReceivedCalls().Count(), Is.EqualTo(1));
        //Assert.That(prediction, Is.EqualTo(resultPayload));
        
        // Cleanup
        _mockedClient.ClearSubstitute();
    }
    
    [TearDown]
    public void TearDown()
    {
        _mockedClient.Dispose();
    }
}