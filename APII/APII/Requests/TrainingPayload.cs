namespace APII.APII.Requests;
public class TrainingPayload
{
     public string model_name { get; set; } = "MyLRModel_v6";
    public string model_type { get; set; } = "";
    public string table_name { get; set; } = "plant_data_test";
    public string targetMeasure { get; set; } = "growth_milestone";
    public float testSize { get; set; } = 0.2f;
    public int estimators { get; set; } = 100;
    public int randomState { get; set; } = 45;

    public string target_measure { get; set; } = "growth_milestone";
    public float test_size { get; set; } = 0.2f;
    public int max_depth { get; set; } = 5; 
}