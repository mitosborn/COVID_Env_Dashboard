import dash
import plotly
import dash_core_components as dcc
import dash_html_components as html 
import dash_bootstrap_components as dbc 
import dash_table
import pandas as pd
from datetime import datetime
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from app import app 
from database import transforms
import json
from urllib.request import urlopen
from datetime import datetime as dt
import re
from sklearn.linear_model import LinearRegression
import geojson
import plotly.express as px
import os
import calendar
from plotly.subplots import make_subplots
import numpy as np
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

#  html.Div([
#         dbc.Row([dbc.Col(html.Div(html.P("A single, half-width column")),style = {'padding':'50px'})
#                 ,dbc.Col(
aq_units = {'Ozone':'ppm','PM2.5':'μg/m3','NOx':'ppb','CO':'ppm','NO':'ppm'}
econ_units ={"cumulative cases":'cases',"cumulative deaths": 'deaths',"cumulative deaths per 100k":'deaths/100k',"cumulative cases per 100k":'cases/100k'}
wq_units = {"Dissolved Oxygen":"milligrams/Liter","Orthophosphate":"milligrams/Liter"}
ghg_units = {"XCO2":"ppm","XCH4":"ppm"}
units = {"AQ":aq_units,"ECON":econ_units,"WQ":wq_units,"GHG":ghg_units}
layout = dcc.Graph(id= 'cty_map',style={"height":'100%'})

@app.callback(Output('cty_map','figure'),[Input('parameter','value'),Input('sub-group','value'),Input('wtr_layer','value'),Input('date_interval','value'),Input('comp_year','value'),Input('date_range','value')
                                          ,Input('mode','value')])
