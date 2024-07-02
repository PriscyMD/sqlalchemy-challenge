# Import the dependencies.
from flask import Flask, jsonify
import numpy as np
import sqlalchemy
import datetime as dt
from datetime import date, timedelta
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, text

#################################################
# Database Setup
#################################################
engine = create_engine(f"sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask (__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def homepage():
    return ('''
    <h1>Welcome to Home Page</h1>
    <h3>List of available routes:</h3>
    <ul>
        <li> <ahref="/api/v1.0/precipitation"> /api/v1.0/precipitation </a> </li>
        <li> <ahref="/api/v1.0/stations"> /api/v1.0/stations </a> </li>
        <li> <ahref="/api/v1.0/tobs"> /api/v1.0/tobs </a> </li>
            
        <li> /api/v1.0/&lt;start&gt;</li>
        <li> /api/v1.0/&lt;start&gt;/&lt;end&gt;</li>
    </ul>
    ''')

@app.route("/api/v1.0/precipitation")
def precipitation():
    with Session(engine) as session:
        recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
        recent_db = dt.datetime.strptime(recent_date, '%Y-%m-%d')
        last_year_db = recent_db - timedelta(days=365)
        result_precipitation = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= last_year_db).all()
        precipitation = {row.date: row.prcp for row in result_precipitation}
    return jsonify(precipitation)


@app.route("/api/v1.0/stations")
def stations():
    query = text("SELECT station FROM station")
    with Session(engine) as session:
        result_stations = session.execute(query)
        stations = [row.station for row in result_stations]
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    with Session(engine) as session:
        active_stations = session.query(Measurement.station, func.count(Measurement.station).label('count')).\
            group_by(Measurement.station).\
            order_by(func.count(Measurement.station).desc()).\
            all()
        active_station_id = active_stations[0].station
        recent_date = session.query(func.max(Measurement.date)).scalar()
        recent_db = dt.datetime.strptime(recent_date, '%Y-%m-%d')
        last_year_db = recent_db - dt.timedelta(days=365)
        tobs_result = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == active_station_id).\
                        filter(Measurement.date >= last_year_db).all()
        tobs = {row.date: row.tobs for row in tobs_result}
    return jsonify(tobs)

@app.route("/api/v1.0/<start>")
def start(start):
    with Session(engine) as session:
        start_date = dt.datetime.strptime(start, "%Y-%m-%d").date()
        result = session.query(func.min(Measurement.tobs), 
                              func.avg(Measurement.tobs), 
                              func.max(Measurement.tobs)).filter(Measurement.date >= start_date).all()
        temps = list(result[0])
    return jsonify(temps)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    with Session(engine) as session:
        start_date = dt.datetime.strptime(start, "%Y-%m-%d").date()
        end_date = dt.datetime.strptime(end, "%Y-%m-%d").date()
        result =session.query(func.min(Measurement.tobs), 
                              func.avg(Measurement.tobs), 
                              func.max(Measurement.tobs)).filter(Measurement.date >= start_date)\
                                                         .filter(Measurement.date <= end_date).all()
        temps = list(result[0])
    return jsonify(temps)

if __name__=='main':
    app.run(debug=True)