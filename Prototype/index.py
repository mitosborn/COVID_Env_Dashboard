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
param_output = {'GHG':[{"label": "XCO2", "value": "XCO2"},
                     {"label": "XCH4", "value": "XCH4"}],
                'AQ':[{"label": "NOx", "value": "NOx"},
                     {"label": "PM2.5", "value": "PM2.5"},
                      {"label": "CO", "value": "CO"},
                      {"label": "Ozone", "value": "Ozone"}],
                'WQ':[{"label": "Dissolved Oxygen", "value": "Dissolved Oxygen"},
                     {"label": "Orthophosphate", "value": "Orthophosphate"}],
                'ECON':[{"label": "Cumulative Cases", "value": "cumulative cases"},
                        {"label":"Cumulative Deaths","value":"cumulative deaths"},
                        {"label":"Cumulative Deaths per 100k","value":"cumulative deaths per 100k"},
                        {"label":"Cumulative Cases per 100k","value":"cumulative cases per 100k"}]}
show_water = lambda x: {'display':'block'} if x == 'WQ' else {'display':'none'}
#Function that updates the parameters shown. If the selected group is not water, hides the layer tab.
#Additionally, the function always sets layers to none to prevent layers showing after water is deselected.
@app.callback([Output('parameter','options'),Output('parameter','value'),Output('water_title','style'),Output('wtr_layer','style'),Output('wtr_layer','value')],[Input('sub-group','value')])
def return_parameters(selected_group):
    return param_output[selected_group], param_output[selected_group][0]['value'], show_water(selected_group),show_water(selected_group), 'None'

@app.callback(Output('date_range','marks'),[Input('date_interval','value'),Input('parameter','value'),Input('sub-group','value')])
def return_timeline(interval, group, parameter):
    print(interval,group,parameter)
    return {
        0: {'label': '0 °C', 'style': {'color': '#77b0b1'}},
        26: {'label': '26 °C'},
        37: {'label': '37 °C'},
        100: {'label': '100 °C', 'style': {'color': '#f50'}}
    }

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