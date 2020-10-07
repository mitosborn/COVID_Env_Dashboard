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
df = transforms.master_df
app.layout = sidepanel.layout
param_output = {'GHG':[{"label": "CO2", "value": "XCO2"},
                     {"label": "CH4", "value": "XCH4"}],
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

@app.callback([Output('date_range','marks'),Output('date_range','max'),Output('date_range','style'),Output('date_title','style'),Output('date_range','value')],[Input('date_interval','value'),Input('parameter','value'),Input('sub-group','value'),Input('mode','value'),Input('comp_year','value')])
def return_timeline(interval, parameter, group,compare_mode, year_selected):
    print(interval,group,parameter)
    base_year = 2020
    if len(compare_mode) == 0:
        if year_selected == 'avg':
            base_year = 2000
        else:
            base_year = year_selected
    if interval == 'monthly':
        print(group, parameter)
        local_df = df[group][parameter]
        local_df = local_df[local_df['date'].dt.year == base_year]
        months = set(local_df['date'])
        max_month = list(map(lambda x: x.month,months))
        to_return = {val.month:{'label':val.strftime("%b"),'style': {"transform": "rotate(45deg)"}} for val in months}
        print(to_return)
        return to_return, max(max_month), {'display':'block'}, {'display':'block'}, 1
    return {
        0: {'label': '0 °C', 'style': {'color': '#77b0b1'}},
        26: {'label': '26 °C'},
        37: {'label': '37 °C'},
        100: {'label': '100 °C', 'style': {'color': '#f50'}}
    }, 150, {'display':'none'}, {'display':'none'}, 1

@app.callback(Output('tabs-content', 'children'),
              [Input('tabs', 'value')])
def render_content(tab):
    if tab == 'tab-1':
        return tab1.layout


@app.callback([Output('comp_year','options'),Output('mode_title','children')],[Input('mode','value')])
def update_comp_chart(compare_mode):
    #Because the value is outputted in a list, set its value as the first element
    if len(compare_mode) > 0:
        return [{'label': '2015', 'value': 2015}, {'label': '2016', 'value': 2016}, {'label': '2017', 'value': 2017},
                 {'label': '2018', 'value': 2018}, {'label': '2019', 'value': 2019},
                 {'label': '2015-2019 Average', 'value': 'avg'}], html.H3("Comparison Year")
    return ([{'label': '2015', 'value': 2015}, {'label': '2016', 'value': 2016}, {'label': '2017', 'value': 2017}, {'label': '2018', 'value': 2018}, {'label': '2019', 'value': 2019},{'label': '2015-2019 Average', 'value': 'avg'},{'label': '2020', 'value': 2020}],
            html.H3("Viewing Year"))



if __name__ == '__main__':
    app.run_server(debug = True)