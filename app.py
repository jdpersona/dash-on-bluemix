import pandas as pd
import numpy as np
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from flask import Flask

daily_df = pd.read_csv("https://raw.githubusercontent.com/jdpersona/Dash_Apps/master/daily_df.csv")

app = dash.Dash(__name__)
server = app.server

app.css.append_css({"external_url": 'https://codepen.io/jdpersona/pen/OZrWLO.css'})


app.css.append_css({"external_url": 'https://codepen.io/jdpersona/pen/GGRxLP.css'})


app.layout = html.Div(children=[     

html.Hr(),  
#html.Div( dcc.Graph(id='graph'), style={"float": "left"}),
html.Div([ 
    
html.Div([  
html.Br(),
dcc.Slider(
        id='items',
        min=30,
        max=90,
        step=30,
        value=30,
        marks = {30:'30 day', 60:'60 day', 90:'90 day'}
    )    
], style = {'width': '20%', "float":"right", "margin-top":"10px", "margin-bottom":"30px"}),
    
    html.H4("Discover NPS Trend"),
    html.Br(),
    dcc.Graph(id='graph')], style={"width" :"70%", "float": "left"}),

    
html.Div([  
 
  html.H4("Date Comparison"),  
  
  html.Br(),
  html.Div([  
  dcc.DatePickerRange(
    id ='my-date-picker-range',
    max_date_allowed = max(daily_df.date),
    end_date= max(daily_df.date),
    start_date = min(daily_df.date),
    #display_format="MMYY DD",
    start_date_placeholder_text="Chose Date 1",
    end_date_placeholder_text="Chose Date 2",
    )], style = {"margin-left":"60px", "opacity": "0.8"}),
    
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    

    
 dcc.Graph(id='output-container-date-picker-range', className="table") 
   
], style = {"float":"right","width": "30%"}),
  
    
    
html.Div([ 
    
    html.H5("Respondent by Count and Proportion"),
    dcc.Graph(id='bar_graph')], style={"width" :"35%", "float": "left"}),
    
    
html.Div([dcc.Graph(id='pie_graph')], style={"width" :"35%","float": "left"})
 
], style = {"width":"90%", "margin-left": "10px", "margin-right": "10px", "margin-top": "10px", "margin-bottom":"30px", "backgroundColor" : "grey"})

###################### First Callback ############################

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
        name='NPS Upper Bound',
        x=window1.date,
        y=window1.NPS_high,
        line = dict(color = '#7F7F7F'),
        mode="lines",
        opacity = 0.2)
         
    trace = go.Scatter(
      name='NPS Score',
      x=window1.date,
      y=window1.NPS,
      line=dict(color='#6AB187'),
      opacity= 0.8)
    
    lower_bound = go.Scatter(
     name='NPS Lower Bound',
     x=window1.date,
     y=window1.NPS_low,
     line = dict(color = '#7F7F7F'),
     opacity = 0.2)

   #Trace order can be important
   # with continuous error bars
    data = [lower_bound, trace, upper_bound]

    return {
        'data': data,
        
        'layout': go.Layout(
            yaxis={'title': 'Daily NPS Score', 'showgrid': False},
            margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
            plot_bgcolor='#F1F1F1', 
            xaxis=dict(
         rangeselector=dict(
            buttons=list([
                dict(count=1,
                     label='1m',
                     step='month',
                     stepmode='backward'),
                dict(count=6,
                     label='6m',
                     step='month',
                     stepmode='backward'),
                dict(step='all')
            ])
        ),
        rangeslider=dict(),
        type='date'
    )
            
            )

           
    }


#########################  second items ######################

@app.callback(Output('bar_graph', 'figure'), [Input('items', 'value')])    
def update_graph(items):
    df = daily_df.rolling(items).sum().dropna()
    df = df[['promoters','passives','detractors']].tail(1)
    nums = [list(i) for i in df.values]
    trace0 = go.Bar(
    x=['promoters', 'passives','detractors'],
    y=[nums[0][0],nums[0][1],nums[0][2]],
    text=['Promoters', 'Passives', 'Detractors'],
    marker=dict(
        color= ['#AC3E31', '#DBAE58', '#6AB187'],
        line=dict(
            color= '#F1F1F1',
            width=1.5,
          )
       ),
       opacity=0.6
       )
    
    data = [trace0]
    return {
        'data': data,
        'layout': go.Layout ({'boxgap':"0.2"}, 
                              plot_bgcolor='#F1F1F1')
         }
 
    
    
 #########################  3rd items ######################   
