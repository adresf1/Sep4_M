namespace MLService.Models.Prediction;

public class PredictionRequest
{
    public string TypeofModel { get; set; }
    public string NameOfModel { get; set; }
    public PredictionData Data { get; set; }
}