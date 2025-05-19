from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, Boolean

Base = declarative_base()

# Cache for table models
_model_cache = {}

def get_model_for_table(table_name: str):
    # If the model is already in cache, return it
    if table_name not in _model_cache:
        if table_name == 'sensor_data':
            _model_cache[table_name] = create_sensor_data_model()
        else:
            raise ValueError(f"No manual schema defined for table '{table_name}'.")

    return _model_cache[table_name]

def create_plant_model(table_name):
    class Plant(Base):
        __tablename__ = table_name
        __table_args__ = {'extend_existing': True} 

        id = Column(Integer, primary_key=True, autoincrement=True)
        soil_type = Column(String)
        sunlight_hours = Column(Float)
        water_frequency = Column(String)
        fertilizer_type = Column(String)
        temperature = Column(Float)
        humidity = Column(Float)
        growth_milestone = Column(Integer)
        
        def __repr__(self):
            return f"<Plant(id={self.id}, soil_type={self.soil_type}, sunlight_hours={self.sunlight_hours}, ...)>"

    return Plant

def create_preprocessed_plant_model(table_name):
    class PlantPreprocessed(Base):
        __tablename__ = table_name
        __table_args__ = {'extend_existing': True}

        id = Column(Integer, primary_key=True, autoincrement=True)

        # One-hot encoded soil types
        soil_loam = Column(Boolean, default=False)
        soil_clay = Column(Boolean, default=False)
        soil_sandy = Column(Boolean, default=False)

        # One-hot encoded water frequencies
        water_bi_weekly = Column(Boolean, default=False)
        water_daily = Column(Boolean, default=False)
        water_weekly = Column(Boolean, default=False)

        # One-hot encoded fertilizer types
        fertilizer_chemical = Column(Boolean, default=False)
        fertilizer_none = Column(Boolean, default=False)
        fertilizer_organic = Column(Boolean, default=False)

        # Original numeric fields
        sunlight_hours = Column(Float)
        temperature = Column(Float)
        humidity = Column(Float)

        # Quadratic Calculated Columns fields
        sunlight_hours_quadratic = Column(Float)
        temperature_quadratic = Column(Float)
        humidity_quadratic = Column(Float)

        # Growth milestone
        growth_milestone = Column(Integer)

    return PlantPreprocessed

def create_sensor_data_model():
    # Define the SensorData class
    class SensorData(Base):
        __tablename__ = 'sensor_data'
        __table_args__ = {'extend_existing': True}  

        id = Column(Integer, primary_key=True)
        air_temperature = Column(Float)
        air_humidity = Column(Float)
        soil_moisture = Column(Float)
        light = Column(Float)
        light_type = Column(String)
        light_max = Column(Float)
        light_min = Column(Float)
        artificial_light = Column(Boolean)
        light_avg = Column(Float)
        distance_to_height = Column(Float)
        water = Column(Float)
        time_since_last_watering = Column(Float)
        water_amount = Column(Float)
        watering_frequency = Column(Float)
        timestamp = Column(String)
        soil_type = Column(String)
        fertilizer_type = Column(String)
        experiment_number = Column(Integer)
        light_variation = Column(Float)
        water_need_score = Column(Float)
        
        
        
        def to_dict(self):
            return {
                'id': self.id,
                'air_temperature': self.air_temperature,
                'air_humidity': self.air_humidity,
                'soil_moisture': self.soil_moisture,
                'light': self.light,
                'light_type': self.light_type,
                'light_max': self.light_max,
                'light_min': self.light_min,
                'artificial_light': self.artificial_light,
                'light_avg': self.light_avg,
                'distance_to_height': self.distance_to_height,
                'water': self.water,
                'time_since_last_watering': self.time_since_last_watering,
                'water_amount': self.water_amount,
                'watering_frequency': self.watering_frequency,
                'timestamp': self.timestamp,
                'soil_type': self.soil_type,
                'fertilizer_type': self.fertilizer_type,
                'experiment_number': self.experiment_number,
                'light_variation': self.light_variation,
                'water_need_score': self.water_need_score
            }
            
    return SensorData        

def calculate_column_averages(session, model, column_names):
    try:
        averages = {}

        for col_name in column_names:
            col = getattr(model, col_name)
            values = session.query(col).filter(model.growth_milestone == 1).all()
            clean_values = [v[0] for v in values if v[0] is not None]

            if clean_values:
                avg = sum(clean_values) / len(clean_values)
                averages[col_name] = avg
            else:
                averages[col_name] = None

        return averages

    except Exception as e:
        raise RuntimeError(f"Error calculating column averages: {e}")
    
def one_hot_encode_columns(raw):
    # Default values for all the one-hot encoded columns (false by default)
    encoded = {
        "soil_loam": False,
        "soil_clay": False,
        "soil_sandy": False,
        "water_bi_weekly": False,
        "water_daily": False,
        "water_weekly": False,
        "fertilizer_chemical": False,
        "fertilizer_none": False,
        "fertilizer_organic": False
    }

    # Set the appropriate one-hot encoding for each field
    # Could this be improved with some enumerations definition
    if raw.soil_type == "loam":
        encoded["soil_loam"] = True
    elif raw.soil_type == "clay":
        encoded["soil_clay"] = True
    elif raw.soil_type == "sandy":
        encoded["soil_sandy"] = True

    if raw.water_frequency == "bi-weekly":
        encoded["water_bi_weekly"] = True
    elif raw.water_frequency == "daily":
        encoded["water_daily"] = True
    elif raw.water_frequency == "weekly":
        encoded["water_weekly"] = True

    if raw.fertilizer_type == "chemical":
        encoded["fertilizer_chemical"] = True
    elif raw.fertilizer_type == "none":
        encoded["fertilizer_none"] = True
    elif raw.fertilizer_type == "organic":
        encoded["fertilizer_organic"] = True

    return encoded

def copy_to_preprocessed(original_row, encoded_values, averages, session, PlantPreprocessed):
    # Create new preprocessed record
    preprocessed_row = PlantPreprocessed(
        soil_loam=encoded_values["soil_loam"],
        soil_clay=encoded_values["soil_clay"],
        soil_sandy=encoded_values["soil_sandy"],
        water_bi_weekly=encoded_values["water_bi_weekly"],
        water_daily=encoded_values["water_daily"],
        water_weekly=encoded_values["water_weekly"],
        fertilizer_chemical=encoded_values["fertilizer_chemical"],
        fertilizer_none=encoded_values["fertilizer_none"],
        fertilizer_organic=encoded_values["fertilizer_organic"],

        # Original numeric fields
        sunlight_hours=original_row.sunlight_hours,
        temperature=original_row.temperature,
        humidity=original_row.humidity,

        # Growth milestone
        growth_milestone=original_row.growth_milestone
    )

    # Quadratic Calculations using the pre-calculated averages
    if averages:
        preprocessed_row.sunlight_hours_quadratic = (original_row.sunlight_hours - averages['sunlight_hours']) ** 2
        preprocessed_row.temperature_quadratic = (original_row.temperature - averages['temperature']) ** 2
        preprocessed_row.humidity_quadratic = (original_row.humidity - averages['humidity']) ** 2

    # Add to the session and commit
    session.add(preprocessed_row)
    session.commit()

    return preprocessed_row