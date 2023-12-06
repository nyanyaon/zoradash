from dash import Dash, html, dcc, callback, Output, Input, dash_table
from dash.long_callback import DiskcacheLongCallbackManager
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

import diskcache
cache = diskcache.Cache("./cache")
long_callback_manager = DiskcacheLongCallbackManager(cache)

def simplify_number(n):
    if(n>1000):
        return str(int(round(n/1000))) + 'K'
    
    return int(n)

df = pd.read_csv('./assets/data.csv')

app = Dash(__name__)

app.title = 'Website Marketing Dashboard'

header = [
    html.H1(children='Website Marketing Dashboard'),
    html.Div([
        html.Label('Channel Grouping', htmlFor='dropdown-selection'),
        dcc.Dropdown(np.append([a for a in df['Channel Grouping'].unique()], ['All']), 'All', id='dropdown-selection'),
    ], className='group')
]

sidebar_item = [
            html.Ul([
                html.Li('Cockpit'),
                html.Li('Sessions'),
                html.Li('Page Views'),
                html.Li('Page Load Time'),
            ])
        ]

app.layout = html.Div([
    html.Div(header, className='header'),
    html.Div([
        html.Div(sidebar_item,className='sidebar'),
        html.Div([
            html.Div([
                html.Div([
                    html.H3(id='total-session'),
                    html.P('Total Sessions')
                ], className='card'),
                html.Div([
                    html.H3(id='total-exits'),
                    html.P('Total Exits')
                ], className='card'),
                html.Div([
                    html.H3(id='total-bounces'),
                    html.P('Total Bounces')
                ], className='card'),
                html.Div([
                    html.H3(id='avg-top'),
                    html.P('Average of Time on Page')
                ], className='card'),
            ], className='row'),
            html.Div([
                html.Div([
                    html.Div([
                        html.H3(id='lty-session'),
                        html.P('Latest Year Sessions')
                    ], className='block dflex align-center fcol w20'),
                    dcc.Graph(id='bar-sumsession-month')
                ], className='latestyearsession dflex'),
                html.Div([
                    html.H3(id='unq_pageviews'),
                    html.P('Unique Pageviews')
                ], className='block dflex align-center fcol w20'),
                html.Div([
                    html.H3(id='avr_pageloadtime'),
                    html.P('Average Page Load Time')
                ], className='block dflex align-center fcol w20'),
            ], className='row'),
            html.Div([
                html.Div([
                    html.Div([
                        dash_table.DataTable(id='tbl_per_device',
                            style_cell={
                                'textAlign': 'center',
                                'border': 'none',
                            },
                            style_cell_conditional=[
                                {
                                    'if': {'column_id': 'Device Category'},
                                    'textAlign': 'left',
                                    'border': 'none',
                                    'borderRight': '1px solid grey'
                                }
                            ],
                            style_header={
                                'textAlign': 'center',
                                'fontWeight': 'bold',
                                'color': '#094780',
                                'border': 'none',
                                'borderBottom': '1px solid grey',
                                'background': 'white'
                            },
                        ),
                    ], className='tbl-per-device'),
                    html.Div([
                        dcc.Graph(id='graph-content')
                    ])
                ], className='col w50'),
                html.Div([
                    dcc.Graph(id='top_pt_by_unqpv')
                ], className='col w25'),
                html.Div([
                    dcc.Graph(id='top_cntry_by_unqpv')
                ], className='col w25'),
            ], className='row'),
        ], className='content')
    ], className='main')
])

