import numpy as np
import pandas as pd
import sqlalchemy
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

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
        f"<a href='/api/v1.0/precipitation'>Precipitation data for last year in database</a><br/>"
        f"<a href='/api/v1.0/stations'>All stations in the database</a><br/>"
        f"<a href='/api/v1.0/tobs'>Most active station for last year of temperature data</a><br/>"
        f"<a href='/api/v1.0/<start>'>Enter start date for min, max, and avg temperatures between start date and last date</a><br/>"
        f"<a href='/api/v1.0/<start>/<end>'>Enter start date and end date for min, max, and avg temperatures between the two dates</a><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the date and tobs columns from the Measurement table for the last year in the dataset
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= '2016-08-23').all()
    
    session.close()

    return jsonify(results)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the station name from the Station table
    results = session.query(Station.name).all()

    session.close()

    # Convert list of tuples into normal list
    all_results = list(np.ravel(results))

    return jsonify(all_results)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the date and tobs columns from the Measurement table for most active station and the last year of data
    results = session.query(Measurement.station, Measurement.date, Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= '2016-08-23').all()
    
    session.close()

    return jsonify(results)


@app.route("/api/v1.0/<start>")
def start(start):

    session = Session(engine)

    # Create query to retrieve all dates
    dates = session.query(Measurement.date).all()

    #Create loop to format strings as parsed dates
    parsed_dates = []

    for date in dates:
        temp = str(date)
        temp = temp.replace('(', '')
        temp = temp.replace(')', '')
        temp = temp.replace(',', '')
        temp = temp.replace("'", '')
        parsed_date = dt.datetime.strptime(temp, '%Y-%m-%d')
        parsed_dates.append(parsed_date)

    # Create query to retrieve all temperature scores
    tobs = session.query(Measurement.tobs).all()

    # Create loop to format strings as parsed prcps
    parsed_tobs = []

    for tob in tobs:
        temp = str(tob)
        temp = temp.replace('(', '')
        temp = temp.replace(')', '')
        temp = temp.replace(',', '')
        temp = temp.replace('None', '')
        parsed_tobs.append(temp)

    # Convert prcp to float (user: SilentGhost)
    # (url: https://stackoverflow.com/questions/1614236/in-python-how-do-i-convert-all-of-the-items-in-a-list-to-floats)
    final_tobs = [float(i) for i in parsed_tobs]
    final_tobs

    # Create dataframe from parsed lists
    measurement_df = pd.DataFrame({'Date': parsed_dates, 'Temp': final_tobs})
    measurement_df

    results = measurement_df[(measurement_df['Date'] >= start)]

    dates_json = len(results['Date'])
    min_json = min(results['Temp'])
    avg_json = sum(results['Temp'])/len(results['Temp'])
    max_json = max(results['Temp'])

    session.close()

    # Create a dictionary from the results
    item_dict = {'measurements': dates_json, 'min_temp': min_json, 'avg_temp': avg_json, 'max_temp': max_json}

    return jsonify(item_dict)



@app.route("/api/v1.0/<start>/<end>")
def end(start, end):

    session = Session(engine)

    # Create query to retrieve all dates
    dates = session.query(Measurement.date).all()

    #Create loop to format strings as parsed dates
    parsed_dates = []

    for date in dates:
        temp = str(date)
        temp = temp.replace('(', '')
        temp = temp.replace(')', '')
        temp = temp.replace(',', '')
        temp = temp.replace("'", '')
        parsed_date = dt.datetime.strptime(temp, '%Y-%m-%d')
        parsed_dates.append(parsed_date)

    # Create query to retrieve all temperature scores
    tobs = session.query(Measurement.tobs).all()

    # Create loop to format strings as parsed prcps
    parsed_tobs = []

    for tob in tobs:
        temp = str(tob)
        temp = temp.replace('(', '')
        temp = temp.replace(')', '')
        temp = temp.replace(',', '')
        temp = temp.replace('None', '')
        parsed_tobs.append(temp)

    # Convert prcp to float (user: SilentGhost)
    # (url: https://stackoverflow.com/questions/1614236/in-python-how-do-i-convert-all-of-the-items-in-a-list-to-floats)
    final_tobs = [float(i) for i in parsed_tobs]
    final_tobs

    # Create dataframe from parsed lists
    measurement_df = pd.DataFrame({'Date': parsed_dates, 'Temp': final_tobs})
    measurement_df

    results = measurement_df[(measurement_df['Date'] >= start) & (measurement_df['Date'] <= end)]

    dates_json = len(results['Date'])
    min_json = min(results['Temp'])
    avg_json = sum(results['Temp'])/len(results['Temp'])
    max_json = max(results['Temp'])

    session.close()

    # Create a dictionary from the results
    item_dict = {'measurements': dates_json, 'min_temp': min_json, 'avg_temp': avg_json, 'max_temp': max_json}

    return jsonify(item_dict)


if __name__ == '__main__':
    app.run(debug=True)
