using System;
using MLService.Models.Training;
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
public class TrainingController : ControllerBase
{
    private readonly HttpClient _httpClient;
    private readonly string _endpoint;
    
    public TrainingController(HttpClient httpClient)
    {
        _httpClient = httpClient;
        // Check if we are running on docker and set URL accordingly
        if (Environment.GetEnvironmentVariable("DOTNET_RUNNING_IN_CONTAINER") == "true")
            _endpoint = "http://Sep4-API-Service:5000/";
        else
            _endpoint = "http://localhost:5010/";
    }
    
    // POST: training
    [HttpPost]
    public async Task<ActionResult<string>> Train([FromBody] TrainingPayload data)
    {
        string endpoint = _endpoint + "train";
        
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
            string error = $"{response.StatusCode}: Failed to request training: {await response.Content.ReadAsStringAsync()}";
            Console.WriteLine(error);
            return error;
        }
    }
}