@app.long_callback(
    output=Output("top_cntry_by_unqpv", "figure"),
    inputs=Input("dropdown-selection", "value"),
    manager=long_callback_manager,
)
def update_bar_top_pt_by_unqpv(value):
    if value=='All':
        df_filter = df
    else:    
        df_filter = df[df['Channel Grouping']==value]
         
    df_filter = df_filter[['Country','Unique Pageviews']].groupby(['Country']).sum(numeric_only=True).sort_values(by='Unique Pageviews', ascending=False).reset_index()

    return px.bar(
        df_filter.head(5), 
        x='Unique Pageviews', 
        y='Country', 
        title='Top 5 Country by Uniqe Pageviews ', 
        text_auto='.2s'
    ).update_traces(
        textfont_size=12, 
        textangle=0, 
        textposition="inside", 
        cliponaxis=False
    ).update_xaxes(
        showticklabels=False,
    ).update_yaxes(
        showticklabels=True,
        title='',
    ).update_layout(
        plot_bgcolor='white',
        font=dict(size=10),
        xaxis_title=None,
        legend=dict(
            font=dict(size=9),
            orientation='h',
            yanchor='top',
            y=1,
            xanchor='left',
            x=0
        ),
        margin=dict(l=10, r=10),
    )

@app.long_callback(
    output=Output("top_pt_by_unqpv", "figure"),
    inputs=Input("dropdown-selection", "value"),
    manager=long_callback_manager,
)
def update_bar_top_pt_by_unqpv(value):
    if value=='All':
        df_filter = df
    else:    
        df_filter = df[df['Channel Grouping']==value]
         
    df_filter = df_filter.groupby(['Page Title','Device Category'])[['Unique Pageviews']].sum(numeric_only=True).sort_values(by='Unique Pageviews', ascending=False).reset_index()

    df_sort = df_filter.head(5)['Page Title']

    return px.bar(
        df_filter[df_filter['Page Title'].isin(df_sort)], 
        x='Page Title', 
        y='Unique Pageviews', 
        color='Device Category', 
        title='Top 5 Page Title by Uniqe Pageviews ', 
        text_auto='.2s'
    ).update_traces(
        textfont_size=12, 
        textangle=0, 
        textposition="inside", 
        cliponaxis=False
    ).update_xaxes(
        showticklabels=True,
        tickangle=90
    ).update_yaxes(
        visible=False, 
        showticklabels=False
    ).update_layout(
        plot_bgcolor='white',
        font=dict(size=10),
        xaxis_title=None,
        legend=dict(
            font=dict(size=9),
            orientation='h',
            yanchor='top',
            y=1,
            xanchor='left',
            x=0
        ),
        margin=dict(l=0, r=0, b=0),
    )

@callback(
        Output('tbl_per_device', 'data'),
        Output('tbl_per_device', 'columns'),
        Input('dropdown-selection', 'value')
)
def update_tbl_per_device(value):
    if value == 'All':
        df_filter = df
    else:  
        df_filter = df[df['Channel Grouping']==value]
    
    df_devices = df_filter.groupby(['Device Category'])[['Sessions', 'Bounces']].agg('sum').reset_index()

    df_devices.loc[len(df_devices.index)] = ['Total', df_devices['Sessions'].sum(), df_devices['Bounces'].sum()]

    return df_devices.to_dict('records'), [{'id': i, 'name': i} for i in df_devices.columns]

@callback(
        Output('avr_pageloadtime', 'children'),
        Input('dropdown-selection', 'value')
)
def update_avr_pageloadtime(value):
    if value == 'All':
        df_filter = df
    else:  
        df_filter = df[df['Channel Grouping']==value]

    df_filter['Date'] = pd.to_datetime(df_filter['Date'], format='%m/%d/%Y')
    df_filter = df_filter[df_filter['Date'].dt.year >= 2019]
       
    return simplify_number(df_filter['Page Load Time'].sum()/df_filter['Page Load Time'].count())

@callback(
        Output('unq_pageviews', 'children'),
        Input('dropdown-selection', 'value')
)
def update_unq_pageviews(value):
    if value == 'All':
        df_filter = df
    else:  
        df_filter = df[df['Channel Grouping']==value]

    df_filter['Date'] = pd.to_datetime(df_filter['Date'], format='%m/%d/%Y')
    df_filter = df_filter[df_filter['Date'].dt.year >= 2019]
       
    return simplify_number(df_filter['Unique Pageviews'].sum())

