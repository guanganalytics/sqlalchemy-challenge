# Import the dependencies.

import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask,jsonify
import datetime as dt
#################################################
# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
#################################################

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement = Base.classes.measurement
station=Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app=Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")      
def welcome():
    return(f"Welcome!<br/>" 
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
        f"Please enter the start date/end date in the format of MMDDYYYY"
            )

@app.route("/api/v1.0/precipitation")
def precipitation_analysis():
    lastyear=dt.date(2017,8,23)-dt.timedelta(days=365)
    sel = [measurement.date,measurement.prcp]
    measurement_precipitation = session.query(*sel).filter(measurement.date>=lastyear).all()
    session.close()
    precipitation_dictionary={}
    for date,prcp in measurement_precipitation:
        precipitation_dictionary[date]=prcp
    return jsonify(precipitation_dictionary)

@app.route("/api/v1.0/stations")
def station_analysis():
    station_list=session.query(station.station).all()
    session.close()
    stations = list(np.ravel(station_list))
    return jsonify(stations=stations)
   

@app.route("/api/v1.0/tobs")
def tobs_analysis():
    lastyear=dt.date(2017,8,23)-dt.timedelta(days=365)
    sel = [measurement.station,measurement.tobs]
    most_active=session.query(measurement.station).group_by(measurement.station).order_by(func.count(measurement.station).desc()).first()[0]
    tobs=session.query(measurement.tobs).filter(measurement.station==most_active).filter(measurement.date>=lastyear).all()
    session.close()
    tobs = list(np.ravel(tobs))
    return jsonify(tobs=tobs)


@app.route("/api/v1.0/<start>")
def start_analysis(start):
    startdate_entered=dt.datetime.strptime(start,"%m%d%Y")
    startdate=session.query(func.min(measurement.tobs),func.max(measurement.tobs),func.avg(measurement.tobs)).filter(measurement.date>=startdate_entered).all()
    session.close()
    startlist= list(np.ravel(startdate))
    return jsonify(startlist=startlist)

@app.route("/api/v1.0/<start>/<end>")
def start_end_analysis(start,end):
    startdate_entered=dt.datetime.strptime(start,"%m%d%Y")
    enddate_entered=dt.datetime.strptime(end,"%m%d%Y")
    start_end=session.query(func.min(measurement.tobs),func.max(measurement.tobs),func.avg(measurement.tobs)).filter(measurement.date>=startdate_entered).filter(measurement.date<=enddate_entered).all()
    session.close()
    start_end= list(np.ravel(start_end))
    return jsonify(start_end=start_end)

if __name__=="__main__":
    app.run()