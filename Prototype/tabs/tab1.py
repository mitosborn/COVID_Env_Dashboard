import dash
import plotly
import dash_core_components as dcc
import dash_html_components as html 
import dash_bootstrap_components as dbc 
import dash_table
import pandas as pd
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from app import app 
from database import transforms
import json
from urllib.request import urlopen
from datetime import datetime as dt
import re
df = transforms.master_df

PAGE_SIZE = 50
mapbox_key = 'pk.eyJ1IjoiY2hyaWRkeXAiLCJhIjoiY2ozcGI1MTZ3MDBpcTJ3cXR4b3owdDQwaCJ9.8jpMunbKjdq1anXwU5gxIw'
with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)


#  html.Div([
#         dbc.Row([dbc.Col(html.Div(html.P("A single, half-width column")),style = {'padding':'50px'})
#                 ,dbc.Col(
layout = html.Div(dcc.Graph(id= 'cty_map'))

@app.callback(Output('cty_map','figure'),[Input('parameter','value'),Input('sub-group','value'),Input('layers','value'),Input('date','date')])
def get_map(parameter, sub_group, layer,date):
    date = dt.strptime(re.split('T| ', date)[0], '%Y-%m-%d')
    fig = go.Figure(go.Choroplethmapbox(geojson=counties,
                                    colorscale='ice',
                                    colorbar_thickness=20
                                    ))
    if sub_group is not None and parameter is not None:
        # print(df[sub_group].keys())
        local_df = df[sub_group][parameter]
        local_df = local_df[local_df['date'] == date]
        print(type(date))
        print(parameter)

        trace = go.Choroplethmapbox(geojson=counties,
                                    locations=local_df['fips'],
                                    z=local_df['value'],
                                    colorscale='ice',
                                    colorbar_thickness=20,
                                    text=local_df['county'],
                                    marker_line_color='white', customdata=local_df['fips'],
                                    hovertemplate='<b>County</b>: <b>%{text}</b>' +
                                                  '<br> <b>Val </b>: %{z}<br>' + '<extra></extra>'
                                    )
        fig = go.Figure(data=trace)
        fig.update_layout(title_text= 'Average of {} on {}'.format(parameter,date.strftime("%B %d, %Y")))
    else:
        fig.update_layout(title_text = 'Select a group and parameter')
    fig.update_layout(width=700, height=700,
                      mapbox=dict(center=dict(lat=31.3915, lon=-99.1707),
                                  accesstoken=mapbox_key, style='basic',
                                  zoom=4.5,
                                  ))

    return fig
