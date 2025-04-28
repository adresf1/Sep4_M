namespace MLService.Models.Training;

public class TrainingPayload
{
    public string model_name { get; set; }
    public string table_name { get; set; }
    public string target_measure { get; set; }
    public float test_size { get; set; }
    public int estimators { get; set; }
    public int random_state { get; set; }

    public TrainingPayload()
    {
        
    }
}