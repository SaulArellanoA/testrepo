#!/usr/bin/env python
# coding: utf-8

import dash
import more_itertools
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

# Load the data using pandas
data = pd.read_csv(
    'https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/'
    'IBMDeveloperSkillsNetwork-DV0101EN-SkillsNetwork/Data%20Files/'
    'historical_automobile_sales.csv'
)

# Initialize the Dash app
app = dash.Dash(__name__)

#---------------------------------------------------------------------------------
# 1) Create the dropdown menu options
dropdown_options = [
    {'label': 'Yearly Statistics', 'value': 'Yearly Statistics'},
    {'label': 'Recession Period Statistics', 'value': 'Recession Period Statistics'}
]

# 2) List of years (1980 to 2023)
year_list = [i for i in range(1980, 2024, 1)]

#---------------------------------------------------------------------------------------
# 3) Create the layout of the app
app.layout = html.Div([
    # TASK 2.1: Add a title to the dashboard
    html.H1(
        "Automobile Sales Statistics Dashboard",
        style={'textAlign': 'left', 'color': '#503D36', 'font-size': 24}
    ),
    
    # TASK 2.2: Add two dropdown menus
    html.Div([
        html.Label("Select Statistics:"),
        dcc.Dropdown(
            id='dropdown-statistics',
            options=dropdown_options,
            value='Select Statistics',          # Default value
            placeholder='Select a report type'  # Placeholder text
        )
    ]),

    html.Div(
        dcc.Dropdown(
            id='select-year',
            options=[{'label': i, 'value': i} for i in year_list],
            placeholder='Select-year',     # <-- Se agregó placeholder
            value='Select-year'           # <-- Se cambió a 'Select-year'
        )
    ),

    # TASK 2.3: Add a division for output display
    html.Div([
        html.Div(
            id='output-container',
            className='chart-grid',
            style={'display': 'flex', 'flex-wrap': 'wrap'}  # Example styling
        ),
    ])
])

#---------------------------------------------------------------------------------------
# TASK 2.4: Creating Callbacks
# 4a) Define the callback function to update (enable/disable) the Year dropdown
@app.callback(
    Output(component_id='select-year', component_property='disabled'),
    Input(component_id='dropdown-statistics', component_property='value')
)
def update_input_container(selected_statistics):
    """
    If 'Yearly Statistics' is chosen, enable (disabled=False).
    Otherwise, disable (disabled=True).
    """
    if selected_statistics == 'Yearly Statistics':
        return False
    else:
        return True

