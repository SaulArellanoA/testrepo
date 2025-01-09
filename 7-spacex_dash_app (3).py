# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36',
                   'font-size': 40}),

    # TASK 1: Add a dropdown list to enable Launch Site selection
    dcc.Dropdown(
        id='site-dropdown',
        options=[{'label': 'All Sites', 'value': 'All Sites'}] + [
            {'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()
        ],
        value='All Sites',
        placeholder="Select a Launch Site here",
        searchable=True
    ),
    html.Br(),

    # TASK 2: Add a pie chart to show the total successful launches count for all sites
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),

    # TASK 3: Add a slider to select payload range
    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        marks={i: f'{i}' for i in range(0, 10001, 2500)},
        value=[min_payload, max_payload]
    ),
    html.Br(),

    # TASK 4: Add a scatter chart to show the correlation between payload and launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# TASK 2:
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'All Sites':
        fig = px.pie(
            spacex_df[spacex_df['class'] == 1],
            names='Launch Site',
            title='Total Success Launches by Site'
        )
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        filtered_counts = filtered_df['class'].value_counts()
        fig = px.pie(
            names=filtered_counts.index.map({0: 'Failure', 1: 'Success'}),
            values=filtered_counts.values,
            title=f'Total Launches for site {entered_site}'
        )
    return fig

# TASK 4:
# TAREA 4: Agregar una función de callback para renderizar el gráfico de dispersión success-payload-scatter-chart
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [
        Input(component_id='site-dropdown', component_property='value'),
        Input(component_id='payload-slider', component_property='value')
    ]
)
def get_scatter_chart(entered_site, payload_range):
    # Desempaquetamos el rango [mínimo, máximo] seleccionado en el control deslizante
    low, high = payload_range
    
    # Creamos una máscara para filtrar los valores de payload (carga útil) que estén
    # dentro del rango indicado
    mask = (spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)
    filtered_df = spacex_df[mask]

    # Lógica para el caso "All Sites" o uno específico
    if entered_site == 'All Sites':
        # Para todos los sitios, dibujamos el gráfico de dispersión con la carga útil (x)
        # y la columna 'class' (y), coloreando por la categoría del cohete
        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title='Payload vs. Outcome for All Sites'
        )
    else:
        # Filtramos solo por el sitio seleccionado
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        # Construimos el gráfico con los mismos ejes, usando la data filtrada
        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title=f'Payload vs. Outcome for {entered_site}'
        )

    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
