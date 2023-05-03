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
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
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
    # Create our session (link) from Python to the DB
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
    return "Coming soon."


@app.route("/api/v1.0/<start>")
def start():
    return "Coming soon."


@app.route("/api/v1.0/<start>/<end>")
def start_end():
    return "Coming soon."


if __name__ == '__main__':
    app.run(debug=True)
