namespace API;

public class SensorData
{
   
    public int ExperimentNumber { get; set; }
    public float AirTemperature { get; set; }
    public float AirHumidity { get; set; }
    public float SoilMoisture { get; set; }
    public float Light { get; set; }
    public string LightType { get; set; }
    public float LightMax { get; set; }
    public float LightMin { get; set; }
    public bool ArtificialLight { get; set; }
    public float LightAvg { get; set; }
    public float DistanceToHeight { get; set; }
    public float Water { get; set; }
    public float TimeSinceLastWatering { get; set; }
    public float WaterAmount { get; set; }
    public float WateringFrequency { get; set; }
    public string Timestamp { get; set; }
    public string SoilType { get; set; }
    public string FertilizerType { get; set; }
    public string ModelType { get; set; }
    public string PredictedData { get; set; }
    // Calculated figures
    public float LightVariation { get; set; }
    public float WaterNeedScore { get; set; }
    

}