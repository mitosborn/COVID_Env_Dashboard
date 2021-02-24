import dash_html_components as html
from dash.dependencies import Input, Output, State
from app import app, server
from tabs import sidepanel
from database import data_importer

df = data_importer.master_df
app.layout = sidepanel.layout
param_output = {'GHG': [{"label": "CO2", "value": "CO2"},
                        {"label": "CH4", "value": "CH4"}],
                'AQ': [{"label": "NOx", "value": "NOx"},
                       {"label": "PM2.5", "value": "PM2.5"},
                       {"label": "CO", "value": "CO"},
                       {"label": "Ozone", "value": "Ozone"}],
                'WQ': [{"label": "Dissolved Oxygen", "value": "Dissolved Oxygen"},
                       {"label": "Orthophosphate", "value": "Orthophosphate"}],
                'ECON': [{"label": "Race/Ethnicity", "value": "race"},
                         {"label": "PM2.5", "value": "pm2.5"}]}
show_water = lambda x: {'display': 'block'} if x == 'WQ' else {'display': 'none'}
show_econ = lambda x: {'display': 'none'} if x == 'ECON' else {'display': 'block'}
show_ts = lambda x: {'display': 'block'} if x == 'ECON' else {'display': 'none'}
hide_ts = lambda x: {'display': 'none'} if x == 'ECON' else {'display': 'flex'}

'''
Function that updates the parameters shown. If the selected group is not water, hides the layer tab.
Additionally, the function always sets layers to none to prevent layers showing after water is deselected.

Input: 
    selected_group: String representing currently selected sub-group of data (GHG, ECON, AQ)
    
Return:
    CSS styling for that respective group. When AQ or GHG are selected, show the comparison year, interval,
    month selector, mode selector, and their titles. When ECON is selected, hide AQ/GHG selectors and update
    selected parameter options to be Race/Ethnicity and PM2.5
    
'''


@app.callback([Output('parameter', 'options'), Output('parameter', 'value'), Output('water_title', 'style'),
               Output('wtr_layer', 'style'), Output('wtr_layer', 'value'), Output('econ_mode', 'style'),
               Output('ts_controls', 'style')], [Input('sub-group', 'value')])
def return_parameters(selected_group):
    return param_output[selected_group], param_output[selected_group][0]['value'], show_water(
        selected_group), show_water(selected_group), 'None', show_econ(selected_group), hide_ts(selected_group)


'''
return_month_timeline creates the list of months the user can select such that the list of months is limited
by the amount of data available. Ex: We can't select December if we do not have data for it. If the selected options
include ECON for group or 'yearly' for interval, we hide the timeline and its respective title (Select month) 

Inputs:
    interval: String that indicates user is displaying data on the heatmap by month
              Value == 'monthly' if a timeline needs to be returned. 
    parameter: Environmental indicator the user selected 
    group: Sub-group (ECON, GHG, AQ) of data the user has selected. If ECON, hide the timeline and its title
    take_difference: List containing value indicating if user is taking difference of 2020 and a past year
                     or if they are only viewing a single year. If true, we must limit the months available
                     by the shorter of the two years we have data for (2020)  
    year_selected: Year to compare 2020 data to or the year to display on its own if take_difference is False

Output:
    Dictionary representing the labels and values for the timeline titled "Select Month", 
    int representing max value for date range (The most recent month available (1-12))
    Dictionary representing style for date range and its title (block or hidden)
    int that defines current value of date_range (the first month available)
'''


@app.callback([Output('date_range', 'marks'), Output('date_range', 'max'), Output('date_range', 'style'),
               Output('date_title', 'style'), Output('date_range', 'value')],
              [Input('date_interval', 'value'), Input('parameter', 'value'), Input('sub-group', 'value'),
               Input('mode', 'value'), Input('comp_year', 'value')])
def return_month_timeline(interval, parameter, group, take_difference, year_selected):
    # print(interval, group, parameter)
    base_year = 2020
    # If take_difference is empty, we are comparing 2020 to another year
    if len(take_difference) == 0:
        base_year = year_selected
    # If the interval is monthly, we need to output a monthly timeline based on the options the user has selected
    if interval == 'monthly' and group != 'ECON':
        # print(group, parameter)

        # Create a dictionary of months based on the base_year (2020 if in comparison mode; otherwise,
        # the year_selected)
        local_df = df[group][parameter]
        local_df = local_df[local_df['date'].dt.year == base_year]
        months = set(local_df['date'])
        max_month = list(map(lambda x: x.month, months))
        # Create dictionary of labels for months and style each label such that it is rotated 45 degrees
        to_return = {val.month: {'label': val.strftime("%b"), 'style': {"transform": "rotate(45deg)"}} for val in
                     months}
        return to_return, max(max_month), {'display': 'block'}, {'display': 'block'}, 1
    # If the user is not viewing data monthly or the selected group is ECON, return filler values for the timeline and
    # hide the selectors and titles that represent monthly data selection
    return {
               0: {'label': '0 °C', 'style': {'color': '#77b0b1'}},
               26: {'label': '26 °C'},
               37: {'label': '37 °C'},
               100: {'label': '100 °C', 'style': {'color': '#f50'}}
           }, 150, {'display': 'none'}, {'display': 'none'}, 1

'''
Returns the years available for viewing based on if the user is in comparison mode. If comparison mode is selected,
we want to only compare 2020 to past years (2015-2019) and not to itself. Otherwise, the user is viewing a singular 
year, meaning let them select from all years available (2015-2020)

Input:
    compare_mode: the current mode the user is in: compare mode or view a single year
    
Return:
    Dictionary representing the years the user can select from and HTML to set the title as
    "Viewing Year" or "Comparison Year"
'''
@app.callback([Output('comp_year', 'options'), Output('mode_title', 'children')], Input('mode', 'value'))
def update_year_comparison_selector(compare_mode):
    # If compare_value is empty, we are in comparison mode: omit 2020 from the year selection
    if len(compare_mode) > 0:
        return [{'label': '2015', 'value': 2015}, {'label': '2016', 'value': 2016}, {'label': '2017', 'value': 2017},
                {'label': '2018', 'value': 2018}, {'label': '2019', 'value': 2019},
                {'label': '2015-2019 Average', 'value': 2000}], html.H3("Comparison Year")
    # Else, we are not in compare mode; include 2020 and change the title to "Viewing Year"
    return ([{'label': '2015', 'value': 2015}, {'label': '2016', 'value': 2016}, {'label': '2017', 'value': 2017},
             {'label': '2018', 'value': 2018}, {'label': '2019', 'value': 2019},
             {'label': '2015-2019 Average', 'value': 2000}, {'label': '2020', 'value': 2020}],
            html.H3("Viewing Year"))

@app.callback(
    Output("modal", "is_open"),
    [Input("open", "n_clicks"), Input("close", "n_clicks")],
    [State("modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open





if __name__ == '__main__':
    app.run_server(debug=True, host = '127.0.0.1')



