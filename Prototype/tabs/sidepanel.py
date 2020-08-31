import dash
import plotly
import dash_core_components as dcc
import dash_html_components as html 
import dash_bootstrap_components as dbc 
import dash_table
import pandas
from dash.dependencies import Input, Output
import datetime
from app import app
import json
from tabs import tab1, tab2
from database import transforms

df = transforms.master_df
selection = {'Air Quality':'AQ','Greenhouse Gases':'GHG','Water Quality':'WQ','Economics':'ECON'}
years = [{'label':'2019','value':2019},{'label':'2018','value':2018},{'label':'2017','value':2017},{'label':'2016','value':2016},{'label':'2015','value':2015},{'label':'2015-2019 Average','value':'avg'}]
interval = [{'label':'Daily','value':'daily'},{'label':'Weekly','value':'weekly'},{'label':'Monthly','value':'monthly'},{'label':'Rolling 14 day average','value':'rolling'}]
layout = html.Div([
    html.H1('COVID Dashboard')
    ,dbc.Row([dbc.Col(
        html.Div([
         html.H2('Filters'),html.H3('Select group'), dcc.Dropdown(
                       id='sub-group',
                         options = [{'label':i,'value':selection[i]} for i in selection.keys()],
                         searchable = False, clearable = False, placeholder = 'Select a group',value ='AQ'),
        html.Div([html.H3('Select Parameter'), dcc.Dropdown(id = 'parameter',searchable = False,options = [{"label": "Air Quality - NO2", "value": "NO2"}],clearable = False,value = 'NO2')
                   ]), html.Div([html.H3('Layers',id = 'water_title'),dbc.RadioItems(id = 'wtr_layer',options=[
                {'label':'None','value':'None'},
                {'label': 'Major Aquifers', 'value': 'Major Aquifers'},
                {'label': 'River Basins', 'value': 'River Basins'},
                {'label': 'Watersheds', 'value': 'Watersheds'}

            ],
        value='None')]),html.Div([html.H3('Select Date'),dcc.DatePickerSingle(
        id='date',
        min_date_allowed=datetime.datetime(2020, 1, 1),
        max_date_allowed=datetime.datetime(2020, 7, 10),
        initial_visible_month=datetime.datetime(2020, 1, 1),
        date=str(datetime.datetime(2020, 1, 1))
    )])], style={'marginBottom': 50, 'marginTop': 25, 'marginLeft':15, 'marginRight':15})
    , width=2)

    ,dbc.Col(html.Div([
            dcc.Tabs(id="tabs", value='tab-1', children=[
                    dcc.Tab(label='County', value='tab-1'),
                    dcc.Tab(label='Sensor', value='tab-2')
                ])
            , html.Div(id='tabs-content')
        ]), width=5), dbc.Col(html.Div([dcc.Tabs(id="temp", value='temp-1', children=[
                    dcc.Tab(label='Trends', value='temp-1')
                ]),dcc.Graph(id = 'model'),
                                        dbc.Row([dbc.Col(html.Div([html.H5('Show Timeline'),dbc.RadioItems(id = 'time_lines',options = [
                                                                                       {'label':'Show','value':True},{'label':'Hide','value':False}],value = True)]
    )),dbc.Col(html.Div([html.H5("Compare Other Years"),dcc.Dropdown(id = 'years',options = years,searchable = False,multi = True,value=['avg'])])),dbc.Col(html.Div([html.H5("Averaging Interval"),dbc.RadioItems(id = 'avg_type',options = interval,value = 'daily')]))])
                                        ]),width = 5)])
    
    ])


