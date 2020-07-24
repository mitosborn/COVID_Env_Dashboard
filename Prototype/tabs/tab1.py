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
import geojson
import plotly.express as px
import os
df = transforms.master_df

PAGE_SIZE = 50
mapbox_key = 'pk.eyJ1IjoiY2hyaWRkeXAiLCJhIjoiY2ozcGI1MTZ3MDBpcTJ3cXR4b3owdDQwaCJ9.8jpMunbKjdq1anXwU5gxIw'
# Import jsons
directory = os.path.dirname(os.path.abspath(__file__))
directory = os.path.join(directory,'jsons')
os.chdir(directory)
with open('counties.json') as f:
    counties = geojson.load(f)
with open('major_aq.json') as f:
    majoraq = geojson.load(f)
with open('river_basin.json') as f:
    riverbasin = geojson.load(f)
with open('watershed.json') as f:
    watershed = geojson.load(f)
local_df = pd.DataFrame()

#  html.Div([
#         dbc.Row([dbc.Col(html.Div(html.P("A single, half-width column")),style = {'padding':'50px'})
#                 ,dbc.Col(
layout = html.Div(dcc.Graph(id= 'cty_map'))

@app.callback(Output('cty_map','figure'),[Input('parameter','value'),Input('sub-group','value'),Input('wtr_layer','value'),Input('date','date')])
def get_map(parameter, sub_group, option_water,date):
    date = dt.strptime(re.split('T| ', date)[0], '%Y-%m-%d')

    # print(df[sub_group].keys())
    local_df = df[sub_group][parameter]
    local_df = local_df[local_df['date'] == date]
    print(type(date))
    print(parameter)

    trace = go.Choroplethmapbox(geojson=counties,
                                locations=local_df['fips'].astype(str),
                                z=local_df['value'],
                                colorscale='reds',featureidkey= 'properties.FIPS',
                                colorbar_thickness=20,
                                text=local_df['county'],
                                marker_line_color='white', customdata=local_df['fips'],
                                hovertemplate='<b>County</b>: <b>%{text}</b>' +
                                              '<br> <b>Val </b>: %{z}<br>' + '<extra></extra>'
                                )
    fig = go.Figure(data=trace)
    fig.update_layout(title_text= 'Average of {} on {}'.format(parameter,date.strftime("%B %d, %Y")),width=700, height=700,
                      mapbox=dict(center=dict(lat=31.3915, lon=-99.1707),
                                  accesstoken=mapbox_key, style='basic',
                                  zoom=4.5,layers=[{'sourcetype': 'geojson', 'opacity': .1,
                                           'source': counties, 'type': "fill", 'color': None}]
                                  ))
    # add aquifer polygons
    if option_water == 'Major Aquifers':
        fig.update_layout(mapbox=dict(layers=[{'sourcetype': 'geojson', 'opacity': 0.6,
                                               'source': majoraq, 'type': "fill", 'color': "royalblue"}]))
    if option_water == 'River Basins':
        fig.update_layout(mapbox=dict(layers=[{'sourcetype': 'geojson', 'opacity': 0.6,
                                               'source': riverbasin, 'type': "line", 'color': "royalblue"}]))
    if option_water == 'Watersheds':
        fig.update_layout(mapbox=dict(layers=[{'sourcetype': 'geojson', 'opacity': 0.6,
                                               'source': watershed, 'type': "line", 'color': "royalblue"}]))
    return fig

@app.callback(Output('model','figure'),[Input('cty_map', 'clickData'),Input('parameter','value'),Input('sub-group','value')])
def display_click_data(clickData,parameter, sub_group):
    if clickData is not None:
        local_df = df[sub_group][parameter]
        fips_number = clickData["points"][0]['location']
        fips_number = int(fips_number)
        print(fips_number)
        print(local_df.head())
        select = local_df[local_df['fips'] == fips_number].copy().reset_index()
        select['Time'] = pd.to_datetime(select['date'])
        print(select)
        print(select.head())
        select = select.groupby(['date','fips','county']).mean().reset_index()
        select['date'] = pd.to_datetime(select['date'])

        fig = px.line(select, x='date', y="value", title='Concentration of '+parameter)

        fig.update_layout(xaxis_title='Time',
                          yaxis_title=parameter+' Concentration (e-6 ppv)')

        fig.update_traces(marker_size=20)
        fig.update_xaxes(
            rangeslider_visible=True,
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all")
                ])
            )
        )
    #return (fips_number, fig)
        return fig
    return px.line()