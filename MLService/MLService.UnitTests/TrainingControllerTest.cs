using MLService.Controllers;
using NSubstitute;
using System.Net;
using MLService.Models.Training;
using Newtonsoft.Json;
using NSubstitute.ClearExtensions;

namespace MLService.UnitTests;

public class TrainingControllerTest
{
    private TrainingController _trainingController;
    private HttpClient _mockedClient;
    
    [SetUp]
    public void Setup()
    {
        _mockedClient = Substitute.For<HttpClient>();
        _trainingController = new TrainingController(_mockedClient);
    }

    [Test]
    public void Training()
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
        var mockResult = new HttpResponseMessage() {StatusCode = HttpStatusCode.OK, Content = new StringContent(resultPayload)};
        _mockedClient.PostAsync((string?)default, default).ReturnsForAnyArgs(mockResult);
        
        var trainingResult = _trainingController.Train(payload).Result;

        var calls = _mockedClient.ReceivedCalls();
        Assert.That(_mockedClient.ReceivedCalls().Count(), Is.EqualTo(1));
        Assert.That(trainingResult.Value, Is.EqualTo(resultPayload));
        
        // Cleanup
        _mockedClient.ClearSubstitute();
    }
    
    [TearDown]
    public void TearDown()
    {
        _mockedClient.Dispose();
    }
}