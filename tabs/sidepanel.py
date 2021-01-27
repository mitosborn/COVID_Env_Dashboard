import dash_core_components as dcc
import dash_html_components as html 
import dash_bootstrap_components as dbc
from app import app
from tabs import plots
from database import data_importer

df = data_importer.master_df
selection = {'Air Quality':'AQ','Greenhouse Gases':'GHG','COVID Cases/Deaths':'ECON'}
dashboard_spacing = {'margin-bottom':'1.2em'}

#Define averaging intervals available on the time series plot
interval = [{'label':'Daily','value':'daily'},{'label':'Weekly','value':'weekly'},{'label':'Monthly','value':'monthly'}]

#Define years available to display on the time series plot
years = [{'label': '2015', 'value': 2015}, {'label': '2016', 'value': 2016}, {'label': '2017', 'value': 2017},
                 {'label': '2018', 'value': 2018}, {'label': '2019', 'value': 2019},
                 {'label': '2015-2019 Average', 'value': 2000}]

#External links for data sources and Rice logo
AQ_source = 'https://www.tceq.texas.gov/agency/data/lookup-data/download-data.html'
GHG_source = "https://science.jpl.nasa.gov/EarthScience/index.cfm"
RICE_LOGO = "https://cdn.freelogovectors.net/wp-content/uploads/2019/10/rice-university-logo.png"

#Define the Navbar
navbar = dbc.Navbar(
    [
        html.A(
            # Create two columns: one containing the Rice logo, the other containing the dashboard title
            dbc.Row(
                [
                    dbc.Col(html.Img(src=app.get_asset_url('rice.png'), width = "190em",height="70em"),width=3),
                    dbc.Col(dbc.NavbarBrand("TX Environmental Impacts Due to COVID-19", className="h-100 d-inline-block", style={'font-size': '32px','font-family':'Trajan','color':'#00205B','font-weight':'bold','text-align':'justify'})),
                ],
                align="center",
                no_gutters=True,
            ),
            href="https://earthscience.rice.edu/", #External link to Rice ESCI website
        ),
        dbc.NavbarToggler(id="navbar-toggler"),
    ],
    color="light",
    dark=False, style = {"position": "sticky", "top":"0","width": "100%","background": "#fff","z-index": "2000"}
)

#Define the time series plot that resides on the right side of the dashboard
timeline_toggle =  dbc.Col([html.Div([html.H5('Show Timeline'), dbc.RadioItems(id ='time_lines', options = [{'label':'Show','value':True},{'label':'Hide','value':False}], value = True)])])
timeline_year_selector = dbc.Col(html.Div([html.H5("Compare Other Years"),dbc.Checklist(id = 'years',options = years,value=[2000],inline=True)]))
select_averaging_interval = dbc.Col(html.Div([html.H5("Averaging Interval"),dbc.RadioItems(id = 'avg_type',options = interval,value = 'daily')]))

#Put all the components together
time_series = dbc.Col(dbc.Container([dbc.Row(dbc.Col([dcc.Graph(id ='model', style={'height': '100%'})]), style = {'height': '92%'}), dbc.Row([timeline_toggle, timeline_year_selector, select_averaging_interval], style = {'height':'8%'}, id='ts_controls')], style={"height":"75vh"}, fluid=True), width =5)

#Define controls on left side of dashboard
select_env_group = html.Div([html.H3('Select group'), dcc.Dropdown(
                       id='sub-group',
                         options = [{'label':i,'value':selection[i]} for i in selection.keys()],
                         searchable = False, clearable = False,value ='AQ')], style = dashboard_spacing)
select_parameter = html.Div([html.H3('Select Parameter'), dcc.Dropdown(id = 'parameter',searchable = False,options = [{"label": "Air Quality - NOx", "value": "NOx"}],clearable = False,value = 'NOx')
                   ],style = dashboard_spacing)
select_water_layers = html.Div([html.H3('Layers',id = 'water_title'),dbc.RadioItems(id = 'wtr_layer',options=[
                {'label':'None','value':'None'},
                {'label': 'Major Aquifers', 'value': 'Major Aquifers'},
                {'label': 'River Basins', 'value': 'River Basins'},
                {'label': 'Watersheds', 'value': 'Watersheds'}], value='None')])

select_difference_mode = html.Div([html.H3("Mode"),dbc.Checklist(id = 'mode',options = [{'label':'Take difference between 2020 and other years','value':True}],value = [True],inline = True,switch=True)],style = dashboard_spacing)

#The comp year 2000 is used internally to represent the average of 2015-2019
select_comp_year = html.Div(dcc.Dropdown(id = 'comp_year',options = years,searchable = False,clearable = False, value=2000))

select_interval = html.Div([html.H3('Interval'),dbc.RadioItems(id = 'date_interval',options = [
                                                                                       {'label':'Monthly','value':'monthly'},{'label':'Annual','value':'annual'}],value = 'monthly')],style = dashboard_spacing)
select_month = html.Div([html.H3('Select Month', id = 'date_title'),dcc.Slider(id = 'date_range',min = 1, max = 12)],style = dashboard_spacing)

#Combine all controls into a control panel on the left side of the dashboard
controls = dbc.Col(html.Div([select_env_group,
                  select_parameter, select_water_layers, html.Div([select_difference_mode,html.Div([html.Div(id = 'mode_title'),select_comp_year],style = dashboard_spacing),select_interval,select_month],id = "econ_mode")], style={'marginBottom': 50, 'marginTop': 25, 'marginLeft':15, 'marginRight':25}),width=2)

#Import heat map from tab1
heat_map = dbc.Col(plots.layout, width=5)

#Define text that shows data sources
bottom_text = dbc.Col([dcc.Markdown('''---'''),html.Label([html.H6('Data Sources'),' Air Quality: ', html.A('TCEQ', href=AQ_source,target = "_blank"),', Greenhouse Gases: ',html.A('NASA',href = GHG_source,target="_blank")])
])

#Combine all components into master layout
layout = html.Div([navbar, dbc.Container([dbc.Row([controls, heat_map, time_series], style = {'height': '90%', 'margin': '1'}), dbc.Row([bottom_text], style = {'height': '10%'})], style={"height": "100%", "width": "100%"}, fluid=True)], style={"height": "100vh", "width": "100vw"})