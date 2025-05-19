#!/usr/bin/env python
# coding: utf-8


from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import scoped_session, sessionmaker
import math
import os
from dotenv import load_dotenv, find_dotenv, dotenv_values
from DemoData import create_sensor_data_model, get_model_for_table, create_plant_model, calculate_column_averages, create_preprocessed_plant_model, one_hot_encode_columns, copy_to_preprocessed
from db import SessionLocal
from sqlalchemy import distinct, create_engine, inspect
from mock_alchemy.mocking import UnifiedAlchemyMagicMock
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Float, String, Boolean
from dotenv import load_dotenv
from pathlib import Path
load_dotenv()

app = Flask(__name__)
class DBSingleton(object):
    def __new__(cls, DATABASE_URL):
        if not hasattr(cls, "engine"):
            cls.engine = create_engine(DATABASE_URL)
            Sessionmaker = sessionmaker(bind=cls.engine)
            cls.session = Sessionmaker()
        return cls.engine, cls.session

def get_engine_and_session(DATABASE_URL):
    return DBSingleton(DATABASE_URL)

print("Db connection started...")

@app.route('/fetch-sensor-data', methods=['POST'])
def post_sensor_data():
    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        return jsonify({'error': 'Missing DATABASE_URL'}), 500

    session = None
    try:
        payload = request.get_json()
        if not isinstance(payload, list):
            return jsonify({'error': 'Expected a list of sensor data'}), 400

        session = SessionLocal()

        # Use the cached model
        SensorData = get_model_for_table('sensor_data')

        for entry in payload:
            light_max = entry.get('light_max', 0)
            light_min = entry.get('light_min', 0)
            time_since_last = entry.get('time_since_last_watering', 0)
            soil_moisture = entry.get('soil_moisture', 0)

            light_variation = light_max - light_min
            water_need_score = (100 - soil_moisture) * (time_since_last / 24)

            # Create a new SensorData instance
            sensor = SensorData(
                air_temperature=entry.get('air_temperature'),
                air_humidity=entry.get('air_humidity'),
                soil_moisture=soil_moisture,
                light=entry.get('light'),
                light_type=entry.get('light_type'),
                light_max=light_max,
                light_min=light_min,
                artificial_light=entry.get('artificial_light'),
                light_avg=entry.get('light_avg'),
                distance_to_height=entry.get('distance_to_height'),
                water=entry.get('water'),
                time_since_last_watering=time_since_last,
                water_amount=entry.get('water_amount'),
                watering_frequency=entry.get('watering_frequency'),
                timestamp=entry.get('timestamp'),
                soil_type=entry.get('soil_type'),
                fertilizer_type=entry.get('fertilizer_type'),
                experiment_number=entry.get('experiment_number'),
                light_variation=light_variation,
                water_need_score=water_need_score
            )
            session.add(sensor)

        session.commit()
        return jsonify({'status': 'Data saved successfully'}), 201

    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500

    finally:
        if session:
            session.close()
    
@app.route('/fetch-sensor-data', methods=['GET'])
def fetch_sensor_data():
    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        return jsonify({'error': 'Missing DATABASE_URL'}), 500

    session = None
    try:
        session = SessionLocal()

        # Use the cached model
        SensorData = get_model_for_table('sensor_data')

        data = session.query(SensorData).all()
        results = []

        for d in data:
            results.append({
                "id": d.id,
                "air_temperature": d.air_temperature,
                "air_humidity": d.air_humidity,
                "soil_moisture": d.soil_moisture,
                "light": d.light,
                "light_type": d.light_type,
                "light_max": d.light_max,
                "light_min": d.light_min,
                "artificial_light": d.artificial_light,
                "light_avg": d.light_avg,
                "distance_to_height": d.distance_to_height,
                "water": d.water,
                "time_since_last_watering": d.time_since_last_watering,
                "water_amount": d.water_amount,
                "watering_frequency": d.watering_frequency,
                "timestamp": d.timestamp,
                "soil_type": d.soil_type,
                "fertilizer_type": d.fertilizer_type,
                "experiment_number": d.experiment_number,
                "light_variation": d.light_variation,
                "water_need_score": d.water_need_score
            })

        return jsonify(results), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        if session:
            session.close()

