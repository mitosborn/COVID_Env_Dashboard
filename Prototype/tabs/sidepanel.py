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
                         searchable = False, clearable = False, placeholder = 'Select a group'),
        html.Div([html.H3('Select Parameter(s)'), dcc.Dropdown(id = 'parameter',searchable = False)
                   ]), html.Div([html.H3('Select Layers'),dcc.Checklist(id = 'layers',options=[
            {'label': 'Aquifers', 'value': 'Aquifers'},
            {'label': 'Water Shed', 'value': 'Watershed'} # we can ignore river basin
        ],
        value=['Aquifers','Watershed'])]),html.Div([html.H3('Select Date'),dcc.DatePickerSingle(
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
        ]), width=6), dbc.Col(html.Div([dcc.Graph(id = 'model')]),width = 3)])
    
    ])
