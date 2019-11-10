import datetime
import math
import json
import pandas as pd
import numpy as np
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.graph_objects as go
from pprint import pprint

streetlight_df = pd.read_csv('/Users/teddyhaley/PycharmProjects/DeCodeCongestion/data/street-lighting-poles.csv',
                             sep=';')
streetlight_df['coordinates'] = streetlight_df['Geom'].apply(lambda x: json.loads(x)['coordinates'])
streetlight_df['lng'] = streetlight_df['Geom'].apply(lambda x: (json.loads(x)['coordinates'])[0])
streetlight_df['lat'] = streetlight_df['Geom'].apply(lambda x: (json.loads(x)['coordinates'])[1])
streetlight_df['node_number'] = np.arange(len(streetlight_df))

streetlight_df['distance_centre'] = np.sqrt(
    (streetlight_df['lat'] - 49.28171181258935) ** 2 + (-123.12331861143021 - streetlight_df['lng']) ** 2)

streetlight_df['distance_centre_norm'] = 1 - ((streetlight_df['distance_centre'] - min(
    streetlight_df['distance_centre'])) / (max(streetlight_df['distance_centre']) - min(
    streetlight_df['distance_centre'])))

external_stylesheets = [dbc.themes.FLATLY]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

# set layout options
app.title = 'LIGHTSPEED'

# Plotly mapbox public token
mapbox_access_token = "pk.eyJ1IjoicGxvdGx5bWFwYm94IiwiYSI6ImNqdnBvNDMyaTAxYzkzeW5ubWdpZ2VjbmMifQ.TXcBE-xg9BFdV2ocecc_7g"

logo = html.A(
    # Use row and col to control vertical alignment of logo / brand
    dbc.Row(
        [
            dbc.Col(
                html.Img(
                    src=app.get_asset_url('text_logo.png'),
                    height="60px",
                    style={'marginRight': '1em'})),
        ],
        align="center",
        no_gutters=True,
    ),
    href="https://github.com/TedHaley/DeCodeCongestion",
    target='_blank'
)

navbar = dbc.Navbar(
    children=[
        dbc.Row(
            [
                dbc.Col(logo,
                        width={"size": 2, "offset": 0, 'order': 1}),

                dbc.Col(
                    html.H1('LIGHT SPEED',
                            style={'color': 'white'})
                ),

            ],
            style={"width": "100%"},
            align='center'
        ),
    ],
    color="primary",
    dark=True,
    style={'marginBottom': '1em'}
)

body = html.Div(
    html.Div([

        html.Div(id='live-update-text'),

        dcc.Slider(
            id='time-slider',
            min=1,
            max=24,
            step=1,
            value=datetime.datetime.now().hour,
        ),

        html.Div(
            children=[
                dcc.Graph(id="map-graph",
                          style={'height': '70vh'}
                          ),
            ],
            style={'height': '70vh',
                   'marginBottom': '1em'}
        ),

        html.Div(id='data_table'),

        dcc.Interval(
            id='interval-component',
            interval=1 * 1000,  # in milliseconds
            n_intervals=0
        ),

        dcc.Interval(
            id='interval-map',
            interval=1 * 60 * 60 * 1000,  # in milliseconds
            n_intervals=0
        )

    ])
)

app.layout = html.Div([
    html.Div(children=[
        navbar,
        body
    ], id='page-content')
])


@app.callback(Output('live-update-text', 'children'),
              [Input('interval-component', 'n_intervals')])
def update_metrics(n):
    dt = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    date = dt.split(' ')[0]
    time = dt.split(' ')[1]

    return [
        html.H4(f"Date: {date}, Time: {time}"),
    ]


@app.callback(Output('map-graph', 'figure'),
              [Input('interval-map', 'n_intervals'),
               Input('time-slider', 'value')])
def update_map(n, time_value):
    now = datetime.datetime.now()

    streetlight_df['time_norm'] = time_value / 24
    streetlight_df['cos_time'] = streetlight_df['time_norm'].apply(lambda x: (math.cos(x * 2 * math.pi) * -2))
    streetlight_df['time_intensity'] = streetlight_df['distance_centre_norm'] * streetlight_df['cos_time']
    streetlight_df['time_intensity_norm'] = (streetlight_df['time_intensity'] - min(
        streetlight_df['time_intensity'])) / (max(streetlight_df['time_intensity']) - min(
        streetlight_df['time_intensity']))

    fig = go.Figure(go.Densitymapbox(lat=streetlight_df['lat'],
                                     lon=streetlight_df['lng'],
                                     z=streetlight_df['time_intensity_norm'],
                                     radius=1))

    fig.update_layout(mapbox_style="stamen-terrain",
                      mapbox_center_lon=streetlight_df['lng'][0],
                      mapbox_center_lat=streetlight_df['lat'][0],
                      mapbox_zoom=11
                      )

    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    return fig


@app.callback(
    Output('data_table', 'children'),
    [Input('map-graph', 'clickData')])
def em_optimizer_parameters(clickData):
    if clickData is not None:
        df = streetlight_df[streetlight_df['node_number'] == clickData['points'][0]['pointNumber']]

        print(df.columns)

        new_df = pd.DataFrame()
        new_df["Node"] = df['node_number']
        new_df['Neighbourhood'] = df['Geo Local Area']
        new_df['Latitude'] = df['lat']
        new_df['Longitude'] = df['lng']
        new_df['Distance Center'] = df['distance_centre_norm']
        # new_df['Devices in Network'] = df['time_intensity_norm'] + 5

        return dbc.Table.from_dataframe(new_df, striped=True, bordered=True, hover=True)


# table = dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True)


if __name__ == '__main__':
    app.run_server()
