using MLService.Controllers;
using NSubstitute;
using System.Net;
using MLService.Models.Prediction;
using Newtonsoft.Json;
using NSubstitute.ClearExtensions;

namespace MLService.UnitTests;

public class PredictionControllerTest
{
    private PredictionController _predictionController;
    private HttpClient _mockedClient;
    
    [SetUp]
    public void Setup()
    {
        _mockedClient = Substitute.For<HttpClient>();
        _predictionController = new PredictionController(_mockedClient);
    }

    [Test]
    public void GetModels()
    {
        string json = "[{\"TypeOfModel\":\"rfc\",\"NameOfModel\":\"RandomForestRegressor.joblib\"}]";
        
        var models = _predictionController.GetModels().Result;
        
        Assert.That(_mockedClient.ReceivedCalls().Count(), Is.EqualTo(0));
        Assert.That(models.Value == json);
        
        // Cleanup
        _mockedClient.ClearSubstitute();
    }

    [Test]
    public void ValidPrediction()
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
        var mockResult = new HttpResponseMessage() {StatusCode = HttpStatusCode.OK, Content = new StringContent(resultPayload)};
        _mockedClient.PostAsync((string?)default, default).ReturnsForAnyArgs(mockResult);
        
        var prediction = _predictionController.Predict(req).Result;
        
        Assert.That(_mockedClient.ReceivedCalls().Count(), Is.EqualTo(1));
        Assert.That(prediction.Value, Is.EqualTo(resultPayload));
        
        // Cleanup
        _mockedClient.ClearSubstitute();
    }

    [TearDown]
    public void TearDown()
    {
        _mockedClient.Dispose();
    }
}