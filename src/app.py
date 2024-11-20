import os
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
import math



# Construct the relative path to abc.xlsx
# current_dir = os.path.dirname(__file__)
# file_path = os.path.join(current_dir,'PowerPlants2024v2.xlsx')
# about_sheet = pd.read_excel(file_path, sheet_name='About')
# data = pd.read_excel(file_path, sheet_name='Power facilities')
url="https://github.com/kavan266/PowerPlantDash/raw/refs/heads/main/src/PowerPlants2024v2.xlsx"

data = pd.read_excel(url, sheet_name='Power facilities')


# Standardize text formatting in relevant columns to avoid issues with default values
data['Status'] = data['Status'].str.strip().str.title()
data['Type'] = data['Type'].str.strip().str.title()
data['Country/area'] = data['Country/area'].str.strip().str.title()
data['Region'] = data['Region'].str.strip().str.title()

# Ensure 'Start year' and 'Retired year' are numeric, replacing non-numeric entries with NaN
data['Start year'] = pd.to_numeric(data['Start year'], errors='coerce')
data['Retired year'] = pd.to_numeric(data['Retired year'], errors='coerce')

# Set year range for the slider based on the valid numeric values
year_min = int(data['Start year'].min())
year_max = int(data['Retired year'].max()) if not data['Retired year'].isna().all() else int(data['Start year'].max())

# Initialize the Dash app with Bootstrap theme
app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
server = app.server
# Layout of the Dash app
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Power Generation Capacity Dashboard", className="text-center text-teal mb-4"), width=12)
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Status", className="bg-teal"),
                dbc.CardBody([
                    dcc.Dropdown(
                        options=[{'label': status, 'value': status} for status in data['Status'].unique()],
                        value=['Operating'],
                        multi=True,
                        id='status-filter',
                        className="mb-2 dropdown",
                        style={'color': 'black'}
                    )
                ])
            ], className="bg-dark")
        ], md=3),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Type", className="bg-teal"),
                dbc.CardBody([
                    dcc.Dropdown(
                        options=[{'label': p_type, 'value': p_type} for p_type in data['Type'].unique()],
                        value=list(data['Type'].unique()),
                        multi=True,
                        id='type-filter',
                        className="mb-2 dropdown",
                        style={'color': 'black'}
                    )
                ])
            ], className="bg-dark")
        ], md=3),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Geography", className="bg-teal"),
                dbc.CardBody([
                    dcc.RadioItems(
                        options=[
                            {'label': 'Region', 'value': 'Region'},
                            {'label': 'Country/area', 'value': 'Country/area'}
                        ],
                        value='Country/area',
                        id='geography-filter',
                        className="mb-2 text-white"
                    )
                ])
            ], className="bg-dark")
        ], md=3),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("View Mode", className="bg-teal"),
                dbc.CardBody([
                    dcc.RadioItems(
                        options=[
                            {'label': 'Absolute Capacity', 'value': 'absolute'},
                            {'label': 'Percentage Share', 'value': 'percentage'}
                        ],
                        value='absolute',
                        id='view-mode-toggle',
                        className="mb-2 text-white"
                    )
                ])
            ], className="bg-dark")
        ], md=3)
    ], className="mb-4"),
    dbc.Row([
        dbc.Card([
            dbc.CardHeader("Year Range", className="bg-teal"),
            dbc.CardBody([
                dcc.RangeSlider(
                    min=year_min,
                    max=year_max,
                    value=[year_min, year_max],
                    marks={i: str(i) for i in range(year_min, year_max, 5)},
                    id='year-slider',
                    className="mb-2"
                )
            ])
        ], className="bg-dark")]),
    dbc.Row([
        dbc.Card([
            dbc.CardHeader("Total Capacity Range (Million MW: M MW) for Countries", className="bg-teal"),
            dbc.CardBody([
                dcc.RangeSlider(
                    min=0,
                    id='capacity-slider',
                    step=1000,
                    value=[100000,2500000],
                    className="mb-2"
                )
            ])
        ], className="bg-dark")]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='capacity-graph'), md=6, className="pr-2"),
        dbc.Col(dcc.Graph(id='map-graph'), md=6, className="pl-2")
    ], className="mb-4"),
    dbc.Row([
        dbc.Col(html.Div([
            html.H3("Dataset Information", className="text-teal"),
            html.P("This dashboard was created using the \"Global Energy Monitor, Global Integrated Power Tracker, September 2024 release\" data."),
            html.H4("Coverage", className="text-teal"),
            html.P("This dataset is a compilation of Global Energy Monitor’s eight dedicated power sector trackers."),
            html.Ul([
                html.Li("Coal: ≥30MW"),
                html.Li("Oil and gas: ≥50MW; ≥20MW in the European Union and the United Kingdom"),
                html.Li("Solar: ≥1MW"),
                html.Li("Wind: ≥10MW (≥1MW for some countries)"),
                html.Li("Nuclear: No threshold applied"),
                html.Li("Hydropower: ≥75MW"),
                html.Li("Bioenergy: ≥30MW"),
                html.Li("Geothermal: ≥1MW"),
            ]),
            html.H4("Definitions", className="text-teal"),
            html.Ul([
                html.Li("Type: One of eight power technology groups (coal, oil/gas, solar, wind, hydropower, nuclear, bioenergy, geothermal)."),
                html.Li("Country/area: Geographical data presented within various economic contexts."),
                html.Li("Region: One of five GEM-defined world regions."),
                html.Li("Capacity (MW): Total nameplate capacity of the project in megawatts."),
                html.Li("Status: One of 8 status categories (e.g., announced, operating, shelved, etc.)."),
                html.Li("Start year: Year the project was or will be commissioned."),
                html.Li("Retired year: Year the project was or will be decommissioned."),
            ])
        ]), width=12)
    ])
], fluid=True, className="bg-dark text-white")

