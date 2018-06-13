## Importing required libraries
import numpy as np
import pandas as pd
import sqlalchemy
import os
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, render_template,jsonify, request, redirect

## Database Setup
dbfile = os.path.join('db', 'belly_button_biodiversity.sqlite')
engine = create_engine(f"sqlite:///{dbfile}")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# Save reference to the tables
samples_table = Base.classes.samples
otu_table = Base.classes.otu
metadata_table = Base.classes.samples_metadata.                       
# Create our session (link) from Python to the DB
session = Session(engine)

# Flask Setup
app = Flask(__name__)


# first route
@app.route("/")
def home():
    """Render Home Page."""
    return render_template("index.html")  

                       
# second route
@app.route('/names')
def names():
    """Return a list of sample names."""
    stmt = session.query(samples_table).statement
    df = pd.read_sql_query(stmt, session.bind)
    df.set_index('otu_id', inplace=True)
    # Return a list of sample names
    return jsonify(list(df.columns))

                       
# third route
@app.route('/otu')
def otu():
    """Return a list of OTU descriptions."""
    results = session.query(otu_table.lowest_taxonomic_unit_found).all()
    # Use numpy ravel to extract list of tuples into a list of otu descriptions
    otu_list = list(np.ravel(results))
    return jsonify(otu_list)

                       
# forth route
@app.route('/metadata/<sample>')
def sample_metadata(sample):
    """Return the MetaData for a given sample."""
    sel = [Samples_Metadata.SAMPLEID, Samples_Metadata.ETHNICITY,
           Samples_Metadata.GENDER, Samples_Metadata.AGE,
           Samples_Metadata.LOCATION, Samples_Metadata.BBTYPE]

    # sample[3:] strips the `BB_` prefix from the sample name to match
    # the numeric value of `SAMPLEID` from the database
    results = session.query(*sel).\
        filter(Samples_Metadata.SAMPLEID == sample[3:]).all()

    # Create a dictionary entry for each row of metadata information
    sample_metadata = {}
    for result in results:
        sample_metadata['SAMPLEID'] = result[0]
        sample_metadata['ETHNICITY'] = result[1]
        sample_metadata['GENDER'] = result[2]
        sample_metadata['AGE'] = result[3]
        sample_metadata['LOCATION'] = result[4]
        sample_metadata['BBTYPE'] = result[5]
    return jsonify(sample_metadata)



@app.route('/metadata/<sample>')
def sample_metadata(sample):
    """Return the MetaData for a given sample."""
    sel = [Samples_Metadata.SAMPLEID, Samples_Metadata.ETHNICITY,
           Samples_Metadata.GENDER, Samples_Metadata.AGE,
           Samples_Metadata.LOCATION, Samples_Metadata.BBTYPE]

    results = session.query(*sel).\
        filter(Samples_Metadata.SAMPLEID == sample[3:]).all()

    data_dict = {}
    for result in results:
        data_dict["AGE"] = result[3]
        data_dict["BBTYPE"] = result[5]
        data_dict["ETHNICITY"] = result[1]
        data_dict["GENDER"] = result[2]
        data_dict["LOCATION"] = result[4]
        data_dict["SAMPLEID"] = result[0]               
    return jsonify(data_dict)
 
                       
# fifth route
def sample_wfreq(sample):
    """Return the Weekly Washing Frequency as a number."""

    results = session.query(Samples_Metadata.WFREQ).\
        filter(Samples_Metadata.SAMPLEID == sample[3:]).all()
    wfreq = np.ravel(results)

    return jsonify(int(wfreq[0]))

                                 
# sixth route
@app.route('/samples/<sample>')
def samples(sample):
    """Return a list dictionaries containing `otu_ids` and `sample_values`."""
    stmt = session.query(Samples).statement
    df = pd.read_sql_query(stmt, session.bind)

    if sample not in df.columns:
        return jsonify(f"Error! Sample: {sample} Not Found!"), 400

    df = df[df[sample] > 1]
    df = df.sort_values(by=sample, ascending=0)
    data = [{
        "otu_ids": df[sample].index.values.tolist(),
        "sample_values": df[sample].values.tolist()
    }]
    return jsonify(data)




if __name__ == "__main__":
    app.run(debug=True)

                       