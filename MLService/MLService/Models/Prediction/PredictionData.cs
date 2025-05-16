namespace MLService.Models.Prediction;

public class PredictionData
{
    public int soil_type { get; set; }
    public double sunlight_hours { get; set; }
    public int water_frequency { get; set; }
    public int fertilizer_type { get; set; }
    public double temperature { get; set; }
    public double humidity { get; set; }

    public PredictionData()
    {
        
    }

    public PredictionData(int soil_type, double sunlight_hours, int water_frequency, int fertilizer_type, double temperature, double humidity)
    {
        this.soil_type = soil_type;
        this.sunlight_hours = sunlight_hours;
        this.water_frequency = water_frequency;
        this.fertilizer_type = fertilizer_type;
        this.temperature = temperature;
        this.humidity = humidity;
    }

}