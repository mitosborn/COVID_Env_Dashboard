import dash_core_components as dcc
import pandas as pd
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from app import app
from database import data_importer
from sklearn.linear_model import LinearRegression
import geojson
import plotly.express as px
import os
import calendar
from plotly.subplots import make_subplots
import numpy as np

df = data_importer.master_df


PAGE_SIZE = 50
mapbox_key = 'pk.eyJ1IjoiY2hyaWRkeXAiLCJhIjoiY2ozcGI1MTZ3MDBpcTJ3cXR4b3owdDQwaCJ9.8jpMunbKjdq1anXwU5gxIw'
# Import jsons
root = os.path.dirname(os.path.abspath(__file__))
base = os.path.join(root, 'jsons')
with open(os.path.join(base, 'counties.json')) as f:
    counties = geojson.load(f)
superscript = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")
mg3 = '(\u03BCg/m3)'.translate(superscript)

# Define units for each environmental indicator
aq_units = {'Ozone': 'ppm', 'PM2.5': 'μg/m3',
            'NOx': 'ppb', 'CO': 'ppm', 'NO': 'ppm'}
econ_units = {"cumulative cases": 'cases', "cumulative deaths": 'deaths',
              "cumulative deaths per 100k": 'deaths/100k', "cumulative cases per 100k": 'cases/100k'}
ghg_units = {"CO2": "ppm", "CH4": "ppm"}
units = {"AQ": aq_units, "ECON": econ_units, "GHG": ghg_units}

layout = dcc.Graph(id='cty_map', style={"height": '95%'})
"""
get_map creates the central heat map. Returns map of Texas populated with user specified parameters.

Inputs:
    parameter: Current parameter selected
    sub_group: One of the following values [AQ, GHG, ECON]
    comp_type: Decides whether data displayed is per month or per year. Output of 'Interval' radio  
    comp_month: Selected month of data to be displayed if user selects 'Monthly' interval
    take_diff: Boolean deciding to display 2020 - selected year or only the selected year
"""


