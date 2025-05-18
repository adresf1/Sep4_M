using System;

namespace APII.Models
{
    public class DemoPlantDTO
    {
        public int Id { get; set; }
        public string Soil_Type { get; set; }
        public string Water_Frequency { get; set; }
        public string Fertilizer_Type { get; set; }
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
                if (value < -50 || value > 60)
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

        //Target meassure
        public int Growth_Milestone { get; set; }
    }
}
