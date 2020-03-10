from flask import Flask, render_template, request, redirect, url_for, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, Polution, User

#import tensorflow as tf
#from keras import backend as K
#from keras.models import load_model
import pandas as pd
import numpy as np
import os
import datetime

import boto3
import io


app = Flask(__name__)


engine = create_engine('sqlite:///polution.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
@app.route('/ml')
def MLWebApp():
    polution = session.query(Polution).order_by(Polution.created_date.desc()).first()
    return render_template('index.html', polution=polution)

@app.route('/ml/forecast/', methods=['GET', 'POST'])
def forecast():

    if request.method == 'POST':
        newforecast = Polution(name=request.form['name'],
                                polution=request.form['polution'],
                                dew=request.form['dew'],
                                temp=request.form['temp'],
                                pres=request.form['pres'],
                                wnddir=request.form['wnddir'],
                                wndspd=request.form['wndspd'],
                                snow=request.form['snow'],
                                rain=request.form['rain'])
        session.add(newforecast)
        session.commit()
        return redirect(url_for('results'))
    else:
        return render_template('forecast.html')

@app.route('/ml/results/')
def results():
    polution = session.query(Polution).order_by(Polution.created_date.desc()).first()
    output = [[int(polution.polution),
              int(polution.dew),
              int(polution.temp),
              int(polution.pres),
              int(polution.wnddir),
              int(polution.wndspd),
              int(polution.snow),
              int(polution.rain)]]
    test1 = [[1,1,1,1,1,1,1,1]]
    test = pd.DataFrame(output)

    #prediction localy
    #predictions = ScoringService.predict(test)

    #prediction with sage maker
    payload = test
    #payload_file = io.StringIO()
    payload_file = io.BytesIO()
    payload.to_csv(payload_file, header = None, index = None)

    client = boto3.client('sagemaker-runtime', region_name='us-east-1')
    response = client.invoke_endpoint(EndpointName='transcanada-poc2-2020-03-03-04-56-08-192',
                                      ContentType = 'text/csv',
                                      Body= payload_file.getvalue())
    sagemaker_results = response['Body'].read()
    #return str(predictions), str(sagemaker_results)
    #return str(sagemaker_results)

    #prediction from athena
    athena = boto3.client('athena', region_name='us-east-1')
    s3     = boto3.resource('s3', region_name='us-east-1')
    query = ("""SELECT * FROM pollution""")
    print(query)
    s3_bucket = 'aws-athena-query-results-532109487980-us-east-1'
    database = "athenadbtest"
    s3_ouput  = 's3://'+ s3_bucket
    response = athena.start_query_execution(
        QueryString=query,
        QueryExecutionContext={
            'Database': database
        },
        ResultConfiguration={
            'OutputLocation': 's3://aws-athena-query-results-532109487980-us-east-1',
    })


    print(response)
    QueryExecutionId = response['QueryExecutionId']
    s3_key = QueryExecutionId + '.csv'
    local_filename = QueryExecutionId + '.csv'
    #s3.Bucket(s3_bucket).download_file(s3_key, local_filename)
    time.sleep(10)
    print(s3_key)
    s33 = boto3.client('s3', region_name='us-east-1')

    obj = s33.get_object(Bucket='aws-athena-query-results-532109487980-us-east-1', Key=s3_key)
    df = pd.read_csv(obj['Body'])
    #df = pd.read_csv(local_filename)
    df = df.drop('index',axis=1)

    #prediction with sage maker
    payload2 = df
    payload_file2 = io.BytesIO()
    payload2.to_csv(payload_file2, header = None, index = None)

    client = boto3.client('sagemaker-runtime', region_name='us-east-1')
    response = client.invoke_endpoint(EndpointName='transcanada-poc2-2020-03-03-04-56-08-192',
                                      ContentType = 'text/csv',
                                      Body= payload_file2.getvalue())
    sagemaker_results2 = response['Body'].read()

    return render_template('results.html', sagemaker_prediction=sagemaker_results)

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
