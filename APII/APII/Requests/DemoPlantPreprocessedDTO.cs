using System;

namespace APII.Models
{
    public class DemoPlantPreprocessedDTO
    {
        public int Id { get; set; }
        public bool Soil_Loam { get; set; }
        public bool Soil_Clay { get; set; }
        public bool Soil_Sandy { get; set; }
        public bool Water_Bi_Weekly { get; set; }
        public bool Water_Daily { get; set; }
        public bool Water_Weekly { get; set; }
        public bool Fertilizer_Chemical { get; set; }
        public bool Fertilizer_None { get; set; }
        public bool Fertilizer_Organic { get; set; }
        private float sunlight_Hours;
        private float temperature;
        private float humidity;
        public float Sunlight_Hours
        {
            get => sunlight_Hours;
            set
            {
                if (value < 0 || value > 24)
                    throw new ArgumentOutOfRangeException(nameof(Sunlight_Hours), "Sunlight hours must be between 0 and 24.");
                sunlight_Hours = value;
            }
        }

        public float Temperature
        {
            get => temperature;
            set
            {
                if (value < -20 || value > 70)
                    throw new ArgumentOutOfRangeException(nameof(Temperature), "Temperature must be between -50 and 60 Celsius.");
                temperature = value;
            }
        }

        public float Humidity
        {
            get => humidity;
            set
            {
                if (value < 0 || value > 100)
                    throw new ArgumentOutOfRangeException(nameof(Humidity), "Humidity must be between 0% and 100%.");
                humidity = value;
            }
        }

        // Quadratic Calculated Columns fields
        public float Sunlight_Hours_Quadratic { get; set; }
        public float Temperature_Quadratic { get; set; }
        public float Humidity_Quadratic { get; set; }

        // Growth milestone - Target Meassure
        public int Growth_Milestone { get; set; }
    }
}
