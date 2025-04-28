using Newtonsoft.Json;

namespace API
{
    public class SensorData
    {
        [JsonProperty("experiment_number")]
        public int ExperimentNumber { get; set; }

        [JsonProperty("air_temperature")]
        public float AirTemperature { get; set; }

        [JsonProperty("air_humidity")]
        public float AirHumidity { get; set; }

        [JsonProperty("soil_moisture")]
        public float SoilMoisture { get; set; }

        [JsonProperty("light")]
        public float Light { get; set; }

        [JsonProperty("light_type")]
        public string LightType { get; set; }

        [JsonProperty("light_max")]
        public float LightMax { get; set; }

        [JsonProperty("light_min")]
        public float LightMin { get; set; }

        [JsonProperty("artificial_light")]
        public bool ArtificialLight { get; set; }

        [JsonProperty("light_avg")]
        public float LightAvg { get; set; }

        [JsonProperty("distance_to_height")]
        public float DistanceToHeight { get; set; }

        [JsonProperty("water")]
        public float Water { get; set; }

        [JsonProperty("time_since_last_watering")]
        public float TimeSinceLastWatering { get; set; }

        [JsonProperty("water_amount")]
        public float WaterAmount { get; set; }

        [JsonProperty("watering_frequency")]
        public float WateringFrequency { get; set; }

        [JsonProperty("timestamp")]
        public string Timestamp { get; set; }

        [JsonProperty("soil_type")]
        public string SoilType { get; set; }

        [JsonProperty("fertilizer_type")]
        public string FertilizerType { get; set; }

        // Calculated figures
        [JsonProperty("light_variation")]
        public float LightVariation { get; set; }

        [JsonProperty("water_need_score")]
        public float WaterNeedScore { get; set; }
    }

    public class PredictionInput
{
    [JsonProperty("TypeofModel")]
    public string TypeofModel { get; set; }

    [JsonProperty("NameOfModel")]
    public string NameOfModel { get; set; }

    [JsonProperty("Data")]
    public PredictionData Data { get; set; }
}

public class PredictionData
{
    [JsonProperty("soil_type")]
    public int SoilType { get; set; }

    [JsonProperty("sunlight_hours")]
    public int SunlightHours { get; set; }

    [JsonProperty("water_frequency")]
    public int WaterFrequency { get; set; }

    [JsonProperty("fertilizer_type")]
    public int FertilizerType { get; set; }

    [JsonProperty("temperature")]
    public int Temperature { get; set; }

    [JsonProperty("humidity")]
    public int Humidity { get; set; }
}
}