from flask import Flask, render_template, request, redirect, url_for, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, Polution, User

import tensorflow as tf
from keras import backend as K
from keras.models import load_model
import pandas as pd
import numpy as np
import os
import datetime

import boto3
import io

class ScoringService(object):
    model = None                # Where we keep the model when it's loaded

    @classmethod
    def get_model(cls):
        """Get the model object for this instance, loading it if it's not already loaded."""
        if cls.model == None:
            cls.model = load_model('meter831001_01.h5')
        return cls.model


    @classmethod
    def predict(cls, input):
        """For the input, do the predictions and return them.

        Args:
            input (a pandas dataframe): The data on which to do the predictions. There will be
                one prediction per row in the dataframe"""
        test_X = input.values
        test_X = test_X.reshape((test_X.shape[0], 1, test_X.shape[1]))

        sess = K.get_session()
        with sess.graph.as_default():
            clf = cls.get_model()
            return clf.predict(test_X)


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

    test = pd.DataFrame(output)

    #prediction localy
    predictions = ScoringService.predict(test)

    #prediction with sage maker
    payload = test
    payload_file = io.StringIO()
    payload.to_csv(payload_file, header = None, index = None)

    client = boto3.client('sagemaker-runtime')
    response = client.invoke_endpoint(EndpointName='transcanada-poc-2020-01-14-20-02-57-206',
                                      ContentType = 'text/csv',
                                      Body= payload_file.getvalue())
    sagemaker_results = response['Body'].read()
    #return str(predictions), str(sagemaker_results)
    #return str(sagemaker_results)
    return render_template('results.html', local_prediction=predictions,
                            sagemaker_prediction=sagemaker_results)

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