#======================== DemoData Endpoints, CRUD  ===========================
@app.route('/DemoDataRaw/<int:id>', methods=['GET'])
def get_single_plant_data(id):
    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        return jsonify({'error': 'Missing DATABASE_URL'}), 500

    session = None
    try:
        #never reached as flask handles negative values 
        if id < 1:
            return jsonify({'error': 'Invalid ID'}), 400

        session = SessionLocal()
        PlantDataTest = create_plant_model('plant_data_test')

        entry = session.get(PlantDataTest, id)
        if entry is None:
            return jsonify({'error': f'Entry with id {id} not found'}), 404

        result = {
            "id": entry.id,
            "soil_type": entry.soil_type,
            "sunlight_hours": entry.sunlight_hours,
            "water_frequency": entry.water_frequency,
            "fertilizer_type": entry.fertilizer_type,
            "temperature": entry.temperature,
            "humidity": entry.humidity,
            "Growth_Milestone": entry.growth_milestone
        }

        return jsonify(result), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        if session:
            session.close()


@app.route('/DemoDataRaw', methods=['GET'])
def get_plant_data():
    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        return jsonify({'error': 'Missing DATABASE_URL'}), 500

    session = None
    try:
        session = SessionLocal()
        PlantDataTest = create_plant_model('plant_data_test')

        data = session.query(PlantDataTest).all()
        results = []

        for d in data:
            results.append({
                "id": d.id,
                "soil_type": d.soil_type,
                "sunlight_hours": d.sunlight_hours,
                "water_frequency": d.water_frequency,
                "fertilizer_type": d.fertilizer_type,
                "temperature": d.temperature,
                "humidity": d.humidity,
                "Growth_Milestone": d.growth_milestone
            })

        return jsonify(results), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        if session:
            session.close()


@app.route('/DemoDataRaw', methods=['POST'])
def add_plant_data():
    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        return jsonify({'error': 'Missing DATABASE_URL'}), 500

    session = None
    try:
        session = SessionLocal()
        PlantDataTest = create_plant_model('plant_data_test')
        data = request.get_json()

        new_entry = PlantDataTest(
            soil_type=data['soil_type'],
            sunlight_hours=data['sunlight_hours'],
            water_frequency=data['water_frequency'],
            fertilizer_type=data['fertilizer_type'],
            temperature=data['temperature'],
            humidity=data['humidity'],
            growth_milestone=data['growth_milestone']
        )

        session.add(new_entry)
        session.commit()

        return jsonify({
            "message": "Data added successfully!",
            "entry_id": new_entry.id
        }), 201

    except Exception as e:
        if session:
            session.rollback()
        return jsonify({'error': str(e)}), 500

    finally:
        if session:
            session.close()


@app.route('/DemoDataRaw/<int:id>', methods=['POST'])
def update_plant_data(id):
    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        return jsonify({'error': 'Missing DATABASE_URL'}), 500

    session = None
    try:
        if id < 1:
            return jsonify({'error': 'Invalid ID'}), 400

        session = SessionLocal()
        PlantDataTest = create_plant_model('plant_data_test')
        data = request.get_json()
         
        print(f"Incoming JSON: {data}")

        # Type checks (same as original)
        if 'soil_type' in data and not isinstance(data['soil_type'], str):
            return jsonify({'error': 'Invalid data type for soil_type'}), 400
        if 'sunlight_hours' in data and (
            not isinstance(data['sunlight_hours'], (int, float)) or isinstance(data['sunlight_hours'], bool)
        ):
            return jsonify({'error': 'Invalid data type for sunlight_hours'}), 400
        if 'water_frequency' in data and not isinstance(data['water_frequency'], str):
            return jsonify({'error': 'Invalid data type for water_frequency'}), 400
        if 'fertilizer_type' in data and not isinstance(data['fertilizer_type'], str):
            return jsonify({'error': 'Invalid data type for fertilizer_type'}), 400
        if 'temperature' in data and (
            not isinstance(data['temperature'], (int, float)) or isinstance(data['temperature'], bool)
        ):
            return jsonify({'error': 'Invalid data type for temperature'}), 400
        if 'humidity' in data and (
            not isinstance(data['humidity'], (int, float)) or isinstance(data['humidity'], bool)
        ):
            return jsonify({'error': 'Invalid data type for humidity'}), 400
        if 'growth_milestone' in data and (
            not isinstance(data['growth_milestone'], int) or isinstance(data['growth_milestone'], bool)
        ):
            return jsonify({'error': 'Invalid data type for growth_milestone'}), 400

        entry = session.get(PlantDataTest, id)
        print(f"Retrieved DB entry before update: {entry}")
        if entry is None:
            return jsonify({'error': f'Entry with id {id} not found'}), 404

        # Apply updates
        entry.soil_type = data.get('soil_type', entry.soil_type)
        entry.sunlight_hours = data.get('sunlight_hours', entry.sunlight_hours)
        entry.water_frequency = data.get('water_frequency', entry.water_frequency)
        entry.fertilizer_type = data.get('fertilizer_type', entry.fertilizer_type)
        entry.temperature = data.get('temperature', entry.temperature)
        entry.humidity = data.get('humidity', entry.humidity)
        entry.growth_milestone = data.get('growth_milestone', entry.growth_milestone)

        session.commit()
        return jsonify({'message': f'Entry with id {id} updated successfully'}), 200

    except Exception as e:
        if session:
            session.rollback()
        return jsonify({'error': str(e)}), 500

    finally:
        if session:
            session.close()
            print("Session closed")


