using System;
using System.Text.Json.Serialization;

namespace APII.Models
{
    public class DemoPlantDTO
    {
        [JsonPropertyName("Id")]
        public int Id { get; set; }

        [JsonPropertyName("soil_type")]
        public string soil_type { get; set; }

        [JsonPropertyName("water_frequency")]
        public string water_frequency { get; set; }

        [JsonPropertyName("fertilizer_type")]
        public string fertilizer_type { get; set; }

        private float _sunlight_hours;
        private float _temperature;
        private float _humidity;

        [JsonPropertyName("sunlight_hours")]
        public float sunlight_hours
        {
            get => _sunlight_hours;
            set
            {
                if (value < 0 || value > 24)
                    throw new ArgumentOutOfRangeException(nameof(sunlight_hours), "Sunlight hours must be between 0 and 24.");
                _sunlight_hours = value;
            }
        }

        [JsonPropertyName("temperature")]
        public float temperature
        {
            get => _temperature;
            set
            {
                if (value < -50 || value > 60)
                    throw new ArgumentOutOfRangeException(nameof(temperature), "Temperature must be between -50 and 60 Celsius.");
                _temperature = value;
            }
        }

        [JsonPropertyName("humidity")]
        public float humidity
        {
            get => _humidity;
            set
            {
                if (value < 0 || value > 100)
                    throw new ArgumentOutOfRangeException(nameof(humidity), "Humidity must be between 0% and 100%.");
                _humidity = value;
            }
        }

        [JsonPropertyName("growth_milestone")]
        public int growth_milestone { get; set; }
    }
}
