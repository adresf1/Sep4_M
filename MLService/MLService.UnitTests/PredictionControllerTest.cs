using MLService.Controllers;
using System.Net;
using Microsoft.AspNetCore.Http;
using MLService.Models.Prediction;
using Newtonsoft.Json;
using RichardSzalay.MockHttp;
using Microsoft.AspNetCore.Mvc;
using System.Text;

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
        string expectedResponse =
            "{\"model_files\": [\"log_reg_pipeline.joblib\",\"RandomForestRegressor_20250511_210430.joblib\",\"RandomForestRegressor.joblib\",\"RandomForestRegressor_20250510_160735.joblib\"],\"status\": \"success\"}";
        
        var request = _mockedHandler.When(method: HttpMethod.Get, "http://Sep4-ModelTraining-Service:5000/models")
            .Respond("application/json", "{\"model_files\": [\"log_reg_pipeline.joblib\",\"RandomForestRegressor_20250511_210430.joblib\",\"RandomForestRegressor.joblib\",\"RandomForestRegressor_20250510_160735.joblib\"],\"status\": \"success\"}");
        
        var models = _predictionController.GetModels().Result;
        
        Assert.That(_mockedHandler.GetMatchCount(request), Is.EqualTo(1));
        Assert.That(models.Value, Is.EqualTo(expectedResponse));
        
        // Cleanup
        _mockedHandler.Clear();
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
        _predictionController.ControllerContext = controllerContext;
            
        var response = await _predictionController.Predict();
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