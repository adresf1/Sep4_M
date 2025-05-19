using Microsoft.AspNetCore.Mvc;
using MLService.Models;
using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Net.Http;
using System.Text;
using APII.Models;
using System.Threading.Tasks;

namespace APII.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class DemoDataController : ControllerBase
    {
        private readonly HttpClient _httpClient;
        private readonly string _pythonServiceUrl = "http://Sep4-DataProcessing-Service:5000/DemoDataRaw"; // Example base

        public DemoDataController(HttpClient httpClient)
        {
            _httpClient = httpClient;
        }

        // GET: api/DemoData
        [HttpGet]
        public async Task<ActionResult<IEnumerable<DemoPlantDTO>>> GetAll()
        {
            try
            {
                var response = await _httpClient.GetStringAsync(_pythonServiceUrl);
                var data = JsonConvert.DeserializeObject<List<DemoPlantDTO>>(response);
                return Ok(data);
            }
            catch (Exception ex)
            {
                return BadRequest($"Error fetching data: {ex.Message}");
            }
        }

        // GET: api/DemoData/{id}
        [HttpGet("{id}")]
        public async Task<ActionResult<DemoPlantDTO>> GetById(int id)
        {
            try
            {
                var response = await _httpClient.GetStringAsync($"{_pythonServiceUrl}/{id}");
                var item = JsonConvert.DeserializeObject<DemoPlantDTO>(response);
                return Ok(item);
            }
            catch (HttpRequestException)
            {
                return NotFound($"Item with ID {id} not found.");
            }
            catch (Exception ex)
            {
                return BadRequest($"Error fetching item: {ex.Message}");
            }
        }

        // POST: api/DemoData
        [HttpPost]
        public async Task<ActionResult<DemoPlantDTO>> Create([FromBody] DemoPlantDTO newItem)
        {
            try
            {
                var content = new StringContent(JsonConvert.SerializeObject(newItem), Encoding.UTF8, "application/json");
                var response = await _httpClient.PostAsync(_pythonServiceUrl, content);

                if (!response.IsSuccessStatusCode)
                    return BadRequest($"Failed to create item. Status: {response.StatusCode}");

                var created = JsonConvert.DeserializeObject<DemoPlantDTO>(await response.Content.ReadAsStringAsync());
                return CreatedAtAction(nameof(GetById), new { id = created.Id }, created);
            }
            catch (Exception ex)
            {
                return BadRequest($"Error creating item: {ex.Message}");
            }
        }

        // POST: api/DemoDataRaw/{id}
        [HttpPost("{id}")]
        public async Task<IActionResult> Update(int id, [FromBody] DemoPlantDTO updatedItem)
        {
            try
            {
                var content = new StringContent(JsonConvert.SerializeObject(updatedItem), Encoding.UTF8, "application/json");

                // Send POST request instead of PUT
                var response = await _httpClient.PostAsync($"{_pythonServiceUrl}/{id}", content);

                if (!response.IsSuccessStatusCode)
                {
                    var responseContent = await response.Content.ReadAsStringAsync();
                    return NotFound($"Item with ID {id} not found or update failed. Details: {responseContent}");
                }

                var successContent = await response.Content.ReadAsStringAsync();
                return Ok(JsonConvert.DeserializeObject(successContent));
            }
            catch (Exception ex)
            {
                return BadRequest($"Error updating item: {ex.Message}");
            }
        }

        // DELETE: api/DemoData/{id}
        [HttpDelete("{id}")]
        public async Task<IActionResult> Delete(int id)
        {
            try
            {
                var response = await _httpClient.DeleteAsync($"{_pythonServiceUrl}/{id}");
                if (!response.IsSuccessStatusCode)
                    return NotFound($"Item with ID {id} not found.");

                return NoContent();
            }
            catch (Exception ex)
            {
                return BadRequest($"Error deleting item: {ex.Message}");
            }
        }
    }
}