#---------------------------------------------------------------------------------------
# 4b) Callback for plotting
@app.callback(
    Output(component_id='output-container', component_property='children'),
    [
        Input(component_id='dropdown-statistics', component_property='value'),
        Input(component_id='select-year', component_property='value')
    ]
)
def update_output_container(selected_statistics, input_year):
    """
    Produce different plots depending on whether 'Yearly Statistics' 
    or 'Recession Period Statistics' is selected, and on the chosen year.
    """
    # If 'Recession Period Statistics' is chosen:
    if selected_statistics == 'Recession Period Statistics':
        # Filter data for recession periods (Recession == 1)
        recession_data = data[data['Recession'] == 1]

        # TASK 2.5: Create and display graphs for Recession Report Statistics
        
        # Plot 1: Automobile sales fluctuate over Recession Period (year wise)
        yearly_rec = (recession_data.groupby('Year')['Automobile_Sales']
                                     .mean().reset_index())
        R_chart1 = dcc.Graph(
            figure=px.line(
                yearly_rec,
                x='Year',
                y='Automobile_Sales',
                title="Average Automobile Sales fluctuation over Recession Period"
            )
        )

        # Plot 2: Average number of vehicles sold by vehicle type
        average_sales = (recession_data.groupby('Vehicle_Type')['Automobile_Sales']
                                      .mean().reset_index())
        R_chart2 = dcc.Graph(
            figure=px.bar(
                average_sales,
                x='Vehicle_Type',
                y='Automobile_Sales',
                title="Average Vehicles Sold by Vehicle Type (Recession)"
            )
        )

        # Plot 3: Pie chart for total advertising expenditure by vehicle type
        exp_rec = (recession_data.groupby('Vehicle_Type')['Advertising_Expenditure']
                                 .sum().reset_index())
        R_chart3 = dcc.Graph(
            figure=px.pie(
                exp_rec,
                values='Advertising_Expenditure',
                names='Vehicle_Type',
                title="Total Advertising Expenditure by Vehicle Type (Recession)"
            )
        )

        # Plot 4: Bar chart for effect of unemployment rate on vehicle type and sales
        unemp_data = (recession_data.groupby(['Vehicle_Type', 'unemployment_rate'])
                                    ['Automobile_Sales'].mean().reset_index())
        R_chart4 = dcc.Graph(
            figure=px.bar(
                unemp_data,
                x='Vehicle_Type',
                y='Automobile_Sales',
                color='unemployment_rate',  # shows rate as a color legend
                title='Effect of Unemployment Rate on Vehicle Type and Sales (Recession)'
            )
        )

        # Return the four charts in 2x2 layout
        return [
            html.Div(
                className='chart-item',
                children=[html.Div(children=R_chart1), html.Div(children=R_chart2)],
                style={'display': 'flex'}
            ),
            html.Div(
                className='chart-item',
                children=[html.Div(children=R_chart3), html.Div(children=R_chart4)],
                style={'display': 'flex'}
            )
        ]

    # If 'Yearly Statistics' is chosen and a valid year is selected:
    elif (input_year and selected_statistics == 'Yearly Statistics'):
        yearly_data = data[data['Year'] == int(input_year)]

        # TASK 2.6: Create and display graphs for Yearly Report Statistics

        # Plot 1: Yearly Automobile sales (line chart) for the whole period
        yas = data.groupby('Year')['Automobile_Sales'].mean().reset_index()
        Y_chart1 = dcc.Graph(
            figure=px.line(
                yas,
                x='Year',
                y='Automobile_Sales',
                title="Average Automobile Sales Over All Years"
            )
        )

        # Plot 2: Total Monthly Automobile sales using line chart for the selected year
        monthly_sales = (yearly_data.groupby('Month')['Automobile_Sales']
                                    .sum().reset_index())
        Y_chart2 = dcc.Graph(
            figure=px.line(
                monthly_sales,
                x='Month',
                y='Automobile_Sales',
                title=f"Total Monthly Automobile Sales for {input_year}"
            )
        )

        # Plot 3: Average number of vehicles sold by vehicle type in the selected year
        avr_vdata = (yearly_data.groupby('Vehicle_Type')['Automobile_Sales']
                                 .mean().reset_index())
        Y_chart3 = dcc.Graph(
            figure=px.bar(
                avr_vdata,
                x='Vehicle_Type',
                y='Automobile_Sales',
                title=f"Average Vehicles Sold by Vehicle Type in {input_year}"
            )
        )

        # Plot 4: Total advertisement expenditure for each vehicle type (pie chart)
        exp_data = (yearly_data.groupby('Vehicle_Type')['Advertising_Expenditure']
                                .sum().reset_index())
        Y_chart4 = dcc.Graph(
            figure=px.pie(
                exp_data,
                values='Advertising_Expenditure',
                names='Vehicle_Type',
                title=f"Advertising Expenditure by Vehicle Type in {input_year}"
            )
        )

        # Return the four charts in 2x2 layout
        return [
            html.Div(
                className='chart-item',
                children=[html.Div(children=Y_chart1), html.Div(children=Y_chart2)],
                style={'display': 'flex'}
            ),
            html.Div(
                className='chart-item',
                children=[html.Div(children=Y_chart3), html.Div(children=Y_chart4)],
                style={'display': 'flex'}
            )
        ]

    # If no valid selection or no specific match, return nothing
    else:
        return None

#---------------------------------------------------------------------------------------
# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)
