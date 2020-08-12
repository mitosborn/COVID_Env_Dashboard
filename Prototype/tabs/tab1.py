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
aq_units = {'Ozone':'ppm','PM2.5':'μg/m3','NOx':'ppb','CO':'ppm','NO':'ppm'}
econ_units ={"cumulative cases":'cases',"cumulative deaths": 'deaths',"cumulative deaths per 100k":'deaths/100k',"cumulative cases per 100k":'cases/100k'}
wq_units = {"Dissolved Oxygen":"milligrams/Liter","Orthophosphate":"milligrams/Liter"}
ghg_units = {"XCO2":"ppm","XCH4":"ppm"}
units = {"AQ":aq_units,"ECON":econ_units,"WQ":wq_units,"GHG":ghg_units}
layout = html.Div(dcc.Graph(id= 'cty_map'))

@app.callback(Output('cty_map','figure'),[Input('parameter','value'),Input('sub-group','value'),Input('wtr_layer','value'),Input('date','date')])
def get_map(parameter, sub_group, option_water,date):
    date = dt.strptime(re.split('T| ', date)[0], '%Y-%m-%d')

    # print(df[sub_group].keys())
    print(df[sub_group].keys())
    if sub_group == 'ECON':
        date = dt.now()
        local_df = df[sub_group]['Econ_Clean'].loc[:,['fips',parameter,'county']].copy()
        local_df.rename(columns = {parameter:'value'},inplace = True)
        local_df['fips'] = local_df['fips'].astype(int)
        print(local_df)
    else:
        local_df = df[sub_group][parameter]
        local_df = local_df[local_df['date'] == date]
        local_df = local_df.groupby(['date','fips','county']).mean().reset_index()
    print(type(date))
    print(parameter)
    title = (lambda x,a: parameter+' ('+units[x][a]+')' if x not in 'ECON' else 'COVID '+units[x][a].capitalize())(sub_group,parameter)
    trace = go.Choroplethmapbox(geojson=counties,
                                locations=local_df['fips'].astype(str),
                                z=local_df['value'],
                                colorscale='reds',featureidkey= 'properties.FIPS',
                                colorbar_thickness=20,
                                text=local_df['county'],
                                marker_line_color='white', customdata=local_df['fips'],
                                hovertemplate='<b>County</b>: <b>%{text}</b>' +
                                              '<br> <b>Value </b>: %{z}<br>' + '<extra></extra>',
                                colorbar_title_text=title)
    fig = go.Figure(data=trace)
    title = (lambda x,a: 'Average of {} on {}'.format(a,date.strftime("%B %d, %Y")) if x not in 'ECON' else a.capitalize() + ' as of '+date.strftime("%B %d, %Y"))(sub_group,parameter)
    fig.update_layout(title_text= title,width=750, height=750,
                      mapbox=dict(center=dict(lat=31.3915, lon=-100.1707),
                                  accesstoken=mapbox_key, style='basic',
                                  zoom=4.75,layers=[{'sourcetype': 'geojson', 'opacity': .1,
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

@app.callback(Output('model','figure'),[Input('cty_map', 'clickData'),Input('parameter','value'),Input('sub-group','value'),Input('time_lines','value')])
def display_click_data(clickData,parameter, sub_group,show_lines):
    if clickData is not None and sub_group != 'ECON':
        local_df = df[sub_group][parameter]
        fips_number = clickData["points"][0]['location']
        fips_number = str(int(fips_number))
        print(fips_number)
        print(local_df.head())
        select = local_df[local_df['fips'] == fips_number].copy().reset_index()
        select['Time'] = pd.to_datetime(select['date'])
        print(select)
        print(select.head())
        select = select.groupby(['date','fips','county']).mean().reset_index()
        select['date'] = pd.to_datetime(select['date'])

        fig = px.line(select, x='date', y="value", title='Concentration of '+parameter + ' in ' + select.loc[0,'county'] + ' County')

        fig.update_layout(xaxis_title='Time',
                          yaxis_title=parameter+' Concentration ('+units[sub_group][parameter]+')')

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
        fig.layout.yaxis.update(range=[min(select['value']), max(select['value'])])

        if show_lines:
            opening = 'State<br>Opening'
            closure = "State<br>Closure"
            fig.add_trace(go.Scatter(
                x=["2020-05-05","2020-05-05"],
                y=[min(select['value']),max(select['value'])],
                name=opening,
                mode = 'lines',
                line_color = '#51E10E'
            ))
            fig.add_trace(go.Scatter(
                x=["2020-04-02", "2020-04-02"],
                y=[min(select['value']), max(select['value'])],
                name=closure,
                mode='lines',
                line_color='#ED0925'
            ))

        return fig
    elif sub_group == 'ECON':
        print(clickData)
        print('here')
        return px.bar(df[sub_group]['Econ_Clean'],x = 'county', y = parameter)
    else:
        text = "Click on a county to see trends"
        fig = px.line()
        fig.add_annotation(
            x=0.5,
            y=0.5,
            text=text,
            xref="paper",
            yref="paper",
            showarrow=False,
            font_size=20
        )
    return fig