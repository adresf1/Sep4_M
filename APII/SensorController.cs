using Microsoft.AspNetCore.Mvc;
using System.Collections.Generic;
using System.Threading.Tasks;
using API;

[Route("api/[controller]")]
[ApiController]
public class SensorController : ControllerBase
{
    // GET: api/sensors
    [HttpGet]
    public async Task<ActionResult<IEnumerable<SensorData>>> GetSensors()
    {
        var data = await DatabaseHelper.GetSensorDataAsync();
        return Ok(data);
    }

    // POST: api/sensors
    [HttpPost]
    public async Task<ActionResult<SensorData>> CreateSensorData(SensorData sensorData)
    {
        await DatabaseHelper.InsertSensorDataAsync(sensorData);
        return CreatedAtAction(nameof(GetSensors), new { id = sensorData.Temperature }, sensorData);
    }
}