@app.route('/DemoDataRaw/<int:id>', methods=['DELETE'])
def delete_plant_data(id):
    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        return jsonify({'error': 'Missing DATABASE_URL'}), 500

    session = None
    try:
        session = SessionLocal()
        PlantDataTest = create_plant_model('plant_data_test')
        
        entry = session.get(PlantDataTest, id)
        if entry is None:
            return jsonify({'error': f'Entry with id {id} not found'}), 404

        session.delete(entry)
        session.commit()

        return jsonify({'message': f'Entry with id {id} deleted successfully'}), 200

    except Exception as e:
        if session:
            session.rollback()
        return jsonify({'error': str(e)}), 500

    finally:
        if session:
            session.close()


@app.route('/DemoDataRaw/unique-values', methods=['GET'])
def get_unique_plant_data_fields():
    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        return jsonify({'error': 'Missing DATABASE_URL'}), 500

    session = None
    try:
        session = SessionLocal()
        PlantDataTest = create_plant_model('plant_data_test')

        unique_soil_types = [row[0] for row in session.query(distinct(PlantDataTest.soil_type)).all()]
        unique_water_freqs = [row[0] for row in session.query(distinct(PlantDataTest.water_frequency)).all()]
        unique_fertilizers = [row[0] for row in session.query(distinct(PlantDataTest.fertilizer_type)).all()]

        return jsonify({
            "soil_types": unique_soil_types,
            "water_frequencies": unique_water_freqs,
            "fertilizer_types": unique_fertilizers
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        if session:
            session.close()

#======================== Preprocess Endpoint  ===========================


@app.route('/preprocess', methods=['POST'])
def preprocess_data():
    try:
        payload = request.get_json()

        copy_from = payload.get('CopyFrom')
        copy_to = payload.get('CopyTo')

        if not copy_from or not copy_to:
            return jsonify({'error': 'Both CopyFrom and CopyTo table names must be provided.'}), 400

        # Dynamically create models from table names
        #wrong needs to be refactored
        PlantModel = create_plant_model(copy_from)
        PlantPreprocessed = create_preprocessed_plant_model(copy_to)
        
        #Check if tables exist
        PlantModel.__table__.create(db.engine, checkfirst=True)
        PlantPreprocessed.__table__.create(db.engine, checkfirst=True)


        # Fetch all rows from the source table
        original_data = db.session.query(PlantModel).all()

        if not original_data:
            return jsonify({'message': 'No records found in source table.', 'records_transferred': 0}), 200

        # Calculate column averages once
        averages = calculate_column_averages(db, PlantModel, ['sunlight_hours', 'temperature', 'humidity'])

        transferred_count = 0

        for row in original_data:
            encoded_values = one_hot_encode_columns(row)
            copy_to_preprocessed(row, encoded_values, averages, db, PlantPreprocessed)
            transferred_count += 1

        return jsonify({
            "message": "Data successfully piped.",
            "records_transferred": transferred_count,
            "copied_from": copy_from,
            "copied_to": copy_to,
            "averages": averages
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get-tables', methods=['GET'])
def get_tables():
    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        return jsonify({'error': 'Missing DATABASE_URL'}), 500
    session = None
    try:
        engine, session = get_engine_and_session(DATABASE_URL)
        ins = inspect(engine)
        tables = ins.get_table_names()
        # Remove system table
        tables.remove('spatial_ref_sys')
        return jsonify(tables), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    #app = create_app()
    app.run(host='0.0.0.0', port=5000)