# Callback to update the MW slider, capacity graph, and map based on user input
@app.callback(
    [Output('capacity-slider', 'min'),
     Output('capacity-slider', 'max'),
     Output('capacity-slider', 'value'),
     Output('capacity-slider', 'marks'),
     Output('capacity-graph', 'figure'),
     Output('map-graph', 'figure')],
    [Input('status-filter', 'value'),
     Input('type-filter', 'value'),
     Input('geography-filter', 'value'),
     Input('view-mode-toggle', 'value'),  # New input for view mode toggle
     Input('year-slider', 'value'),
     Input('capacity-slider', 'value')]
)
def update_figure(status, type_selection, geography, view_mode, year_range, capacity_range):
    filtered_data = data[
        data['Status'].isin(status) &
        data['Type'].isin(type_selection) &
        (data['Start year'] <= year_range[1]) &
        (data['Retired year'].isna() | (data['Retired year'] >= year_range[0]))
    ]
    total_capacity_data = filtered_data.groupby([geography])['Capacity (MW)'].sum().reset_index()
    min_capacity = 0
    max_capacity = math.ceil(total_capacity_data['Capacity (MW)'].max() * 1.01)
    if capacity_range is None or capacity_range == [0, 0]:
        capacity_range = [min_capacity, max_capacity]
    num_marks = 10
    step = max_capacity / (num_marks - 1)
    capacity_marks = {int(i * step): f"{(i * step) / 1e6:.2f}M" for i in range(num_marks)}
    total_capacity_data = total_capacity_data[
        (total_capacity_data['Capacity (MW)'] >= capacity_range[0]) &
        (total_capacity_data['Capacity (MW)'] <= capacity_range[1])
    ]
    if total_capacity_data.empty:
        empty_fig = px.bar(title="No data available for the selected filters.")
        empty_map_fig = px.scatter_mapbox(title="No data available for the selected filters.")
        empty_map_fig.update_layout(height=1000, margin=dict(l=10, r=10, t=50, b=10))
        return min_capacity, max_capacity, capacity_range, capacity_marks, empty_fig, empty_map_fig
    filtered_data = filtered_data.merge(total_capacity_data[[geography]], on=geography, how='inner')
    grouped_data = filtered_data.groupby([geography, 'Type'])['Capacity (MW)'].sum().reset_index()
    totals = grouped_data.groupby(geography)['Capacity (MW)'].sum().reset_index()
    grouped_data = grouped_data.merge(totals, on=geography, suffixes=('', '_total'))
    
    if view_mode == 'percentage':
        grouped_data['Capacity (MW)'] = (grouped_data['Capacity (MW)'] / grouped_data['Capacity (MW)_total']) * 100
        xaxis_title = "Percentage Share (%)"
        text_format = lambda x: f"{x:.1f}%"
    else:
        xaxis_title = "Total Capacity (Million MW)"
        text_format = lambda x: f"{x / 1e6:.2f}M"
    
    fig = px.bar(
        grouped_data,
        y=geography,
        x='Capacity (MW)',
        color='Type',
        title=f'Power Generation Capacity by {geography}',
        labels={'Capacity (MW)': xaxis_title, geography: geography},
        text=grouped_data['Capacity (MW)'].apply(text_format)
    )
    fig.update_traces(textposition='outside')
    fig.update_layout(
        legend=dict(orientation="h", y=-0.1, x=0.5, xanchor="center") if geography == "Region" else dict(orientation="h", y=-0.05, x=0.5, xanchor="center"),
        height=500 if geography == "Region" else 2000,
        margin=dict(l=10, r=10, t=50, b=10),
        xaxis_title=xaxis_title,
        yaxis=dict(
            categoryorder='total ascending',
            tickmode='linear',
            dtick=1
        )
    )

    map_fig = px.scatter_mapbox(
        filtered_data,
        lat='Latitude',
        lon='Longitude',
        hover_name='Plant / Project name',
        hover_data={'Capacity (MW)': True, 'Type': True},
        color='Type',
        size='Capacity (MW)',
        title="Power Plant Locations",
        mapbox_style="open-street-map",
        zoom=3
    )
    map_fig.update_layout(
        legend=dict(orientation="h", y=-0.05, x=0.5, xanchor="center"),
        height=1000,
        margin=dict(l=10, r=10, t=50, b=10),
    )
    return min_capacity, max_capacity, capacity_range, capacity_marks, fig, map_fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
