# import dependencies
import numpy as np
import pandas as pd
import datetime as dt
from dateutil.relativedelta import relativedelta 

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################

database_path = 'Resources/hawaii.sqlite'
engine = create_engine(f'sqlite:///{database_path}')

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# create our session (link) from Python to the DB
session = Session(bind=engine)


#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&#60;start&#62;<br/>"
        f"/api/v1.0/&#60;start&#62;/&#60;end&#62;<br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # create a session (link) from Python to the SQLite database
    session = Session(engine)

    """Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data)
    to a dictionary using date as the key and prcp as the value. Return the JSON representation of your dictionary."""
    
    # find most recent date and date one year prior
    most_recent = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    prev_year = (dt.datetime.strptime(most_recent, '%Y-%m-%d') - relativedelta(years=1)).strftime('%Y-%m-%d')
    
    # perform a query to retrieve the data and precipitation scores
    prcp_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= prev_year).\
        order_by(Measurement.date).all()

    session.close()
    
    # construct a dictionary that holds dates as keys and precipitation measurements as values
    prcp_dict = {}
    for date, prcp in prcp_data:
        prcp_dict[date] = prcp

    return jsonify(prcp_dict)


@app.route("/api/v1.0/stations")
def stations():
    # create a session (link) from Python to the SQLite database
    session = Session(engine)

    """Return a JSON list of stations from the dataset."""
    station_data = session.query(Station.station,
                                 Station.name,
                                 Station.latitude,
                                 Station.longitude,
                                 Station.elevation).all()

    session.close()

    # create a dictionary from each row of data and append to a list of all stations
    all_stations = []
    for st, n, lat, lon, ele in station_data:
        
        station_dict = {}
        station_dict["station"] = st
        station_dict["name"] = n
        station_dict["latitude"] = lat
        station_dict["longitude"] = lon
        station_dict["elevation"] = ele
        
        all_stations.append(station_dict)

    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def tobs():
    # create a session (link) from Python to the SQLite database
    session = Session(engine)
    
    """Query the dates and temperature observations of the most-active station for the previous year of data.
    Return a JSON list of temperature observations for the previous year."""
    most_active_station = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).first()[0]
    
    most_recent = session.query(Measurement.date).\
        filter(Measurement.station == most_active_station).\
        order_by(Measurement.date.desc()).first()[0]
    
    starting_point = (dt.datetime.strptime(most_recent, '%Y-%m-%d') - relativedelta(years=1)).strftime('%Y-%m-%d')
    
    tobs_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station).\
        filter(Measurement.date >= starting_point).all()
    
    session.close()
    
    # create a dictionary from each row of data and append to a list of all stations
    all_tobs = []
    for d, t in tobs_data:
        
        tobs_dict = {}
        tobs_dict["date"] = d
        tobs_dict["temperature"] = t
        
        all_tobs.append(tobs_dict)

    return jsonify(all_tobs)


@app.route("/api/v1.0/<start>")
def start(start):
    # create a session (link) from Python to the SQLite database
    session = Session(engine)
    
    """Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start.
    Calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date."""
    
    session.close()
    
    return f"{start}"


@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    # create a session (link) from Python to the SQLite database
    session = Session(engine)
    
    """Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start-end range.
    Calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive."""
    
    session.close()
    
    return f"{start} and {end}."


if __name__ == '__main__':
    app.run(debug=True)
