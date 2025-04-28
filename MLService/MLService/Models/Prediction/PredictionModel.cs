namespace MLService.Models.Prediction;

public class PredictionModel
{
    public string TypeOfModel { get; set; }
    public string NameOfModel { get; set; }

    public PredictionModel()
    {
        
    }
    
    public PredictionModel(string typeOfModel, string nameOfModel)
    {
        TypeOfModel = typeOfModel;
        NameOfModel = nameOfModel;
    }
}