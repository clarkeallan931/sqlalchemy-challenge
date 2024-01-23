# Import the dependencies.
import flask 
import numpy as np
from flask import Flask 
from flask import jsonify 
from datetime import date 
import sqlalchemy 
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import func
from sqlalchemy.orm import Session
import sqlite3
from sqlalchemy import inspect 
import datetime
import datetime


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model

Base = automap_base()

Base.prepare(autoload_with = engine)

# reflect the tables

station = Base.classes.station
measurement = Base.classes.measurement

session = Session(bind = engine)

# Save references to each table


# Create our session (link) from Python to the DB


#################################################
# Flask Setup
#################################################
app = Flask(__name__)


@app.route("/")
def homepage(): 
    return (

        f"Available Routes: </br>"
        f"/api/v1.0/precipitation <br/>"
        f"/api/v1.0/stations <br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start <br/>"
        f"api/v1.0/start/end"
    )



@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    results = session.query(measurement.date, measurement.prcp).filter(measurement.date>='2016-08-23').all()  #filtering by year
    session.close()
    lastyear = [] #creating the dictioary that displays on the link
    for date,prcp in results:
        dict = {}
        dict['date']=date
        dict['precipitation']=prcp
        lastyear.append(dict)

    return jsonify(lastyear)



@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(station.station).all()
    session.close()
    stations = list(np.ravel(results)) #making sure the list displays 
    return jsonify(stations)


@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    results = session.query(measurement.date,measurement.tobs).filter(measurement.station == station.station).filter(measurement.date >= '2016-08-23').filter(station.station == 'USC00519281').all() 
    #filtering by last year and most active station
    session.close()
    temps = []
    for date,tobs in results: #creating dict to display
        dict = {}
        dict['date'] = date
        dict['temp'] = tobs
        temps.append(dict)
    return jsonify(temps)


@app.route("/api/v1.0/<start>")
#to work format is (YYYYMMDD) on search bar 
def startdate(start):
    dateformatsearch = datetime.datetime.strptime(start,'%Y%m%d').date().isoformat() #ensuring the entry is converted to the right format 
    session = Session(engine)
    dates = session.query(measurement.date,measurement.tobs).filter(measurement.station == station.station).filter(measurement.date >= '2016-08-23').all()
    #filtering by date
    session.close()
    templist = []
    finallist = []
    for date,tobs in dates: #extracting date and temp data into a dict
        dict = {}
        dict['Date'] = date
        dict['Temp'] = tobs
        templist.append(dict)
    for temp in templist: #making sure that the date that was entered is in the list I created (doing this by looping throught the list)
        if temp['Date'] == dateformatsearch:
            #if that statement is true I am calling the querty 
            results = session.query(measurement.date,func.max(measurement.tobs), func.min(measurement.tobs), func.avg(measurement.tobs)).filter(measurement.station == station.station).filter(measurement.date >= dateformatsearch).group_by(measurement.date).order_by(measurement.date).all()
            for date,max, min, avg in results:
                #dictionary that will display from the query
                final = {}
                final['Date']= date
                final['Max'] = max
                final['Min'] = min
                final['Average'] = avg
                finallist.append(final)
            return jsonify(finallist)
            
    else:
        return jsonify("Could not find date")
        
    

@app.route("/api/v1.0/<start>/<end>")
#for <start> and <end> search format that worked was (YYYYMMDD)  
def startend(start,end):
    dateformatstart = datetime.datetime.strptime(start,'%Y%m%d').date().isoformat() #used this to convery to the date format 
    dateformatend = datetime.datetime.strptime(end,'%Y%m%d').date().isoformat()
    session = Session(engine)
    dates = session.query(measurement.date,measurement.tobs).filter(measurement.station == station.station).filter(measurement.date >= '2016-08-23').all()
    #filtering by date 
    session.close()
    templist = []
    finallist = []
    for date,tobs in dates:
        #dictionary to compare to search 
        dict = {}
        dict['Date'] = date
        dict['Temp'] = tobs
        templist.append(dict)
    for temp in templist:
        if dateformatstart and dateformatend in temp['Date']:
            #adding less that the dateformatend date to the querty 
            results = session.query(measurement.date,func.max(measurement.tobs), func.min(measurement.tobs),func.avg(measurement.tobs)).filter(measurement.station == station.station).filter(measurement.date >= dateformatstart).filter(measurement.date <= dateformatend).group_by(measurement.date).order_by(measurement.date).all()
            for date, max, min, avg in results:
                #creating the dictionary that displays based on the session query
                final = {}
                final['Date']= date
                final['Max'] = max
                final['Min'] = min
                final['Average']=avg
                finallist.append(final)
            return jsonify(finallist)
    else:
        return jsonify("Could not find date")


#################################################
# Flask Routes
###############################################



if __name__ =='__main__':
    app.run(debug = True)