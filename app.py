# Import the dependencies.

import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from datetime import datetime, timedelta
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model

Base = automap_base()

# reflect the tables

Base.prepare(autoload_with=engine)

# Save references to each table

Measurement = Base.classes.measurement

Station = Base.classes.station


# Create our session (link) from Python to the DB

from sqlalchemy.orm import sessionmaker 

Session = sessionmaker(bind=engine)
session = Session()

#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route('/')
def home():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/temperatures<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )

@app.route('/api/v1.0/precipitation')
def precipitation():
    end_date = session.query(func.max(Measurement.date)).scalar()
    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    start_date = end_date - timedelta(days=365)

    precipitation_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= start_date).\
        order_by(Measurement.date).all()

    precipitation_dict = {date: prcp for date, prcp in precipitation_data}

    return jsonify(precipitation_dict)

@app.route('/api/v1.0/stations')
def stations():
    stations_data = session.query(Station.station, Station.name).all()

    if not stations_data:
        return jsonify({"error": "No stations found"}), 404

    stations_list = [{'station_id': station[0], 'name': station[1]} for station in stations_data]

    return jsonify(stations_list)

@app.route('/api/v1.0/tobs')
def tobs():
    most_active_station = 'USC00519281'
    end_date = session.query(func.max(Measurement.date)).scalar()
    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    start_date = end_date - timedelta(days=365)

    tobs_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station).\
        filter(Measurement.date >= start_date).\
        order_by(Measurement.date).all()

    tobs_list = [{'date': date, 'temperature': temperature} for date, temperature in tobs_data]

    return jsonify(tobs_list)

@app.route('/api/v1.0/<start>')
def start(start):
    try:
        results = session.query(
            func.min(Measurement.tobs),
            func.avg(Measurement.tobs),
            func.max(Measurement.tobs)
        ).filter(Measurement.date >= start).all()

        if not results or results[0][0] is None:
            return jsonify({"error": "No data found for the given start date."}), 404

        temperature_stats = {
            'Start Date': start,
            'TMIN': results[0][0],
            'TAVG': results[0][1],
            'TMAX': results[0][2]
        }

        return jsonify(temperature_stats)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1.0/<start>/<end>')
def start_end(start, end):
    try:
        results = session.query(
            func.min(Measurement.tobs),
            func.avg(Measurement.tobs),
            func.max(Measurement.tobs)
        ).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

        if not results or results[0][0] is None:
            return jsonify({"error": "No data found for the given date range."}), 404

        temperature_stats = {
            'Start Date': start,
            'End Date': end,
            'TMIN': results[0][0],
            'TAVG': results[0][1],
            'TMAX': results[0][2]
        }

        return jsonify(temperature_stats)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1.0/tobs_with_stations')
def tobs_with_stations():
   
    end_date = session.query(func.max(Measurement.date)).scalar()
    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    start_date = end_date - timedelta(days=365)

    results = session.query(Measurement.date, Measurement.tobs, Station.name).\
        join(Station, Measurement.station == Station.station).\
        filter(Measurement.date >= start_date).\
        order_by(Measurement.date).all()

    tobs_list = [{'date': date, 'temperature': temperature, 'station': station_name} 
                  for date, temperature, station_name in results]

    return jsonify(tobs_list)

if __name__ == '__main__':
    app.run(debug=True)