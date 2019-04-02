# Graphing stock data, custom date ranges, candlesticks, SMA's

import os #used to reference local time
import pandas as pd #manipulate imported data
import pandas_datareader.data as web #remote data access for pandas
import datetime #manipulate timeframes
from dateutil.relativedelta import relativedelta #extensions for datetime module
import dash #deploying analytical web app
import dash_core_components as dcc #extension for dash used for graph output
import dash_html_components as html #extension for dash used for html organizing
from dash.dependencies import Input, Output #used to allow input/output fields for search

app = dash.Dash(__name__)

server = app.server

app.layout = html.Div(children=[

    html.Div(id='output-graph'),
    
        html.Div(children=[
            html.Div(children='Enter stock ticker:'), 
            dcc.Input(id='input', value='TSLA', type='text'),
        ]),

        html.Div(children=[
            html.Div(children='Enter start date:'),
            dcc.Input(id='inputStart', value=datetime.date.today() - relativedelta(years=5), type='text'),
        ]),

        html.Div(children=[
            html.Div(children='Enter end date:'),
            dcc.Input(id='inputEnd', value=datetime.date.today(), type='text'),
        ]),
])

@app.callback(
    Output(component_id='output-graph', component_property='children'),
        [Input(component_id='input', component_property='value'),
        Input(component_id='inputStart', component_property='value'),
        Input(component_id='inputEnd', component_property='value')]
)

def update_graph(input_data, inputStart_data, inputEnd_data):
    df = web.DataReader(input_data.upper(), 'iex', inputStart_data, inputEnd_data)
    df['50ma'] = df['close'].rolling(window=50, min_periods=0).mean()
    df['200ma'] = df['close'].rolling(window=200, min_periods=0).mean()
    
    return dcc.Graph(
        figure={
            'data': [
                {'x':df.index, 'open':df.open, 'high':df.high, 'low':df.low, 'close':df.close, 'type':'candlestick', 'name':input_data.upper()},
                {'x':df.index, 'y':df['50ma'], 'type':'line', 'name':'50 SMA'},
                {'x':df.index, 'y':df['200ma'], 'type':'line', 'name':'200 SMA'},
                
                
            ],
            'layout':{
                'title': {
                    'text':"Investors Exchange (iEX) - {}\n".format(input_data.upper())
                },

                'xaxis':{
                    'title': 'Date',
                    'rangeslider':{'visible':False},
                },

                'yaxis':{
                    'title': 'Price',
                },
            }
        }
    )

if __name__ == '__main__':
    app.run_server(debug=True)