@app.callback(Output('cty_map', 'figure'), [Input('parameter', 'value'), Input('sub-group', 'value'), Input('date_interval', 'value'), Input('comp_year', 'value'), Input('date_range', 'value'), Input('mode', 'value')])
def get_map(parameter, sub_group, comp_type, comp_year, comp_month, take_diff):
    print(type(take_diff))
    print(take_diff)
    if sub_group == 'ECON':
        local_df = df['ECON']['econ_data']
        print(local_df.columns)
        fig = go.Figure()
        text_template = '<b>'+local_df['county'] + ' County</b><br>Cases/100k: ' + local_df['cases/100k'].round(
            2).astype(str) + '<br>Deaths/100k: ' + local_df['deaths/100k'].round(2).astype(str)

        if parameter == 'pm2.5':
            text_template += '<br>PM2.5: ' + \
                local_df['pm2.5'].round(2).astype(
                    str) + ' ' + mg3+'<extra></extra>'
            trace = go.Choroplethmapbox(geojson=counties,
                                        locations=local_df['fips'].astype(str),
                                        z=local_df['pm2.5'],
                                        colorscale='magma',
                                        colorbar_thickness=15, colorbar_len=0.7, colorbar_y=0.7,
                                        marker_line_color='white', name='pm 2.5 '+mg3, featureidkey='properties.FIPS',
                                        colorbar_title='PM 2.5 ' + mg3, colorbar_titlefont=dict(size=11),
                                        colorbar_tickfont=dict(size=11), hovertemplate=text_template, reversescale=True)

            fig.add_trace(trace)
            fig.update_layout(showlegend=True, title_text='Historical PM2.5 and COVID Incidence',
                              title_x=0.5, title_y=0.97, autosize=True, legend=dict(font=dict(size=11),
                                                                                    yanchor='bottom',
                                                                                    xanchor='right',
                                                                                    y=1, x=1, orientation='h'),
                              mapbox=dict(center=dict(lat=31.3915, lon=-100.1707),
                                          accesstoken=mapbox_key, style="streets",
                                          zoom=5.75))
        # Comparing race vs Cases/Deaths
        else:
            text_template += '<br>Population Minority: ' + \
                local_df['bah'].round(2).astype(str) + '%<extra></extra>'
            trace = go.Choroplethmapbox(geojson=counties,
                                        locations=local_df['fips'].astype(str),
                                        z=local_df['bah'], featureidkey='properties.FIPS',
                                        colorscale='oranges',
                                        colorbar_thickness=15, colorbar_len=0.7, colorbar_y=0.7,
                                        marker_line_color='white', name='Percent Minority: ',
                                        colorbar_title='Percentage', colorbar_titlefont=dict(size=11),
                                        colorbar_tickfont=dict(size=11), hovertemplate=text_template)

            fig.add_trace(trace)

            fig.update_layout(showlegend=True,
                              title_text='Percentage Population Minority vs. COVID incidence',
                              title_x=0.5, title_y=0.97,
                              autosize=True, legend=dict(font=dict(size=11),
                                                         yanchor='bottom',
                                                         xanchor='right',
                                                         y=1, x=1, orientation='h'),
                              mapbox=dict(center=dict(lat=31.3915, lon=-100.1707),
                                          accesstoken=mapbox_key, style="streets",
                                          zoom=5.75))
        print("These columns here")
        print(local_df.columns)
        # Cases/100k
        trace2 = go.Scattermapbox(lon=local_df['intptlong'], lat=local_df['intptlat'], mode='markers',
                                  marker=go.scattermapbox.Marker(symbol='circle', size=local_df[
                                      'cases/100k'],
            sizemode='area', sizeref=max(local_df['cases/100k']) / (
                                      50 ** 2),
            opacity=0.7, color='gray'),
            name='Cases per 100k Population', hoverinfo='skip')
        # Deaths/100k
        trace3 = go.Scattermapbox(lon=local_df['intptlong'], lat=local_df['intptlat'], mode='markers',
                                  marker=go.scattermapbox.Marker(symbol='circle',
                                                                 size=4*local_df['deaths/100k'], sizemode='area',
                                                                 sizeref=max(
                                                                     local_df['cases/100k']) / (50 ** 2),
                                                                 opacity=0.4, color='royalblue'),
                                  name='Deaths per 100k Population', hoverinfo='skip')

        # trace2.update_layout(title_x=0.5, title_y=0.9)

        fig.add_trace(trace2)
        fig.add_trace(trace3)

        return fig

    else:
        year = comp_year
        print(parameter)
        print(sub_group)
        local_df = df[sub_group][parameter].copy()

        if take_diff:
            colorscale = 'bluered'
            current = local_df[local_df['date'].dt.year == 2020].copy()
            current['month'] = current['date'].dt.month
            current = current.loc[:, ['fips', 'county', 'month', 'value']].groupby(
                ['fips', 'county', 'month']).mean().reset_index()
            past = local_df[local_df['date'].dt.year == year].copy()
            past['month'] = past['date'].dt.month
            past = past.loc[:, ['fips', 'county', 'month', 'value']].groupby(
                ['fips', 'county', 'month']).mean().reset_index()
            merged = current.merge(past, how='left', on=[
                                   'fips', 'county', 'month'], suffixes=['_current', '_past'])
            merged = merged.interpolate()
            print(past)
        else:
            colorscale = 'inferno'
            current = local_df[local_df['date'].dt.year == year].copy()
            current['month'] = current['date'].dt.month
            current = current.loc[:, ['fips', 'county', 'month', 'value']].groupby(
                ['fips', 'county', 'month']).mean().reset_index()
            merged = current

        print(current)
        print("Space")

        if comp_type == 'annual':
            merged = merged.groupby(['fips', 'county']).mean().reset_index()
        else:
            merged = merged[merged['month'] == comp_month]
        if take_diff:
            merged['value'] = merged['value_current'] - merged['value_past']
        local_df = merged

    title = (lambda x, a: parameter+' (' +
             units[x][a]+')' if x not in 'ECON' else 'COVID '+units[x][a].capitalize())(sub_group, parameter)
    trace = go.Choroplethmapbox(geojson=counties,
                                locations=local_df['fips'].astype(str),
                                z=local_df['value'].round(2),
                                colorscale=colorscale, featureidkey='properties.FIPS',
                                colorbar_thickness=20,
                                text=local_df['county'],
                                marker_line_color='white', customdata=local_df['fips'],
                                hovertemplate='<b>%{text} County</b>' +
                                              '<br><b>'+parameter +
                                                  '</b>: %{z} ' +
                                units[sub_group][parameter] +
                                '<extra></extra>',
                                colorbar_title_text=title)
    print("Got here")
    fig = go.Figure(data=trace)
    if year == 2000:
        comp_year = "2015-2019 Average"
    comp_year = str(comp_year)
    comp_month = calendar.month_name[comp_month]
    # Make title
    if take_diff:
        if comp_type == 'annual':
            title = "Annual Difference of {} between <br> {} and 2020".format(
                parameter, comp_year)
        else:
            title = "Annual Difference of {} between <br> {} {} and {} 2020".format(
                parameter, comp_month[0:3], comp_year, comp_month[0:3])

    else:
        if comp_type == 'annual':
            title = 'Annual Average of {} in {}'.format(
                parameter, str(comp_year))
        else:
            title = 'Annual Average of {} in {} {}'.format(
                parameter, comp_month[0:3], comp_year)

    fig.update_layout(title={'text': title, 'y': 0.95, 'x': 0.5, 'xanchor': 'center', 'yanchor': 'top'}, autosize=True,
                      mapbox=dict(center=dict(lat=31.3915, lon=-100.1707),
                                  accesstoken=mapbox_key, style='streets',
                                  zoom=4.75, layers=[{'sourcetype': 'geojson', 'opacity': .1,
                                                      'source': counties, 'type': "fill", 'color': None}]
                                  ))
    return fig


