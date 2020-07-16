# -*- coding: utf-8 -*-
"""
Created on Mon Jul 13 13:33:04 2020

@author: zevge
"""


import pandas as pd
import plotly.express as px  # (version 4.7.0)
import plotly.graph_objects as go

import dash  # (version 1.12.0) pip install dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import datetime


from netCDF4 import Dataset
import json
import plotly.offline as py


raw = pd.read_csv('NWQMC_Data.csv')
water = pd.DataFrame()

water['sub'] = raw['CharacteristicName']
water['lat'] = raw['LatitudeMeasure']
water['lon'] = raw['LongitudeMeasure']
water['val'] = raw['ResultMeasureValue']
water['units'] = raw['ResultMeasure/MeasureUnitCode']
water['date'] = raw['ActivityStartDate']
water['date'] = pd.to_datetime(water['date'])


water['year'] = water.date.dt.year
water['month'] = water.date.dt.month
water['id'] = raw['MonitoringLocationIdentifier']

water['avg'] = water['val'].groupby(water['id']).transform('mean')
water['show'] = water['avg'].astype(str) + " " + water['units']


current_date = datetime.datetime(2020,1,1)
base = datetime.datetime.today()
base = base.replace(hour=0, minute=0, second=0)
numdays = (base - datetime.datetime.fromisoformat('2020-01-01')).days
date_list = [base - datetime.timedelta(days=x) for x in range(numdays)]
date_list.insert(0,datetime.datetime(2020,1,1))
water['avg1'] = water['val'].groupby(water['id']).transform('mean')


app = dash.Dash(__name__)

app.layout = html.Div([

    html.H1("Point Map Demo 2", style={'text-align': 'center'}),
    
      dcc.Dropdown(id="slct_var",
                 options=[
                     {"label": "Chloride", "value": 'Chloride'},
                     {"label": "Dissolved oxygen (DO)", "value": 'Dissolved oxygen (DO)'},
                     {"label": "Nitrate", "value": 'Nitrate'},
                     {"label": "Orthophosphate", "value": 'Orthophosphate'},
                     {"label": "Temperature, water", "value": 'Temperature, water'},
                     {"label": "Sulfate", "value": 'Sulfate'},
                     {"label": "Specific conductance", "value": 'Specific conductance'},],
                 multi=False,
                 value= 'Chloride',
                 style={'width': "40%"}
                 ),
      dcc.Graph(id='water_map'),dcc.Slider(
    id = 'year-slider',
    min=2016,
    max=2020,
    step=None,
    marks={
        2016: '2016',
        2017: '2017',
        2017: '2018',
        2018: '2019',
        2019: '2020'
    },
    value=2016
) ]   )




@app.callback(
    Output('water_map', 'figure'),
    [Input(component_id='slct_var', component_property='value'),
    Input(component_id='year-slider', component_property='value')]
    
)


def update_graph(slct_var, slct_date):
    
    dff = water.copy()
    dff = dff[dff['sub'] == slct_var]
    dff =  dff[dff['year'] == slct_date]
    dff['avg'] = dff['val'].groupby(dff['id']).transform('mean')
    dff['show'] = dff['avg'].astype(str) + " " + dff['units']

    
    fig = px.scatter_mapbox(dff, lat="lat", lon="lon", hover_name = 'show', color = 'avg', size = 
                            'avg',
    color_continuous_scale=px.colors.cyclical.IceFire, size_max=15, zoom=10)
    
    mapboxt = 'pk.eyJ1IjoiY2hyaWRkeXAiLCJhIjoiY2ozcGI1MTZ3MDBpcTJ3cXR4b3owdDQwaCJ9.8jpMunbKjdq1anXwU5gxIw'       
    
    fig.update_layout(title_text= 'Texas PointMap',
                      title_x=0.5, width = 700, height=700,
                      mapbox = dict(center= dict(lat=31.3915,  lon=-99.1707),
                                     accesstoken= mapboxt,style = 'basic',
                                     zoom=4.5,
                                   ));
   

    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        
 

    return fig


if __name__ == '__main__':
    app.run_server(debug=False)
