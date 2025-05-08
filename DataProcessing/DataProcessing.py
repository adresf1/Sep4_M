#!/usr/bin/env python
# coding: utf-8


from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import scoped_session, sessionmaker
import math
import os
from dotenv import load_dotenv
load_dotenv()
from DemoData import create_plant_model, calculate_column_averages, create_preprocessed_plant_model, one_hot_encode_columns, copy_to_preprocessed
from sqlalchemy import distinct

app = Flask(__name__)
print("Starting app...")
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

print("Db connection started...")

class SensorData(db.Model):
    __tablename__ = 'sensor_data'

    id = db.Column(db.Integer, primary_key=True)
    air_temperature = db.Column(db.Float)
    air_humidity = db.Column(db.Float)
    soil_moisture = db.Column(db.Float)
    light = db.Column(db.Float)
    light_type = db.Column(db.String)
    light_max = db.Column(db.Float)
    light_min = db.Column(db.Float)
    artificial_light = db.Column(db.Boolean)
    light_avg = db.Column(db.Float)
    distance_to_height = db.Column(db.Float)
    water = db.Column(db.Float)
    time_since_last_watering = db.Column(db.Float)
    water_amount = db.Column(db.Float)
    watering_frequency = db.Column(db.Float)
    timestamp = db.Column(db.String)
    soil_type = db.Column(db.String)
    fertilizer_type = db.Column(db.String)
    experiment_number = db.Column(db.Integer)
    
    # Calculated figures
    light_variation = db.Column(db.Float)
    water_need_score = db.Column(db.Float)

with app.app_context():
    db.create_all()


@app.route('/fetch-sensor-data', methods=['POST'])
def post_sensor_data():
    try:
        data = request.get_json()

        if not isinstance(data, list):
            return jsonify({'error': 'Expected a list of sensor data'}), 400

        for entry in data:
            # Beregninger:
            light_max = entry.get('light_max', 0)
            light_min = entry.get('light_min', 0)
            time_since_last = entry.get('time_since_last_watering', 0)
            soil_moisture = entry.get('soil_moisture', 0)

            light_variation = light_max - light_min
            water_need_score = (100 - soil_moisture) * (time_since_last / 24)

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

            db.session.add(sensor)

        db.session.commit()
        return jsonify({'status': 'Data saved successfully'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/fetch-sensor-data', methods=['GET'])
def fetch_sensor_data():
    try:
        data = SensorData.query.all()
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

@app.route('/DemoDataRaw', methods=['GET'])
def get_plant_data():
    try:
        PlantDataTest = create_plant_model('plant_data_test')
        data = db.session.query(PlantDataTest).all()
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

@app.route('/DemoDataRaw', methods=['POST'])
def add_plant_data():
    try:
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

        db.session.add(new_entry)
        db.session.commit()

        return jsonify({
            "message": "Data added successfully!",
            "entry_id": new_entry.id
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/DemoDataRaw/<int:id>', methods=['DELETE'])
def delete_plant_data(id):
    try:
        PlantDataTest = create_plant_model('plant_data_test')
        
        # Find the entry by ID
        entry = db.session.get(PlantDataTest, id)

        if entry is None:
            return jsonify({'error': f'Entry with id {id} not found'}), 404

        db.session.delete(entry)
        db.session.commit()

        return jsonify({'message': f'Entry with id {id} deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/DemoDataRaw/unique-values', methods=['GET'])
def get_unique_plant_data_fields():
    try:
        PlantDataTest = create_plant_model('plant_data_test')

        unique_soil_types = [row[0] for row in db.session.query(distinct(PlantDataTest.soil_type)).all()]
        unique_water_freqs = [row[0] for row in db.session.query(distinct(PlantDataTest.water_frequency)).all()]
        unique_fertilizers = [row[0] for row in db.session.query(distinct(PlantDataTest.fertilizer_type)).all()]

        return jsonify({
            "soil_types": unique_soil_types,
            "water_frequencies": unique_water_freqs,
            "fertilizer_types": unique_fertilizers
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/preprocess', methods=['POST'])
def preprocess_data():
    try:
        payload = request.get_json()

        copy_from = payload.get('CopyFrom')
        copy_to = payload.get('CopyTo')

        if not copy_from or not copy_to:
            return jsonify({'error': 'Both CopyFrom and CopyTo table names must be provided.'}), 400

        # Dynamically create models from table names
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
