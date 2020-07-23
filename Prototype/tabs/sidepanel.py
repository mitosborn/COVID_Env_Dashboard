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

layout = html.Div([
    html.H1('COVID Dashboard')
    ,dbc.Row([dbc.Col(
        html.Div([
         html.H2('Filters'),html.H3('Select a group'), dcc.Dropdown(
                       id='sub-group',
                         options = [{'label':i,'value':selection[i]} for i in selection.keys()],
                         searchable = False, clearable = False, placeholder = 'Select a group',value ='AQ'),
        html.Div([html.H3('Select Parameter(s)'), dcc.Dropdown(id = 'parameter',searchable = False,options = [{"label": "Air Quality - NO2", "value": "NO2"}],value = 'NO2')
                   ]), html.Div([html.H3('Select Layers'),dbc.RadioItems(id = 'wtr_layer',options=[
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
    , width=3)

    ,dbc.Col(html.Div([
            dcc.Tabs(id="tabs", value='tab-1', children=[
                    dcc.Tab(label='County', value='tab-1'),
                    dcc.Tab(label='Sensor', value='tab-2')
                ])
            , html.Div(id='tabs-content')
        ]), width=5), dbc.Col(html.Div([dcc.Tabs(id="temp", value='temp-1', children=[
                    dcc.Tab(label='Model', value='temp-1')
                ]),dcc.Graph(id = 'model')]
    #                                    style = {
    # "position": "fixed",
    # "top": 200,
    # "left": 1050,
    # "bottom": 0,
    # "width": "80rem",
    # "padding": "2rem 1rem",
    # #"background-color": "#f8f9fa",}
    ),width = 4)])
    
    ])