'''
display_click_data returns the timeseries plot on the right side of the dashboard

Inputs:
    clickData: FIPS code of county selected by user
    parameter: Parameter of data to be shown
    sub_group: Group [AQ, GHG, ECON] data comes from
    show_lines: Boolean to show lockdown begin and lockdown end lines
    years: Years to display on plot
    avg_type: [Daily, Weekly, Monthly] averaging types

Returns:
    Plot with the specified parameters 
'''


@app.callback(Output('model', 'figure'), [Input('cty_map', 'clickData'), Input('parameter', 'value'), Input('sub-group', 'value'), Input('time_lines', 'value'), Input('years', 'value'),
                                          Input('avg_type', 'value')])
def display_click_data(clickData, parameter, sub_group, show_lines, years, avg_type):
    if clickData is not None and sub_group != 'ECON':
        years.append(2020)
        local_df = df[sub_group][parameter].copy()
        fips_number = clickData["points"][0]['location']
        fips_number = str(int(fips_number))
        print(fips_number)
        print(local_df.head())
        select = local_df[local_df['fips'] == fips_number].reset_index()
        select['date'] = pd.to_datetime(select['date'])
        # Aggregate Data by county
        select = select.groupby(
            ['date', 'fips', 'county']).mean().reset_index()
        dataframes = {}
        for year in years:
            dataframe = select[select['date'].dt.year == year].copy()
            dataframe['date'] = dataframe['date'].apply(
                lambda x: x.replace(year=2020))
            if avg_type == 'weekly':
                dataframe = dataframe.groupby(['county', 'fips']).apply(
                    lambda x: x.resample('7D', on='date').mean()).reset_index()
            elif avg_type == 'monthly':
                dataframe['date'] = dataframe['date'].apply(
                    lambda x: x.replace(day=1))
                dataframe = dataframe.groupby(
                    ['date', 'county', 'fips']).mean().reset_index()
                print(dataframe)
            elif avg_type == 'rolling':
                dataframe = dataframe.pivot_table(
                    index='date', columns=['county', 'fips'], values='value')
                dataframe = dataframe.rolling(window=14).mean()
                dataframe = dataframe.stack(
                    level=[0, 1]).reset_index(name='value')

            dataframes[year] = dataframe
        # Averaging interval
        print(years)
        print(dataframes)
        fig = px.line(title='Concentration of '+parameter + ' in ' +
                      select.loc[0, 'county'] + ' County', labels={'date': 'Date'})
        label_style = {2020: {'label': '2020', 'color': '#0921ED'},
                       2019: {'label': '2019', 'color': '#ED0925'}, 2018: {'label': '2018', 'color': '#09ED10'}, 2017: {'label': '2017', 'color': '#ED09ED'}, 2016: {'label': '2016', 'color': '#F6F79D'}, 2015: {'label': '2015', 'color': '#7EF3E5'}, 2000: {'label': 'Avg 2015-2019', 'color': '#94B8D5'}}
        max_val = 0
        min_val = float('inf')
        # Add selected years to the plot
        for year, frame in dataframes.items():
            print("Columns are for the scatter:")
            print(frame.columns)

            #name_template = 'Year: ' + year +'<br>'+parameter+': '

            # Determine max and min of all data so we can set the axis without unused space
            try:
                max_val = max(max_val, max(frame['value']))
                min_val = min(min_val, min(frame['value']))
                fig.add_trace(go.Scatter(
                    x=frame['date'],
                    y=frame['value'],
                    name=label_style[year]['label'],
                    mode='lines',
                    line_color=label_style[year]['color'], hoverinfo='skip', hovertemplate='<b>'+label_style[year]['label']+'</b><br>Value: '+frame['value'].round(2).astype(str) + '<extra></extra>'
                ))
            except:
                print("Empty df")

        fig.update_layout(xaxis_title='Time',
                          yaxis_title=parameter +
                          ' Concentration (' +
                          units[sub_group][parameter] + ')',
                          margin=dict(t=70, l=10, b=10, r=10))

        fig.update_traces(marker_size=20)
        # Add space for max value to show on graph
        max_val = 1.01 * max_val
        min_val = .989 * min_val
        fig.layout.yaxis.update(range=[min_val, max_val])

        # Add opening and closure lines to graph if 'show timeline' is selected
        if show_lines:
            opening = 'State<br>Opening'
            closure = "State<br>Closure"
            fig.add_trace(go.Scatter(
                x=["2020-05-05", "2020-05-05"],
                y=[min_val, max_val],
                name=opening,
                mode='lines',
                line={'dash': 'dot', 'color': 'black', 'width': 4}
            ))
            fig.add_trace(go.Scatter(
                x=["2020-04-02", "2020-04-02"],
                y=[min_val, max_val],
                name=closure,
                mode='lines',
                line={'shape': 'linear', 'dash': 'dash',
                      'color': 'black', 'width': 4},
            ))

        return fig
    # If ECON is selected, display two scatterplots on the right side
    elif sub_group == 'ECON':
        row = 0
        if parameter == 'pm2.5':
            x_val = 'pm2.5'
            x_title = 'PM2.5 Concentration ' + mg3
            case_title = 'COVID Cases vs PM2.5 Concentration'
            death_title = 'COVID Deaths vs PM2.5 Concentration'
            fig = make_subplots(rows=2, cols=1, specs=[[{"type": "scatter"}], [{"type": "scatter"}]], subplot_titles=(
                'COVID Cases vs PM2.5 Concentration', 'COVID Deaths vs PM2.5 Concentration'), vertical_spacing=0.15)

        else:
            x_val = 'bah'
            x_title = 'Percentage Population Minority'
            case_title = 'COVID Cases vs Percentage Population Minority'
            death_title = 'COVID Deaths vs Percentage Population Minority'
            fig = make_subplots(rows=3, cols=1,
                                specs=[[{"type": "table"}], [
                                    {"type": "scatter"}], [{"type": "scatter"}]],
                                subplot_titles=(
                                    'Cost of COVID Deaths by Race/Ethnicity (Harris County)', case_title,
                                    death_title), vertical_spacing=0.15)
            frame = df['ECON']['harris_cty']
            frame_col = list(frame.columns)
            header = [x.capitalize() for x in list(frame.columns)]
            header[0] = 'Race/Ethnicity'
            fig.add_trace(go.Table(header=dict(values=header,
                                               fill_color='paleturquoise',
                                               align='left'),
                                   cells=dict(values=[frame[frame_col[0]], frame[frame_col[1]], frame[frame_col[2]]],
                                              fill_color='lavender',
                                              align='left')), row=1, col=1)
            row += 1

        fig.append_trace(return_scatter_figure(x_val, 'cases/100k', x_title,
                                               'COVID Cases/100k', case_title)['data'][0], row=row+1, col=1)
        fig.append_trace(get_trend_line(x_val, 'cases/100k'), row=row+1, col=1)

        fig.update_xaxes(title_text=x_title, row=row+1, col=1)
        fig.update_yaxes(title_text='COVID Cases/100k', row=row+1, col=1)
        row += 1
        fig.append_trace(return_scatter_figure(x_val, 'deaths/100k', x_title,
                                               'COVID Deaths/100k', death_title)['data'][0], row=row+1, col=1)
        fig.append_trace(get_trend_line(
            x_val, 'deaths/100k'), row=row+1, col=1)

        fig.update_xaxes(title_text=x_title, row=row + 1, col=1)
        fig.update_yaxes(title_text='COVID Deaths/100k', row=row + 1, col=1)
        fig.update_layout(autosize=True, margin=dict(
            l=80, r=18, b=0))
        fig['layout']['showlegend'] = False
        return fig

    # Need to seperate the two panels and resolve issue with stacking
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
            font_size=20)
    return fig


