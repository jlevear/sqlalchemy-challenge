import numpy as np

import numpy as np
import pandas as pd
import sqlalchemy
import datetime as dt
from datetime import timedelta
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
        f"<a href='/api/v1.0/precipitation'>precipitation</a><br/>"
        f"<a href='/api/v1.0/stations'>stations</a><br/>"
        f"<a href='/api/v1.0/tobs'>tobs</a><br/>"
        f"<a href='/api/v1.0/<start>'>start</a><br/>"
        f"<a href='/api/v1.0/<start>/<end>'>start/end</a><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the date and prcp columns from the Measurement table
    dates = session.query(Measurement.date).all()
    
    # Create loop to format strings as parsed dates
    parsed_dates = []

    for date in dates:
        temp = str(date)
        temp = temp.replace('(', '')
        temp = temp.replace(')', '')
        temp = temp.replace(',', '')
        temp = temp.replace("'", '')
        parsed_date = dt.datetime.strptime(temp, '%Y-%m-%d')
        parsed_dates.append(parsed_date)

    # Calculate date 1 year ago from the last data point in the database
    max_date = max(parsed_dates)
    min_date = max_date - timedelta(days=365)

    # Create loop to filter dates to only 1 year ago
    filtered_dates = []

    for parsed_date in parsed_dates:
        if (parsed_date <= max_date) and (parsed_date >= min_date):
            filtered_dates.append(parsed_date)

    # Create query to retrieve all precipitation scores
    prcps = session.query(Measurement.prcp).all()

    # Create loop to format strings as parsed prcps
    parsed_prcps = []

    for prcp in prcps:
        temp = str(prcp)
        temp = temp.replace('(', '')
        temp = temp.replace(')', '')
        temp = temp.replace(',', '')
        temp = temp.replace('None', '')
        parsed_prcps.append(temp)

    # Create dataframe from parsed lists
    measurement_df = pd.DataFrame({'Date': parsed_dates, 'Prcp': parsed_prcps})
    measurement_df

    # Filter dataframe to dates to only 1 year ago
    date_filter = measurement_df['Date'] >= min_date
    filtered_dates_df = measurement_df[date_filter]

    # Filter dataframe to eliminate blank prcp entries
    prcp_filter = filtered_dates_df['Prcp'] != ''
    filtered_prcp_df = filtered_dates_df[prcp_filter]

    # Separate columns before creating a new dataframe
    final_dates = filtered_prcp_df['Date']
    final_dates

    # Convert prcp to float (user: SilentGhost)
    # (url: https://stackoverflow.com/questions/1614236/in-python-how-do-i-convert-all-of-the-items-in-a-list-to-floats)
    final_prcps = [float(i) for i in filtered_prcp_df['Prcp']]
    final_prcps

    # Create dataframe with filters applied
    final_df = pd.DataFrame({'Date': final_dates, 'Precipitation': final_prcps})
    final_df

    dates_json = final_df['Date'].to_json()
    prcps_json = final_df['Precipitation'].to_json()

    session.close()

    # Create a dictionary from the results
    item_dict = {'date':dates_json, 'prcps':prcps_json}

    return jsonify(item_dict)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the station name and station key from the Station table
    results = session.query(Station.name, Station.station).all()

    session.close()

    # Convert list of tuples into normal list
    all_results = list(np.ravel(results))

    return jsonify(all_results)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Join the two tables on station
    sel = [Station.name, Measurement.station, Measurement.date, Measurement.tobs]
    same_station = session.query(*sel).filter(Measurement.station == Station.station).all()

    # Create a dataframe that includes station name
    station_df = pd.DataFrame(same_station, columns=['Name', 'Station', 'Date', 'Tobs']).reset_index()

    # Filter dataframe for station USC00519281
    filter_station_df = station_df['Station'] == 'USC00519281'
    active_station_df = station_df[filter_station_df]
    active_station_df

    session.close()

    # Convert list of tuples into normal list
    all_results = list(np.ravel(active_station_df))

    return jsonify(all_results)

@app.route("/api/v1.0/<start>")
def start(start):
    session = Session(engine)

    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).all()

    session.close()

    # Convert list of tuples into normal list
    all_results = list(np.ravel(results))

    return jsonify(all_results)

@app.route("/api/v1.0/<start>/<end>")
def end(end):
    session = Session(engine)

    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).all()

    session.close()

    # Convert list of tuples into normal list
    all_results = list(np.ravel(results))

    return jsonify(all_results)

if __name__ == '__main__':
    app.run(debug=True)
