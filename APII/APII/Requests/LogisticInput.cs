namespace MLService.Models;

public class LogisticInput
{
    public string soil_type { get; set; }
    public string water_frequency { get; set; }
    public string fertilizer_type { get; set; }
    public int sunlight_hours { get; set; }
    public int Temperature { get; set; }
    public int Humidity { get; set; }
}