'''
return_scatter_figure creates a scatter plot comparing the data of the inputted
parameters.

Inputs:
    x_parameter,y_parameter: Explanatory and dependent variables
    x_title,y_title,title: Titles of the x_axis, y_axis, and plot
Return:
    Scatterplot containing data from the x and y parameters with the specified
    labels
'''


def return_scatter_figure(x_parameter, y_parameter, x_title, y_title, title):
    local_df = df['ECON']['econ_data']
    names = {x_parameter: x_title, y_parameter: y_title}
    print(names)
    fig = px.scatter(local_df, x=x_parameter, y=y_parameter,
                     hover_name='county', labels=names, title=title)
    return fig


'''
get_trend_line creates a scatter plot containing a linear regression
from the data representing the inputted parameters 

Inputs:
    x_parameter,y_parameter: Explanatory and dependent variables

Returns: 
    Scatter plot with a linear regression line 

'''
def get_trend_line(x_parameter, y_parameter):
    local_df = df['ECON']['econ_data']
    X = np.array(local_df[x_parameter]).reshape(-1, 1)

    # Fit data to model
    model = LinearRegression()
    model.fit(X, np.array(local_df[y_parameter]))

    # Reform linear regression for plotting
    x_range = np.linspace(X.min(), X.max(), 100)
    y_range = model.predict(x_range.reshape(-1, 1))

    # Create scatter plot containing linear regression
    fig = go.Scatter(x=x_range, y=y_range, mode='lines',
                     line=dict(color="#eb3434"), name='Regression')

    return fig

