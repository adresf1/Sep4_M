using System;
using MLService.Models.Prediction;
using Microsoft.AspNetCore.Mvc;
using System.Collections.Generic;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using System.Collections.Generic;
using System.Net.Http;
using System.Threading.Tasks;
using Newtonsoft.Json;

namespace MLService.Controllers;

[Route("api/[controller]")]
public class PredictionController : ControllerBase
{
    private readonly HttpClient _httpClient;
    private readonly string _endpoint = "http://Sep4-ModelTraining-Service:5000/";

    public PredictionController(HttpClient httpClient)
    {
        _httpClient = httpClient;
      
    }
    
   

    //GET: prediction
    [HttpGet]
    public async Task<ActionResult<string>> GetModels()
    {
        List<PredictionModel> models = new List<PredictionModel>()
        {
            new PredictionModel("rfc","RandomForestRegressor.joblib")
        };
        return JsonConvert.SerializeObject(models);
    }

    // POST: prediction
    [HttpPost]
    public async Task<ActionResult<string>> Predict([FromBody] PredictionRequest data)
    {
        string endpoint = _endpoint + "rfc_predict";
        
        string payload = JsonConvert.SerializeObject(data);
        
        var content = new StringContent(payload, System.Text.Encoding.UTF8, "application/json");
        var response = await _httpClient.PostAsync(endpoint, content);

        if (response.IsSuccessStatusCode)
        {
            return await response.Content.ReadAsStringAsync();
        }
        else
        {
            // TODO: Implement logging
            string error = $"{response.StatusCode}: Failed to request prediction: {await response.Content.ReadAsStringAsync()}";
            Console.WriteLine(error);
            return error;
        }
    }
    
    [HttpPost("logistic")]
public async Task<ActionResult<string>> PredictLogistic([FromBody] LogisticPredictionRequest data)
{
    string endpoint = _endpoint + "logistic_predict";
    var content = new StringContent(JsonConvert.SerializeObject(data), System.Text.Encoding.UTF8, "application/json");
    var response = await _httpClient.PostAsync(endpoint, content);

    if (response.IsSuccessStatusCode)
        return await response.Content.ReadAsStringAsync();
    else
    {
        string error = $"{response.StatusCode}: Failed to request Logistic prediction: {await response.Content.ReadAsStringAsync()}";
        Console.WriteLine(error);
        return error;
    }
}
}
