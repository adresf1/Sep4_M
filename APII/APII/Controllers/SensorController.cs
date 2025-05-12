using Microsoft.AspNetCore.Mvc;
using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using APII;
using APII.Models;
using MLService.Models.Prediction;
using Newtonsoft.Json.Linq; // Justér navnerum efter din løsning


namespace APII.Controllers;

[Route("api/[controller]")]
[ApiController]
public class SensorController : ControllerBase
{
    private readonly HttpClient _httpClient;
    private readonly string _pythonServiceUrl = "http://Sep4-DataProcessing-Service:5000/fetch-sensor-data";
    private readonly string _mlServiceUrl = "http://Sep4-ML-Service:8080/api/prediction"; // ML Service endpoint

    public SensorController(HttpClient httpClient)
    {
        _httpClient = httpClient;
    }

  

    // GET: api/sensors
    [HttpGet]
    public async Task<ActionResult<IEnumerable<SensorData>>> GetSensors()
    {
        try
        {
            var response = await _httpClient.GetStringAsync(_pythonServiceUrl);
            var data = JsonConvert.DeserializeObject<List<SensorData>>(response);
            return Ok(data);
        }
        catch (Exception ex)
        {
            return BadRequest($"Error retrieving sensor data: {ex.Message}");
        }
    }

    // POST: api/Sensor
    [HttpPost]
    public async Task<ActionResult<string>> PostSensorData([FromBody] PostSensorData sensorData)
    {
        try
        {
            var payload = new List<PostSensorData> { sensorData };
            var json = JsonConvert.SerializeObject(payload);

            var content = new StringContent(json, Encoding.UTF8, "application/json");
            var response = await _httpClient.PostAsync(_pythonServiceUrl, content);

            if (response.IsSuccessStatusCode)
            {
                return Ok("Sensor data sent successfully.");
            }
            else
            {
                var errorResponse = await response.Content.ReadAsStringAsync();
                return BadRequest($"Failed to send sensor data. Python response: {errorResponse}");
            }
        }
        catch (Exception ex)
        {
            return BadRequest($"Error sending sensor data: {ex.Message}");
        }
    }

    [HttpGet("model")]
    public async Task<ActionResult<string>> GetModel()
    {
        try
        {
            var response = await _httpClient.GetStringAsync($"{_mlServiceUrl}");
            return Ok(response);
        }
        catch (Exception ex)
        {
            return BadRequest($"Error retrieving model: {ex.Message}");
        }
    }

   [HttpPost("predict")]
public async Task<IActionResult> PredictUnified()
{
    try
    {
        using var reader = new StreamReader(Request.Body);
        var body = await reader.ReadToEndAsync();

        if (string.IsNullOrWhiteSpace(body))
            return BadRequest("Request body is empty.");

        JObject jsonObj;
        try
        {
            jsonObj = JObject.Parse(body);
        }
        catch (JsonReaderException jex)
        {
            return BadRequest($"Invalid JSON format: {jex.Message}");
        }

        var typeOfModel = jsonObj["TypeofModel"]?.ToString();
        if (string.IsNullOrWhiteSpace(typeOfModel))
            return BadRequest("Missing 'TypeofModel' in request body.");

        string targetUrl;
        StringContent content;

        if (typeOfModel.Equals("logistic", StringComparison.OrdinalIgnoreCase))
        {
            var logisticRequest = jsonObj.ToObject<LogisticPredictionRequest>();
            var json = JsonConvert.SerializeObject(logisticRequest);
            content = new StringContent(json, Encoding.UTF8, "application/json");
            targetUrl = $"{_mlServiceUrl}/predict";
        }
        else if (typeOfModel.Equals("rfc", StringComparison.OrdinalIgnoreCase))
        {
            var rfcRequest = jsonObj.ToObject<Rfc_PredictionRequest>();
            var json = JsonConvert.SerializeObject(rfcRequest);
            content = new StringContent(json, Encoding.UTF8, "application/json");
            targetUrl = $"{_mlServiceUrl}/predict"; // default is RFC
        }
        else
        {
            return BadRequest("Unsupported TypeofModel. Use 'logistic' or 'rfc'.");
        }

        var response = await _httpClient.PostAsync(targetUrl, content);
        var responseContent = await response.Content.ReadAsStringAsync();

        if (response.IsSuccessStatusCode)
        {
            return Ok(responseContent);
        }

        return BadRequest($"Prediction failed: {responseContent}");
    }
    catch (Exception ex)
    {
        return BadRequest($"Error during prediction: {ex.Message}");
    }
}

}
        