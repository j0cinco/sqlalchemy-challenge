# Import Flask
from flask import Flask, jsonify

# Import the dependencies.
from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime as dt

# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect, func

# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

#################################################
# Database Setup
#################################################


# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB


#################################################
# Flask Setup
#################################################
app = Flask(__name__)




#################################################
# Flask Routes
#################################################

# 1. Listing Routes
@app.route("/")
def home():
    return(
        f"Available Routes:<br/>"
        f"Precipitation: /api/v1.0/precipitation<br/>"
        f"Stations: /api/v1.0/stations<br/>"
        f"Temperature for one year: /api/v1.0/tobs<br/>"
        f"Temperature statistics from the start date (enter date as: yyyy-mm-dd): /api/v1.0/start<br/>"
        f"Temperature statistics from start to end dates (enter date as: yyyy-mm-dd/yyyy-mm-dd): /api/v1.0/start/end"
    )

# 2. What happens if /api/v1.0/precipitation route is selected
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Find the most recent date in the data set.
    recent_date = session.query(measurement.date).order_by(measurement.date.desc()).first()[0]
    # Starting from the most recent data point in the database.
    conv_recent_date = dt.datetime.strptime(recent_date, '%Y-%m-%d').date()
    # Calculate the date one year from the last date in data set.
    one_year = conv_recent_date - dt.timedelta(days=365)
    # Perform a query to retrieve the data and precipitation scores
    sel = [measurement.date, measurement.prcp]
    query_result = session.query(*sel).filter(measurement.date <= conv_recent_date).filter(measurement.date > one_year).all()    
    session.close()

    # jsonify
    precipitation = []
    for date, prcp in query_result:
            prcp_dict = {}
            prcp_dict["Date"] = date
            prcp_dict["Precipitation"] = prcp
            precipitation.append(prcp_dict)
    return jsonify(precipitation)


# 3. What happens if /api/v1.0/stations route is selected
@app.route("/api/v1.0/stations")
def stations():
    station = Base.classes.station
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Design a query to find the most active stations (i.e. what stations have the most rows?)
    station_list_query = session.query(measurement.station, station.name, func.count(measurement.station)).\
    group_by(measurement.station).\
    order_by(func.count(measurement.station).desc()).all()
    session.close()

    # jsonify
    stations_list = []
    for station, name, count in station_list_query:
         stations_dict = {}
         stations_dict['station'] = station
         stations_dict['name'] = name
         stations_dict['count'] = count
         stations_list.append(stations_dict)
    return jsonify(stations_list)


# 4.  What happens if /api/v1.0/tobs route is selected
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    # Design a query to find the most active stations (i.e. what stations have the most rows?)
    active_stations = session.query(measurement.station, func.count(measurement.station)).\
    group_by(measurement.station).\
    order_by(func.count(measurement.station).desc()).all()
    # Using the most active station id from the previous query, calculate the lowest, highest, and average temperature.
    most_active = active_stations[0][0]
    # Find the most recent date in the data set.
    recent_date = session.query(measurement.date).order_by(measurement.date.desc()).first()[0]
    # Starting from the most recent data point in the database.
    conv_recent_date = dt.datetime.strptime(recent_date, '%Y-%m-%d').date()
    # Calculate the date one year from the last date in data set.
    one_year = conv_recent_date - dt.timedelta(days=365)
    # Query the last 12 months of temperature observation data for this station and plot the results as a histogram
    tobs_query = session.query(measurement.date, measurement.tobs).order_by(measurement.date.desc()).\
    filter(measurement.station == most_active).\
    filter(measurement.date <= conv_recent_date).\
    filter(measurement.date > one_year).all()    
    session.close()

    # jsonify
    tobs_list = []
    for date, tobs in tobs_query:
         tobs_dict = {}
         tobs_dict['date'] = date
         tobs_dict['tobs'] = tobs
         tobs_list.append(tobs_dict)
    return jsonify(tobs_list)


# 5. What happens if /api/v1.0/<start> route is selected
@app.route("/api/v1.0/<start>")
def start_date(start):
    session = Session(engine)
    # Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.
    # For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.
    start_tobs_query  = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date >= start).all()
    session.close()

    # jsonify
    start_tobs_list = []
    for min, avg, max in start_tobs_query:
        start_tobs_dict = {}
        start_tobs_dict['min'] = min
        start_tobs_dict['avg'] = avg
        start_tobs_dict['max'] = max
        start_tobs_list.append(start_tobs_dict)
    return jsonify(start_tobs_list)


# 6. What happens if /api/v1.0/<start>/<end> route is selected
@app.route("/api/v1.0/<start>/<end>")
def end(start, end):
    session = Session(engine)
    # Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.
    # For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.
    start_end_tobs_query  = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).\
        filter(measurement.date <=end).all()
    session.close()

    # jsonify
    start_end_tobs_list = []
    for min, avg, max in start_end_tobs_query:
        start_end_tobs_dict = {}
        start_end_tobs_dict['min'] = min
        start_end_tobs_dict['avg'] = avg
        start_end_tobs_dict['max'] = max
        start_end_tobs_list.append(start_end_tobs_dict)
    return jsonify(start_end_tobs_list)

if __name__ == "__main__":
    app.run(debug=True)