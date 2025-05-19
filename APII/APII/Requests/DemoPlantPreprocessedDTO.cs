using System;
using System.Text.Json.Serialization;

namespace APII.Models
{
    public class DemoPlantPreprocessedDTO
    {
        [JsonPropertyName("Id")]
        public int Id { get; set; }

        [JsonPropertyName("soil_loam")]
        public bool soil_loam { get; set; }

        [JsonPropertyName("soil_clay")]
        public bool soil_clay { get; set; }

        [JsonPropertyName("soil_sandy")]
        public bool soil_sandy { get; set; }

        [JsonPropertyName("water_bi_weekly")]
        public bool water_bi_weekly { get; set; }

        [JsonPropertyName("water_daily")]
        public bool water_daily { get; set; }

        [JsonPropertyName("water_weekly")]
        public bool water_weekly { get; set; }

        [JsonPropertyName("fertilizer_chemical")]
        public bool fertilizer_chemical { get; set; }

        [JsonPropertyName("fertilizer_none")]
        public bool fertilizer_none { get; set; }

        [JsonPropertyName("fertilizer_organic")]
        public bool fertilizer_organic { get; set; }

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
                if (value < -20 || value > 70)
                    throw new ArgumentOutOfRangeException(nameof(temperature), "Temperature must be between -20 and 70 Celsius.");
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

        // Quadratic Calculated Columns fields
        [JsonPropertyName("sunlight_hours_quadratic")]
        public float sunlight_hours_quadratic { get; set; }

        [JsonPropertyName("temperature_quadratic")]
        public float temperature_quadratic { get; set; }

        [JsonPropertyName("humidity_quadratic")]
        public float humidity_quadratic { get; set; }

        // Growth milestone - Target Measure
        [JsonPropertyName("growth_milestone")]
        public int growth_milestone { get; set; }
    }
}