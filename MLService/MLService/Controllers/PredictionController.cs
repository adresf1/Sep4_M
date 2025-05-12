using System;
using MLService.Models.Prediction;
using Microsoft.AspNetCore.Mvc;
using System.Collections.Generic;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using System.Collections.Generic;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

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

    
    [HttpPost("predict")]
    public async Task<ActionResult<string>> Predict()
    {
        using var reader = new StreamReader(Request.Body);
        var body = await reader.ReadToEndAsync();

        if (string.IsNullOrWhiteSpace(body))
            return BadRequest("Request body is empty.");

        // Peek into TypeofModel to determine which class to deserialize to
        var jsonObj = JObject.Parse(body);
        var typeOfModel = jsonObj["TypeofModel"]?.ToString();

        if (string.IsNullOrEmpty(typeOfModel))
            return BadRequest("Missing TypeofModel field.");

        string endpoint = _endpoint + "predict";
        string payload;
    
        if (typeOfModel.Equals("logistic", StringComparison.OrdinalIgnoreCase))
        {
            var logisticRequest = jsonObj.ToObject<LogisticPredictionRequest>();
            payload = JsonConvert.SerializeObject(logisticRequest);
        }
        else
        {
            var genericRequest = jsonObj.ToObject<PredictionRequest>();
            payload = JsonConvert.SerializeObject(genericRequest);
        }

        var content = new StringContent(payload, Encoding.UTF8, "application/json");
        var response = await _httpClient.PostAsync(endpoint, content);

        if (response.IsSuccessStatusCode)
        {
            return await response.Content.ReadAsStringAsync();
        }
        else
        {
            string error = $"{response.StatusCode}: Failed to request prediction: {await response.Content.ReadAsStringAsync()}";
            Console.WriteLine(error);
            return error;
        }
    }




}
