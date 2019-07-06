#import datetime as dt
from datetime import datetime as dt
from datetime import timedelta
#from dateutil.relativedelta import relativedelta
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine('sqlite:///3/Practice/hawaii.sqlite', connect_args={'check_same_thread': False})

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create session from Python to the DB
session = Session(engine)

#################################################
# Set up Flask and landing page
#################################################
app = Flask(__name__)


@app.route("/")
def welcome():
    return (
        f"<center><h1>Welcome to Hawaii Climate Analysis and Exploration!</h1><br/><br/></center>"
        f"<h2><b>All available Routes:</b></h2><br/>"
        f"<h3><b>1. Return a JSON representation of dictionary using `date` as the key and `prcp` as the value for prior 12months from last available date</b></h3>"
        f"<h3>/api/v1.0/precipitation</h3><br/></br>"
        f"<h3><b>2. Return a JSON list of stations from the dataset.</b></h3>"
        f"<h3>/api/v1.0/stations<h3><br/></br>"
        f"<h3><b>3. Return a JSON representation of dictionary using `date` as the key and `Temperature` as the value for prior 12months from last available date</b></h3>"
        f"<h3>/api/v1.0/tobs<h3><br/></br>"
        f"<h3><b>4.`TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date. For specific start date, enter the required date. Eg: ""/api/v1.0/2016-01-01"" </b></h3>"
        f"<h3>/api/v1.0/date<h3><br/></br>"
        f"<h3><b>5.`TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive. For specific start date and end date, enter the required date. Eg: ""/api/v1.0/2014-01-01/2017-03-01"" </b></h3>"
        f"<h3>/api/v1.0/start_date/end_date<h3><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
     #Convert the query results to a Dictionary using `date` as the key and `prcp` as the value.
     #Return the JSON representation of your dictionary.
 
    maxDate = max(session.query(Measurement.date).all())
    days_to_subtract = 365
    SD = dt.strptime(maxDate[0],'%Y-%m-%d') - timedelta(days=days_to_subtract)
    SD = SD.strftime('%Y-%m-%d')
    Last12MonthPPTList = session.query(Measurement.date,Measurement.prcp).filter(Measurement.date >= SD).all()
    Last12MonthPPTDict = dict()
    [Last12MonthPPTDict [t [0]].append(t [1]) if t [0] in list(Last12MonthPPTDict.keys()) 
    else Last12MonthPPTDict.update({t [0]: [t [1]]}) for t in Last12MonthPPTList]
    return jsonify(Last12MonthPPTDict)


# /api/v1.0/stations
# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    s_results = session.query(Station.station, Station.name).all()
    return jsonify(s_results)


# /api/v1.0/tobs
# query for the dates and temperature observations from a year from the last data point.
# Return a JSON list of Temperature Observations (tobs) for the previous year.
@app.route("/api/v1.0/tobs")
def tobs():
   Last12MonthTempQuery = "select date, tobs from Measurement \
             where date > (select date((select max(date) from Measurement),'-12 month')) \
             order by date"
   Last12MonthTempList = pd.read_sql_query(Last12MonthTempQuery, engine)
   Last12MonthTempList = [tuple(x) for x in Last12MonthTempList.values]

   Last12MonthTempDict = dict()
   [Last12MonthTempDict [t [0]].append(t [1]) if t [0] in list(Last12MonthTempDict.keys()) 
   else Last12MonthTempDict.update({t [0]: [t [1]]}) for t in Last12MonthTempList]
   return jsonify(Last12MonthTempDict)


# /api/v1.0/<start>
# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date
# When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive.
@app.route("/api/v1.0/<date>")
def startDateOnly(date):
     TempStatQ = "select date, min(tobs) as MinTemp, avg(tobs) as AvgTemp, max(tobs) as MaxTemp \
               from Measurement where date >= '" + date + "' group by date"
     TempStatList = pd.read_sql_query(TempStatQ, engine)
     TempStatList = [tuple(x) for x in TempStatList.values]
     TempStatDict = {}
     for i in TempStatList:
          case = {'minT': i[1], 'avgT': i[2], 'maxT':i[3] }
          TempStatDict[i[0]] = case


     
     return jsonify(TempStatDict)


# /api/v1.0/<start>/<end>
# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date
# When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive.

@app.route("/api/v1.0/<start>/<end>")
def startDateEndDate(start,end):
     TempStatQ = "select date, min(tobs) as MinTemp, avg(tobs) as AvgTemp, max(tobs) as MaxTemp \
               from Measurement where date >= '" + start + "' and \
               date <='" + end + "' group by date"
     TempStatList = pd.read_sql_query(TempStatQ, engine)
     TempStatList = [tuple(x) for x in TempStatList.values]
     TempStatDict = {}
     for i in TempStatList:
          case = {'minT': i[1], 'avgT': i[2], 'maxT':i[3] }
          TempStatDict[i[0]] = case
     return jsonify(TempStatDict)

if __name__ == "__main__":
    app.run(debug=True)