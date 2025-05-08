from sqlalchemy import Column, Integer, String, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

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

    return Plant