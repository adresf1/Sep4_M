using MLService.Controllers;
using System.Net;
using MLService.Models.Training;
using Newtonsoft.Json;
using RichardSzalay.MockHttp;
using Microsoft.AspNetCore.Mvc;

namespace MLService.UnitTests;

public class TrainingControllerTest
{
    private TrainingController _trainingController;
    private MockHttpMessageHandler _mockedHandler;
    
    [SetUp]
    public void Setup()
    {
        _mockedHandler = new MockHttpMessageHandler();
        _trainingController = new TrainingController(_mockedHandler.ToHttpClient());
    }

    [Test]
    public async Task TestTraining()
    {
        TrainingPayload payload = new TrainingPayload()
        {
            model_name = "RandomForestRegressor",
            table_name = "plant_data_test",
            target_measure = "growth_milestone",
            test_size = 0.25f,
            estimators = 42,
            random_state = 123
        };
        
        // Setup mock
        string resultPayload = "{'status': 'success', 'message': 'RandomForest model trained successfully.', 'model_filename': 'testmodel.joblib', 'evaluation_metrics': ''}";

        string endpoint;
        if (Environment.GetEnvironmentVariable("DOTNET_RUNNING_IN_CONTAINER") == "true")
            endpoint = "http://Sep4-API-Service:5000/train";
        else
            endpoint = "http://localhost:5010/train";
        
        var req = _mockedHandler.When(method: HttpMethod.Post, endpoint)
            .Respond("application/json", resultPayload);
        
        var response = await _trainingController.Train(payload);
        var result = response.Value;
        
        Assert.That(_mockedHandler.GetMatchCount(req), Is.EqualTo(1));
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
