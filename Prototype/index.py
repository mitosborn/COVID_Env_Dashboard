import dash
import plotly
import dash_core_components as dcc
import dash_html_components as html 
import dash_table
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

from app import app
from tabs import sidepanel, tab1, tab2
from database import transforms
import sqlite3
import dash
from dash.dependencies import Input, Output
import dash_table
import pandas as pd

from app import app
from tabs import sidepanel, tab1, tab2
from database import transforms

app.layout = sidepanel.layout
param_output = {'GHG':[{"label": "Greenhouse Gas - XCO2", "value": "XCO2"},
                     {"label": "Greenhouse Gas - XCH4", "value": "XCH4"}],'AQ':[{"label": "Air Quality - NO2", "value": "NO2"},
                     {"label": "Air Quality - PM2.5", "value": "PM2.5"}],'WQ':[{"label": "Water Quality - Dissolved Oxygen", "value": "Dissolved Oxygen"},
                     {"label": "Water Quality - Orthophosphate", "value": "Orthophosphate"}],'ECON':[{"label": "COVID Cases", "value": "COVID Cases"}]}


@app.callback(Output('parameter','options'),[Input('sub-group','value')])
def return_parameters(selected_group):
    return param_output[selected_group] if selected_group is not None else [{"label":'',"value":''}]


@app.callback(Output('tabs-content', 'children'),
              [Input('tabs', 'value')])
def render_content(tab):
    if tab == 'tab-1':
        return tab1.layout
    elif tab == 'tab-2':
        return tab2.layout
# @app.callback(Output('',''),[Input('sub-group','value'),Input('parameter','value')])
# def update_graph(group, parameter, map_type):
#     pass




if __name__ == '__main__':
    app.run_server(debug = True)