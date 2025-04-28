using System;
using Microsoft.AspNetCore.Mvc;
using System.Collections.Generic;
using System.Threading.Tasks;
using API;
using Microsoft.AspNetCore.Mvc;
using System.Collections.Generic;
using System.Net.Http;
using System.Threading.Tasks;
using API;
using APII;
using Newtonsoft.Json;
 [Route("api/[controller]")]
    [ApiController]
    public class SensorController : ControllerBase
    {
        private readonly HttpClient _httpClient;
        private readonly string _pythonServiceUrl = "http://Sep4-DataProcessing-Service:5000/fetch-sensor-data";

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

        // POST: api/sensors
        [HttpPost]
        public async Task<ActionResult<string>> PostSensorData([FromBody] PostSensorData sensorData)
        {
            try
            {
                // Wrap the object in a list
                var payload = new List<PostSensorData> { sensorData };
                var json = JsonConvert.SerializeObject(payload);

                var content = new StringContent(json, System.Text.Encoding.UTF8, "application/json");
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
                // Hent model fra Python-service via HTTP GET
                var response = await _httpClient.GetStringAsync("http://localhost:5000/get-model");
                
                return Ok(response);
            }
            catch (Exception ex)
            {
                return BadRequest($"Error retrieving model: {ex.Message}");
            }
        }

        [HttpPost("prediction")]
        public async Task<ActionResult<string>> PostPrediction([FromBody] PredictionInput input)
        {
            try
            {
                var json = JsonConvert.SerializeObject(input);
                var content = new StringContent(json, System.Text.Encoding.UTF8, "application/json");

                var response = await _httpClient.PostAsync("http://localhost:5030/prediction", content);

                if (response.IsSuccessStatusCode)
        {
            var result = await response.Content.ReadAsStringAsync();
            return Ok(result);
        }
        else
        {
            var errorResponse = await response.Content.ReadAsStringAsync();
            return BadRequest($"Prediction failed. Python response: {errorResponse}");
        }
    }
    catch (Exception ex)
    {
        return BadRequest($"Error posting prediction: {ex.Message}");
    }
}

            
    }
        