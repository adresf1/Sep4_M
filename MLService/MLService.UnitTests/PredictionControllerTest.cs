using MLService.Controllers;
using System.Net;
using MLService.Models.Prediction;
using Newtonsoft.Json;
using RichardSzalay.MockHttp;
using Microsoft.AspNetCore.Mvc;

namespace MLService.UnitTests;

public class PredictionControllerTest
{
    private PredictionController _predictionController;
    private MockHttpMessageHandler _mockedHandler;
    
    [SetUp]
    public void Setup()
    {
        _mockedHandler = new MockHttpMessageHandler();
        _predictionController = new PredictionController(_mockedHandler.ToHttpClient());
    }

    [Test]
    public async Task GetModels()
    {
        string json = "[{\"TypeOfModel\":\"rfc\",\"NameOfModel\":\"RandomForestRegressor.joblib\"}]";
        
        var models = _predictionController.GetModels().Result;
        
        Assert.That(models.Value == json);
    }

    [Test]
    public async Task ValidPrediction()
    {
        PredictionRequest req = new PredictionRequest()
        {
            TypeofModel = "rfc",
            NameOfModel = "RandomForestRegressor.joblib",
            Data = new PredictionData()
            {
                soil_type = 1,
                sunlight_hours = 6,
                water_frequency = 3,
                fertilizer_type = 1,
                temperature = 22,
                humidity = 60
            }
        };

        // Configure Mock
        string resultPayload = JsonConvert.SerializeObject(new double[] {50.2, 49.8});
        
        var request = _mockedHandler.When(method: HttpMethod.Post, "http://Sep4-ModelTraining-Service:5000/predict")
            .Respond("application/json", resultPayload);
        
        var response = await _predictionController.Predict(JsonConvert.SerializeObject(req));
        var result = response.Value;
        
        Assert.That(_mockedHandler.GetMatchCount(request), Is.EqualTo(1));
        Assert.That(result, Is.EqualTo(resultPayload));
        
        // Cleanup
        _mockedHandler.Clear();
    }

    [TearDown]
    public void TearDown()
    {
        _mockedHandler.Dispose();
    }
}