import dash
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, title="TX Covid-19 Enviro-Map",
                suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.LUX])
server = app.server
