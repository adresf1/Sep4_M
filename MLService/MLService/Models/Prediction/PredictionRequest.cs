namespace MLService.Models.Prediction;

public class PredictionRequest
{
    public string TypeofModel { get; set; }
    public string NameOfModel { get; set; }
    public PredictionData Data { get; set; }

    public PredictionRequest()
    {
        
    }

    public PredictionRequest(string typeofModel, string nameOfModel, PredictionData data)
    {
        TypeofModel = typeofModel;
        NameOfModel = nameOfModel;
        this.Data = data;
    }
}