using Microsoft.AspNetCore.Mvc;
using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using API;
using APII;
using MLService.Models.Prediction; // Justér navnerum efter din løsning

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

    [HttpPost("logistic")]
    public async Task<IActionResult> ForwardLogisticPrediction([FromBody] LogisticPredictionRequest request)
    {
        try
        {
            var json = JsonConvert.SerializeObject(request);
            var content = new StringContent(json, Encoding.UTF8, "application/json");

            var response = await _httpClient.PostAsync($"{_mlServiceUrl}/logistic", content);

            if (response.IsSuccessStatusCode)
            {
                var result = await response.Content.ReadAsStringAsync();
                return Ok(result);
            }

            var error = await response.Content.ReadAsStringAsync();
            return BadRequest($"ML service logistic prediction failed: {error}");
        }
        catch (Exception ex)
        {
            return BadRequest($"Error forwarding logistic prediction: {ex.Message}");
        }
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

    [HttpPost("rfc-predict")]
    public async Task<ActionResult<string>> Predict([FromBody] Rfc_PredictionRequest data)
    {
        try
        {
            var json = JsonConvert.SerializeObject(data);
            var content = new StringContent(json, Encoding.UTF8, "application/json");

            var response = await _httpClient.PostAsync(_mlServiceUrl, content); // Default POST goes to rfc_predict

            if (response.IsSuccessStatusCode)
            {
                var result = await response.Content.ReadAsStringAsync();
                return Ok(result);
            }

            var error = await response.Content.ReadAsStringAsync();
            return BadRequest($"RFC prediction failed: {error}");
        }
        catch (Exception ex)
        {
            return BadRequest($"Error during RFC prediction: {ex.Message}");
        }
    }
}
        