def get_map(parameter, sub_group, option_water,comp_type,comp_year,comp_month,take_diff):
    # print(df[sub_group].keys())
    # print(comp_year)
    print(type(take_diff))
    print(take_diff)
    if sub_group == 'ECON':
        local_df = df['ECON']['econ_data']
        print(local_df.columns)
        fig = go.Figure()
        if parameter == 'pm2.5':
            trace = go.Choroplethmapbox(geojson=counties,
                                        locations=local_df['fips'].astype(str),
                                        z=local_df['pm2.5'],
                                        colorscale='oranges',
                                        colorbar_thickness=15, colorbar_len=0.7, colorbar_y=0.7,
                                        marker_line_color='white', name='pm 2.5 mg/m3', featureidkey= 'properties.FIPS',
                                        colorbar_title='pm 2.5 (mg/m<sup>3</sup>)', colorbar_titlefont=dict(size=11),
                                        colorbar_tickfont=dict(size=11))

            fig.add_trace(trace)
            fig.update_layout(showlegend=True, title_text='County Average PM 2.5 and COVID Cases',
                              title_x=0.5, title_y=0.94, autosize = True, legend=dict(font=dict(size=11),
                                                                                            yanchor='bottom',
                                                                                            xanchor='right',
                                                                                            y=1, x=1, orientation='h'),
                              mapbox=dict(center=dict(lat=31.3915, lon=-100.1707),
                                          accesstoken=mapbox_key, style="streets",
                                          zoom=5.75))
        #Comparing race vs Cases/Deaths
        else:
            trace = go.Choroplethmapbox(geojson=counties,
                                        locations=local_df['fips'].astype(str),
                                        z=local_df['bah'],featureidkey= 'properties.FIPS',
                                        colorscale='oranges',
                                        colorbar_thickness=15, colorbar_len=0.7, colorbar_y=0.7,
                                        marker_line_color='white', name='Black and Hispanic %',
                                        colorbar_title='Percentage', colorbar_titlefont=dict(size=11),
                                        colorbar_tickfont=dict(size=11))

            fig.add_trace(trace)

            fig.update_layout(showlegend=True, title_text= 'Black & Hispanic American Percentage of COVID Cases/Deaths',
                               title_x=0.5, title_y=0.94, autosize = True, legend=dict(font=dict(size=11),
                                                                                            yanchor='bottom',
                                                                                            xanchor='right',
                                                                                            y=1, x=1, orientation='h'),
                              mapbox=dict(center=dict(lat=31.3915, lon=-100.1707),
                                          accesstoken=mapbox_key, style="streets",
                                          zoom=5.75))
        trace2 = go.Scattermapbox(lon=local_df['intptlong'], lat=local_df['intptlat'], mode='markers',
                                  marker=go.scattermapbox.Marker(symbol='circle', size=2 * local_df[
                                      'cases/100k'],
                                                                 sizemode='area', sizemin=10, sizeref=2. * max(local_df[
                                                                                                                   'cases/100k']) / (
                                                                                                                  10 ** 2),
                                                                 opacity=0.9, color='gray'),
                                  name='Cases per 100k Population')

        trace3 = go.Scattermapbox(lon=local_df['intptlong'], lat=local_df['intptlat'], mode='markers',
                                  marker=go.scattermapbox.Marker(symbol='circle', size=20 * local_df[
                                      'deaths/100k'],
                                                                 sizemode='area', opacity=0.4, color='royalblue'),
                                  name='Deaths per 100k Population')

        fig.add_trace(trace2)
        fig.add_trace(trace3)

        return fig



    else:
        if comp_year == 'avg':
            year = 2000
        else:
            year = comp_year
        print("HERSERERSRE")
        print(parameter)
        print(sub_group)
        local_df = df[sub_group][parameter].copy()

        # Create 2015-2019 df
        if year == 2000:
            dataframe = local_df[local_df['date'].dt.year.isin([2015, 2016, 2017, 2018, 2019])].copy()
            dataframe['date'] = dataframe['date'].apply(lambda x: x.replace(year=2000))
            dataframe = dataframe.groupby(['date', 'fips', 'county']).mean().reset_index()
            local_df = local_df.append(dataframe)



        if take_diff:
            current = local_df[local_df['date'].dt.year == 2020].copy()
            current['month'] = current['date'].dt.month
            current = current.loc[:, ['fips', 'county', 'month', 'value']].groupby(['fips', 'county', 'month']).mean().reset_index()
            past = local_df[local_df['date'].dt.year == year].copy()
            past['month'] = past['date'].dt.month
            past = past.loc[:,['fips','county','month','value']].groupby(['fips','county','month']).mean().reset_index()
            merged = current.merge(past, how='left', on=['fips', 'county', 'month'], suffixes=['_current', '_past'])
            merged = merged.interpolate()
            print(past)
        else:
            current = local_df[local_df['date'].dt.year == year].copy()
            current['month'] = current['date'].dt.month
            current = current.loc[:, ['fips', 'county', 'month', 'value']].groupby(
                ['fips', 'county', 'month']).mean().reset_index()
            merged = current

        print(current)
        print("Space")

        """
        Steps:
        # 1. Implement functionality of difference button
        #    - UI should swap out "comparison year" with "selected year" -> This will be a value switch
        #    - UI should swap out contents of year selector by adding in 2020
        #    - This can be accomplished in one method
          2. 
        """


        if comp_type == 'annual':
            merged = merged.groupby(['fips','county']).mean().reset_index()
        else:
            merged = merged[merged['month'] == comp_month]
        if take_diff:
            merged['value'] = merged['value_current'] - merged['value_past']
        local_df = merged

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
    print("Got here")
    fig = go.Figure(data=trace)
    if year == 2000:
        comp_year = "2015-2019 Average"
    comp_year = str(comp_year)
    comp_month = calendar.month_name[comp_month]
    #Make title
    if take_diff:
        if comp_type == 'annual':
            title = (lambda x,a: 'Annual Difference of {} between {} and 2020'.format(a,comp_year) if x not in 'ECON' else a.capitalize() + ' as of '+ str(year))(sub_group,parameter)
        else:
            title = (lambda x,a: 'Annual Difference of {} between {} {} and {} 2020'.format(a,comp_month,comp_year,comp_month) if x not in 'ECON' else a.capitalize() + ' as of '+date.strftime("%B %d, %Y"))(sub_group,parameter)

    else:
        if comp_type == 'annual':
            title = (lambda x, a: 'Annual Average of {} in {}'.format(a, str(year)) if x not in 'ECON' else a.capitalize() + ' as of ' + str(year))(sub_group, parameter)
        else:
            title = (lambda x,a: 'Annual Average of {} in {} {}'.format(a,comp_month, comp_year) if x not in 'ECON' else a.capitalize() + ' as of '+ str(year))(sub_group,parameter)


    fig.update_layout(title_text= title,autosize = True,
                      mapbox=dict(center=dict(lat=31.3915, lon=-100.1707),
                                  accesstoken=mapbox_key, style='streets',
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


@app.callback(Output('model','figure'),[Input('cty_map', 'clickData'),Input('parameter','value'),Input('sub-group','value'),Input('time_lines','value'),Input('years','value'),
                                        Input('avg_type','value')])
def display_click_data(clickData,parameter, sub_group,show_lines,years,avg_type):
    if clickData is not None and sub_group != 'ECON':
        years.append(2020)
        local_df = df[sub_group][parameter].copy()
        fips_number = clickData["points"][0]['location']
        fips_number = str(int(fips_number))
        print(fips_number)
        print(local_df.head())
        select = local_df[local_df['fips'] == fips_number].reset_index()
        select['date'] = pd.to_datetime(select['date'])
        ### Aggregate Data by county
        select = select.groupby(['date', 'fips', 'county']).mean().reset_index()
        dataframes = {}
        for year in years:
            if year == 'avg':
                print(select)
                dataframe = select[select['date'].dt.year.isin([2015,2016,2017,2018,2019])].copy()
                dataframe['date'] = dataframe['date'].apply(lambda x: x.replace(year=2020))
                dataframe = dataframe.groupby(['date','fips','county']).mean().reset_index()
            else:
                dataframe = select[select['date'].dt.year == year].copy()
                dataframe['date'] = dataframe['date'].apply(lambda x: x.replace(year=2020))

            if avg_type == 'weekly':
                dataframe = dataframe.groupby(['county', 'fips']).apply(
                        lambda x: x.resample('7D', on='date').mean()).reset_index()
            elif avg_type == 'monthly':
                dataframe['date'] = dataframe['date'].apply(lambda x: x.replace(day = 1))
                dataframe = dataframe.groupby(['date','county','fips']).mean().reset_index()
                print(dataframe)
            elif avg_type == 'rolling':
                dataframe = dataframe.pivot_table(index = 'date',columns = ['county','fips'],values = 'value')
                dataframe = dataframe.rolling(window = 14).mean()
                dataframe = dataframe.stack(level = [0,1]).reset_index(name = 'value')

            dataframes[year] = dataframe
        ##### Averaging interval
        print(years)
        print(dataframes)
        fig = px.line(title='Concentration of '+parameter + ' in ' + select.loc[0,'county'] + ' County',labels = {'date':'Date'})
        label_style = {2020:{'label':'2020','color':'#0921ED'},
                       2019:{'label':'2019','color':'#ED0925'}, 2018:{'label':'2018','color':'#09ED10'},2017:{'label':'2017','color':'#ED09ED'},2016:{'label':'2016','color':'#F6F79D'},2015:{'label':'2015','color':'#7EF3E5'},'avg':{'label':'Avg 2015-2019','color':'#94B8D5'}}
        for year, frame in dataframes.items():
            fig.add_trace(go.Scatter(
                x=frame['date'],
                y=frame['value'],
                name=label_style[year]['label'],
                mode='lines',
                line_color=label_style[year]['color']
                ))
        fig.update_layout(xaxis_title='Time',
                          yaxis_title=parameter+' Concentration ('+units[sub_group][parameter]+')',margin=dict(t=70,l=10,b=10,r=10))

        fig.update_traces(marker_size=20)
        # fig.update_xaxes(
        #     rangeslider_visible=True,
        #     rangeselector=dict(
        #         buttons=list([
        #             dict(count=1, label="1m", step="month", stepmode="backward"),
        #             dict(count=6, label="6m", step="month", stepmode="backward"),
        #             dict(count=1, label="YTD", step="year", stepmode="todate"),
        #             dict(count=1, label="1y", step="year", stepmode="backward"),
        #             dict(step="all")
        #         ])
        #     )
        # )
        fig.layout.yaxis.update(range=[min(select['value']), max(select['value'])])

        if show_lines:
            opening = 'State<br>Opening'
            closure = "State<br>Closure"
            fig.add_trace(go.Scatter(
                x=["2020-05-05","2020-05-05"],
                y=[min(select['value']), max(select['value'])],
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
        row = 0
        if parameter == 'pm2.5':
            x_val = 'pm2.5'
            x_title = 'PM2.5 Concentration (mg/m3)'
            case_title = 'COVID Cases/100k vs PM2.5 Concentration'
            death_title = 'COVID Deaths/100k vs PM2.5 Concentration'
            fig = make_subplots(rows=2, cols=1, specs=[[{"type": "scatter"}], [{"type": "scatter"}]], subplot_titles=(
                'COVID Cases/100k vs PM2.5 Concentration', 'COVID Deaths/100k vs PM2.5 Concentration'))
        else:
            x_val = 'bah'
            x_title = 'Black & Hispanic Percentage of Cases'
            case_title = 'COVID Cases/100k vs Black & Hispanic Percentage of Cases'
            death_title = 'COVID Death/100k vs Black & Hispanic Percentage of Cases'
            fig = make_subplots(rows=3, cols=1,
                                specs=[[{"type": "table"}], [{"type": "scatter"}], [{"type": "scatter"}]],
                                subplot_titles=(
                                    'Harris County Race Breakdown', case_title,
                                    death_title))
            frame = df['ECON']['harris_cty']
            frame_col = list(frame.columns)
            fig.add_trace(go.Table(header=dict(values=[x.capitalize() for x in list(frame.columns)],
                                               fill_color='paleturquoise',
                                               align='left'),
                                   cells=dict(values=[frame[frame_col[0]], frame[frame_col[1]], frame[frame_col[2]]],
                                              fill_color='lavender',
                                              align='left')), row=1, col=1)
            row += 1

        fig.append_trace(return_scatter_figure(x_val, 'cases/100k',x_title, 'COVID Cases/100k', case_title)['data'][0], row= row+1, col=1)
        fig.append_trace(get_trend_line(x_val, 'cases/100k',x_title, 'COVID Cases/100k', case_title), row= row+1, col=1)

        fig.update_xaxes(title_text=x_title, row=row+1, col=1)
        fig.update_yaxes(title_text= 'COVID Cases/100k', row=row+1, col=1)
        row += 1
        fig.append_trace(return_scatter_figure(x_val, 'deaths/100k', x_title, 'COVID Deaths/100k', death_title)['data'][0], row=row+1, col=1)
        fig.append_trace(get_trend_line(x_val, 'deaths/100k', x_title, 'COVID Deaths/100k', death_title), row=row+1, col=1)

        fig.update_xaxes(title_text=x_title, row=row + 1, col=1)
        fig.update_yaxes(title_text='COVID Deaths/100k', row=row + 1, col=1)
        fig.update_layout(autosize=True, margin=dict(t=40, l=80, r=18, b=30))
        fig['layout']['showlegend'] = False
        return fig

    #Need to seperate the two panels and resolve issue with stacking
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
# @app.callback(Output('econ-model','figure'),[Input('parameter','value'),Input('sub-group','value')])
# def display_death_scatter(parameter,sub_group):
#     print(parameter,sub_group)
#     if sub_group == 'ECON':
#         print("I am inside")
#         if parameter == 'pm2.5':
#             x_val = 'pm2.5'
#             x_title = 'PM2.5 Concentration (mg/m3)'
#             title = 'COVID Deaths/100k vs PM2.5 Concentration'
#         else:
#             x_val = 'bah'
#             x_title = 'Black & Hispanic Percentage of Cases'
#             title = 'COVID Deaths/100k vs Black & Hispanic Percentage of Cases'
#         print("I am in scatter")
#
#         return return_scatter_figure(x_val, 'deaths/100k',x_title, 'COVID Deaths/100k', title)
#     else:
#         return px.scatter()

def return_scatter_figure(x_parameter,y_parameter,x_title,y_title,title):
    local_df = df['ECON']['econ_data']
    names = {x_parameter: x_title, y_parameter: y_title}
    print(names)
    fig = px.scatter(local_df, x=x_parameter, y=y_parameter, hover_name='county', labels=names, title=title)

    X = np.array(local_df[x_parameter]).reshape(-1, 1)

    model = LinearRegression()
    model.fit(X, np.array(local_df[y_parameter]))

    x_range = np.linspace(X.min(), X.max(), 100)
    y_range = model.predict(x_range.reshape(-1, 1))
    print(x_range,y_range)
    #fig.update_layout(autosize = True,margin=dict(t=40,l=80,r=180,b=30))
    #fig.update_layout(style = {'padding': '6px 0px 0px 8px'})
    return fig

def get_trend_line(x_parameter,y_parameter,x_title,y_title,title):
    local_df = df['ECON']['econ_data']
    X = np.array(local_df[x_parameter]).reshape(-1, 1)

    model = LinearRegression()
    model.fit(X, np.array(local_df[y_parameter]))

    x_range = np.linspace(X.min(), X.max(), 100)
    y_range = model.predict(x_range.reshape(-1, 1))
    print(x_range,y_range)
    #fig = px.line(x=x_range, y=y_range,labels = {'x':x_title,'y':y_title},color='red')
    fig = go.Scatter(x=x_range, y=y_range,mode='lines', line=dict(color="#eb3434"),name = 'Regression')

    #fig.update_layout(autosize = True,margin=dict(t=40,l=80,r=180,b=30))
    #fig.update_layout(style = {'padding': '6px 0px 0px 8px'})
    return fig


# fig = make_subplots(rows=2, cols=1,specs=[[{"type": "table"}],[{"type": "scatter"}]])
#             fig.add_trace(go.Table(header=dict(values=[x.capitalize() for x in list(frame.columns)],
#                 fill_color='paleturquoise',
#                 align='left'),
#     cells=dict(values=[frame[frame_col[0]],frame[frame_col[1]],frame[frame_col[2]]],
#                fill_color='lavender',
#                align='left')),row=1, col=1)
#             fig.append_trace(return_scatter_figure(x_val, 'deaths/100k', x_title,
#                                                                                 'COVID Deaths/100k', death_title)['data'][0],row=2, col=1)