@callback(
        Output('lty-session', 'children'),
        Input('dropdown-selection', 'value')
)
def update_lty_session(value):
    if value == 'All':
        df_filter = df
    else:  
        df_filter = df[df['Channel Grouping']==value]

    dfB = pd.DataFrame({'date': pd.to_datetime(df_filter['Date'], format='%m/%d/%Y'), 'sessions': df_filter['Sessions']})
    df_fyear = dfB.loc[dfB['date'].dt.year >= 2019]
       
    return simplify_number(df_fyear['sessions'].sum())

@callback(
        Output('avg-top', 'children'),
        Input('dropdown-selection', 'value')
)
def update_avg_top(value):
    if value == 'All':
        df_filter = df
    else:  
        df_filter = df[df['Channel Grouping']==value]
       
    return simplify_number(df_filter['Time on Page'].sum()/df_filter['Time on Page'].count())

@callback(
        Output('total-bounces', 'children'),
        Input('dropdown-selection', 'value')
)
def update_total_bounces(value):
    if value == 'All':
        df_filter = df
    else:  
        df_filter = df[df['Channel Grouping']==value]
       
    return simplify_number(df_filter.Bounces.sum())

@callback(
        Output('total-exits', 'children'),
        Input('dropdown-selection', 'value')
)
def update_total_exits(value):
    if value == 'All':
        df_filter = df
    else:  
        df_filter = df[df['Channel Grouping']==value]
       
    return simplify_number(df_filter.Exits.sum())

@callback(
        Output('total-session', 'children'),
        Input('dropdown-selection', 'value')
)
def update_total_sessions(value):
    if value == 'All':
        df_filter = df
    else:  
        df_filter = df[df['Channel Grouping']==value]
       
    return simplify_number(df_filter.Sessions.sum())

@callback(
    Output('bar-sumsession-month', 'figure'),
    Input('dropdown-selection', 'value')
)
def update_bar_sumsession_month(value):
    if value=='All':
        df_filter = df
    else:    
        df_filter = df[df['Channel Grouping']==value]
         
    df_filter['Date'] = pd.to_datetime(df_filter['Date'], format='%m/%d/%Y')
    df_filter = df_filter[df_filter['Date'].dt.year >= 2019]
    df_filter = df_filter.sort_values(by='Date')

    df_filter['month_name'] = df_filter['Date'].dt.month_name()
    df_filter['month'] = df_filter['Date'].dt.month

    df_filter = df_filter.groupby(['month', 'month_name'])['Sessions'].aggregate('sum').reset_index()

    return px.bar(df_filter, x='month_name', y='Sessions', title='Sum of Sessions by Month', text_auto='.2s').update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False).update_xaxes(tickangle=315,showticklabels=True).update_yaxes(visible=False, showticklabels=False).update_layout(xaxis_title=None, margin=dict(l=0, r=10, b=0))
    

@callback(
    Output('graph-content', 'figure'),
    Input('dropdown-selection', 'value')
)
def update_graph(value):
    if value=='All':
        dfA = df
    else:    
        dfA = df[df['Channel Grouping']==value]
    
    dfA['Date'] = pd.to_datetime(dfA['Date'], format='%m/%d/%Y')
    dfA = dfA[['Date', 'Bounces', 'Sessions']].groupby(pd.Grouper(key='Date', freq='M')).sum().reset_index()

    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dfA['Date'],
        y=dfA['Sessions'],
        mode='lines',
        name='Sum of Sessions'
    ))
    fig.add_trace(go.Scatter(
        x=dfA['Date'],
        y=dfA['Bounces'],
        mode='lines',
        name='Sum of Bounces'
    ))
    fig.update_yaxes(tickformat=".2s")
    fig.update_layout(
        plot_bgcolor='white',
        legend=dict(
            orientation='h',
            yanchor='top',
            y=1,
            xanchor='left',
            x=0
        ),
        margin=dict(l=15, r=15, b=15, t=15),
    )

    return fig

if __name__ == '__main__':
    app.run(debug=True)
