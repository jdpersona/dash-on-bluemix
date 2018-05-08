
import dash
import numpy as np
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd


daily_df = pd.read_csv("https://raw.githubusercontent.com/jdpersona/Dash_Apps/master/daily_df.csv")


app = dash.Dash(__name__)
server = app.server

app.css.append_css({'external_url': 'https://codepen.io/chriddyp/pen/dZVMbK.css'})


app.layout = html.Div(className='container', children=[
    html.H1('NPS Changes Overtime'),
    html.Hr(),
    
   html.Div(className='two columns', children=[ 
   dcc.Dropdown(id='items',
     options=[
        {'label': '30 Day', 'value': 30},
        {'label': '60 Day', 'value': 60},
        {'label': '90 Day', 'value': 90}
        ],
         value = 30
         ), 
    ], style = {'width' : '28%'}),


    html.Div( dcc.Graph(id='graph'), className='ten columns' )

])




@app.callback(Output('graph', 'figure'), [Input('items', 'value')])    
def update_graph(items):
    window1 = daily_df.rolling(items).sum().dropna()
   # Compute NPS
    window1['total'] = window1.detractors + window1.passives + window1.promoters
    window1['NPS'] = 100*((window1.promoters/window1.total) - (window1.detractors/window1.total))
    window1['DetPct'] = window1.detractors/window1.total
    window1['ProPct'] = window1.promoters/window1.total
    window1['SE_NPS'] = 100*np.sqrt((window1.ProPct*(1-window1.ProPct) + window1.DetPct*(1-window1.DetPct) + 2*window1.ProPct*window1.DetPct)/window1.total)                 
    window1['MoE'] = 1.96*window1.SE_NPS
    window1['NPS_low'] = window1.NPS - window1.MoE
    window1['NPS_high'] = window1.NPS + window1.MoE
  # Plot 10-day NPS with MoE boundaries\
   # Lists to use in plot
    NPS = list(window1.NPS)
    NPS_low = list(window1.NPS_low)
    NPS_high = list(window1.NPS_high)
    
    upper_bound = go.Scatter(
        name='Upper Bound',
        x=window1.date,
        y=window1.NPS_high,
        mode='lines',
        marker=dict(color="444"),
        line=dict(width=0),
        fillcolor='rgba(68, 68, 68, 0.3)',
        fill='tonexty' )

    trace = go.Scatter(
      name='Measurement',
      x=window1.date,
      y=window1.NPS,
      mode='lines',
      line=dict(color='rgb(31, 119, 180)'),
      fillcolor='rgba(68, 68, 68, 0.3)',
      fill='tonexty')
    
    
    lower_bound = go.Scatter(
     name='Lower Bound',
     x=window1.date,
     y=window1.NPS_low,
     marker=dict(color="444"),
     line=dict(width=0),
     mode='lines' )

    # Trace order can be important
      # with continuous error bars
    data = [lower_bound, trace, upper_bound]

    return {
        'data': data,
        'layout': go.Layout(
            yaxis={'title': 'Daily NPS Score'},
            margin={'l': 40, 'b': 40, 't': 10, 'r': 10}
            )

            }



if __name__ == '__main__':
    app.run_server(debug=True, threaded=True)
    
    
    
    
    
    
    
    
    
    
    