@app.callback(Output('pie_graph', 'figure'), [Input('items', 'value')])    
def update_graph(items):
    df = daily_df.rolling(items).sum().dropna()
    df = df[['promoters','passives','detractors']].tail(1)
    nums = [list(i) for i in df.values]
    labels = ['promoters', 'passives', 'detractors']
    values = [nums[0][0],nums[0][1],nums[0][2]]
    colors = ['#AC3E31', '#DBAE58', '#6AB187']
    trace = go.Pie(labels=labels, values=values,marker=dict(colors=colors), textfont=dict(color='#F1F1F1'))
    data = [trace]
    return {
        'data': data,
        
        #'layout' : go.Layout (plot_bgcolor='#F1F1F1')             
                            
         }




@app.callback(
     dash.dependencies.Output('output-container-date-picker-range', 'figure'),
     [dash.dependencies.Input('items','value'),    dash.dependencies.Input('my-date-picker-range', 'start_date'),
     dash.dependencies.Input('my-date-picker-range', 'end_date')])

def update_output(items, start_date, end_date):
    window1 = daily_df.rolling(items).sum().dropna()
    window1['total'] = window1.detractors + window1.passives + window1.promoters
    window1['NPS'] = 100*((window1.promoters/window1.total) - (window1.detractors/window1.total))
    window1['DetPct'] = window1.detractors/window1.total
    window1['ProPct'] = window1.promoters/window1.total
    window1['SE_NPS'] = 100*np.sqrt((window1.ProPct*(1-window1.ProPct) + window1.DetPct*(1-window1.DetPct) + 2*window1.ProPct*window1.DetPct)/window1.total)                 
    window1['MoE'] = 1.96*window1.SE_NPS
    window1['NPS_low'] = window1.NPS - window1.MoE
    window1['NPS_high'] = window1.NPS + window1.MoE
    window2 = window1[(window1.date == start_date) | (window1.date ==  end_date)]
    window2.reset_index(inplace=True)
    headerColor = 'grey'
    rowEvenColor = 'lightgrey'
    rowOddColor = 'white'
    if len(window2.NPS) < 2 :
        trace = go.Table(
        header=dict(values=['NPS', 'Comment'], fill = dict(color = headerColor),font = dict(color = 'white', size = 12)),
        cells=dict(values=[ ['NA'],["No Data"] ])              
        )
        data = [trace] 
        return {
           'data': data
        }

    elif  round(window2.loc[0,"NPS"]) >  round(window2.loc[1,"NPS"]):
        
        trace = go.Table(
        header=dict(values=['NPS scores', ' NPS Decrease'], fill = dict(color = headerColor), font = dict(color = 'white', size = 12)),
        cells=dict(values=[ [ round(window2.loc[0,"NPS"]) , round(window2.loc[1,"NPS"])],   [ round(window2.loc[0,"NPS"]) - round(window2.loc[1,"NPS"])]], font = dict(color = 'red', size = 12) )
         )
        data = [trace] 
        return {
        'data': data
        }
    #return "Day 1 NPS : {} |Day 2 NPS: {}|increased by {}".format(round(window2.loc[0,"NPS"],1),round(window2.loc[1,"NPS"],1),       
                                                                           #round(window2.loc[0,"NPS"] - window2.loc[1,"NPS"], 1))      
    elif  round(window2.loc[0,"NPS"]) <  round(window2.loc[1,"NPS"]):
        trace = go.Table(
        header=dict(values=['NPS Scores', ' NPS Increase'], fill = dict(color = headerColor), font = dict(color = 'white', size = 12)),
        cells=dict(values=[[round(window2.loc[0,"NPS"]), round(window2.loc[1,"NPS"])], [ '', round(window2.loc[1,"NPS"]) - round(window2.loc[0,"NPS"])]  ], font = dict(color = 'green', size = 12) )
         )
        data = [trace] 
        return {
        'data': data
        }

      #return "Day 1 NPS : {}| Day 2 NPS: {} |decreased by {}".format(round(window2.loc[0,"NPS"],1),round(window2.loc[1,"NPS"],1),round(window2.loc[1,"NPS"] - window2.loc[0,"NPS"], 1))
    else:
        trace = go.Table(
        header=dict(values=['NPS Scores', 'No change'], fill = dict(color = headerColor), font = dict(color = 'white', size = 12)),
        cells=dict(values=[ [round(window2.loc[0,"NPS"]), round(window2.loc[1,"NPS"])],[ round(window2.loc[1,"NPS"]) - round(window2.loc[0,"NPS"]) ]  ] )
         )
        data = [trace] 
        return {
        'data': data
        }

if __name__ == '__main__':
    app.run_server(debug=True, threaded=True)

