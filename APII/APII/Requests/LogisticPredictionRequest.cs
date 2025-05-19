namespace MLService.Models.Prediction;

public class LogisticPredictionRequest
{
    public string TypeofModel { get; set; }
    public string NameOfModel { get; set; }
    public LogisticInput Data { get; set; }
}