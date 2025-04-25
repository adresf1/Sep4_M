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
using Newtonsoft.Json;
 [Route("api/[controller]")]
    [ApiController]
    public class SensorController : ControllerBase
    {

        private readonly HttpClient _httpClient;
        private readonly string _pythonServiceUrl = "http://localhost:5000/fetch-sensor-data";

        public SensorController(HttpClient httpClient)
        {
            Console.WriteLine("Hello World!");
            _httpClient = httpClient;
        }

        // GET: api/sensors
        [HttpGet]
        public async Task<ActionResult<IEnumerable<SensorData>>> GetSensors()
        {
            try
            {
                Console.WriteLine("Hi from get sensors!");
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
        public async Task<ActionResult<IEnumerable<SensorData>>> CreateSensorData([FromBody] List<SensorData> sensorDataList)
        {
            try
            {
                var content = new StringContent(JsonConvert.SerializeObject(sensorDataList), System.Text.Encoding.UTF8, "application/json");
                var response = await _httpClient.PostAsync(_pythonServiceUrl, content);

                if (response.IsSuccessStatusCode)
                {
                    return CreatedAtAction(nameof(GetSensors), new { count = sensorDataList.Count }, sensorDataList);
                }

                return BadRequest("Error sending sensor data to Python service.");
            }
            catch (Exception ex)
            {
                return BadRequest($"Error posting sensor data: {ex.Message}");
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
            
    }
        