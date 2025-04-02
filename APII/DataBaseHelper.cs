using Npgsql;
using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using API;

public static class DatabaseHelper
{
    private static string connectionString = "Host=b4miactrrxbtqyg0obdl-postgresql.services.clever-cloud.com;Port=50013;Username=ujmpoinam3senrd9at7f;Password=FZHjl5BLPSkZWlFJ6rXQqDfUK4Ekwz;Database=b4miactrrxbtqyg0obdl";

    // Asynchronous connection method
    public static async Task<NpgsqlConnection> GetConnectionAsync()
    {
        var conn = new NpgsqlConnection(connectionString);
        await conn.OpenAsync();
        return conn;
    }

    // Get sensor data from database
    public static async Task<List<SensorData>> GetSensorDataAsync()
    {
        var sensorDataList = new List<SensorData>();

        using (var conn = await GetConnectionAsync())
        {
            using (var cmd = new NpgsqlCommand("SELECT temperature, humidity, co2, light, soil_moisture FROM sensor_data;", conn))
            {
                using (var reader = await cmd.ExecuteReaderAsync())
                {
                    while (await reader.ReadAsync())
                    {
                        var sensorData = new SensorData
                        {
                            Temperature = reader.GetFloat(0),
                            Humidity = reader.GetFloat(1),
                            Co2 = reader.GetFloat(2),
                            Light = reader.GetFloat(3),
                            SoilMoisture = reader.GetFloat(4)
                        };
                        sensorDataList.Add(sensorData);
                    }
                }
            }
        }

        return sensorDataList;
    }

    // Insert sensor data into the database
    public static async Task InsertSensorDataAsync(SensorData sensorData)
    {
        using (var conn = await GetConnectionAsync())
        {
            using (var cmd = new NpgsqlCommand("INSERT INTO sensor_data (temperature, humidity, co2, light, soil_moisture) VALUES (@temperature, @humidity, @co2, @light, @soil_moisture);", conn))
            {
                cmd.Parameters.AddWithValue("temperature", sensorData.Temperature);
                cmd.Parameters.AddWithValue("humidity", sensorData.Humidity);
                cmd.Parameters.AddWithValue("co2", sensorData.Co2);
                cmd.Parameters.AddWithValue("light", sensorData.Light);
                cmd.Parameters.AddWithValue("soil_moisture", sensorData.SoilMoisture);

                await cmd.ExecuteNonQueryAsync();
            }
        }
    }
}
