import dash
from dash import dcc, html, Input, Output, State, callback
import plotly.graph_objects as go
import plotly.express as px
from dash.exceptions import PreventUpdate
import time
import ml.dataflow as dataflow
import ml.transform as transform    
import ml.pipeline as pipeline


app = dash.Dash(__name__, 
                meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}])

server = app.server

# TODO
#   rewrite in html/css file
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                background-color: #1E1E1E;
                color: #E0E0E0;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 0;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 2rem;
            }
            .header {
                text-align: center;
                margin-bottom: 2rem;
                padding-bottom: 1rem;
                border-bottom: 1px solid #444;
            }
            .card {
                background-color: #2D2D2D;
                border-radius: 8px;
                padding: 1.5rem;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
                margin-bottom: 1.5rem;
            }
            .button {
                background-color: #FD3777;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 1rem;
                transition: background-color 0.3s;
            }
            .button:hover {
                background-color: #FB5B92;
            }
            .input {
                background-color: #333;
                border: 1px solid #555;
                color: white;
                padding: 10px;
                border-radius: 4px;
                width: 100%;
                font-size: 1rem;
                margin-bottom: 1rem;
            }
            .graph-container {
                height: 600px;
                margin-top: 2rem;
            }
            .loading {
                text-align: center;
                margin-top: 2rem;
                font-style: italic;
                color: #888;
            }
            .footer {
                text-align: center;
                margin-top: 3rem;
                color: #888;
                font-size: 0.9rem;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# TODO
#   split other functions/classes
app.layout = html.Div(className="container", children=[
    html.Div(className="header", children=[
        html.H1("Trend XRP/USD Dashboard", style={"color": "#FD3777"}),
    ]),
    
    html.Div(className="card", children=[
        html.P("Enter ConiGeko API key: "),
        dcc.Input(
            id="api-key-input",
            type="password",
            placeholder="",
            className="input"
        ),
        # html.Small(
        #     "* https://docs.coingecko.com/v3.0.1/reference/setting-up-your-api-key",
        #     className="card-text text-muted",
        #     style={"display": "block", "text-align": "left", 'marginBottom': 15, }
        #     ),
        html.Button(
            "Generate Chart", 
            id="submit-button", 
            className="button"
        ),

        html.Div(id="auth-message", style={"margin-top": "1rem", "color": "#FF5252"})
    ]),
    
    html.Div(id="loading-container", className="loading", children=[
        dcc.Loading(
            id="loading",
            type="circle",
            children=html.Div(id="loading-output")
        )
    ]),
    
    html.Div(id="dashboard-container", style={"display": "none"}, children=[
        html.Div(className="card", children=[
            dcc.Graph(id="merged-line-chart", className="graph-container"),
            html.Div(id="accuracy-container", style={"marginTop": "1rem", "color": "#E0E0E0"})  
        ])
    ]),
    
    html.Div(className="footer", children=[
        html.P("Dashboard created @pypylinx64")
    ])
])

def fetch_data(api_key):
    if not api_key or len(api_key) < 8:
        return None, "invalid API key"
    
    time.sleep(1.5)
    
    try:
        df, accuracy, adfuler = pipeline.prediction_week_crypto(
            api_key,
            ndays=3,
            size_coef=0.2,
            )
        return df, accuracy, "success"

    except Exception as e:
        return None, None, f"Error fetching data: {str(e)}"

@callback(
    [Output("dashboard-container", "style"),
     Output("auth-message", "children"),
     Output("accuracy-container", "children"),
     Output("loading-output", "children"),
     Output("merged-line-chart", "figure")],
    [Input("submit-button", "n_clicks")],
    [State("api-key-input", "value")],
    prevent_initial_call=True
)

def update_dashboard(n_clicks, api_key):
    if not n_clicks:
        raise PreventUpdate
    
    display_style = {"display": "none"}
    auth_message = ""
    loading_output = ""
    fig = go.Figure()
    
    data, accuracy, message = fetch_data(api_key)
    
    if message != "success":
        auth_message = message
        return display_style, auth_message, "", loading_output, fig
    
    display_style = {"display": "block"}
    
    primary_data = data[dataflow.COL_OUT_PRICE]
    secondary_data = data[transform.COL_OUT_PREDICT_DENORMAL]
    
    fig = go.Figure()
    
    fig.add_trace(
        go.Scatter(
            x=primary_data.index.values,
            y=primary_data.values,
            mode='lines',
            name='real_price',
            line=dict(
                color='#FD3777',  
                width=3
            ),
        )
    )
        
    fig.add_trace(
        go.Scatter(
            x=secondary_data.index.values,
            y=secondary_data.values,
            mode='lines',
            name='trend_prediction',
            line=dict(
                color='#ffdb00',  
                width=3
            )
        )
    )

    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor='#2D2D2D',
        paper_bgcolor='#2D2D2D',
        font=dict(color='#E0E0E0'),
        title=dict(
            text='Trend predictions with LR',
            font=dict(color='#E0E0E0', size=24),
            x=0.5
        ),
        margin=dict(l=40, r=40, t=80, b=40),
        xaxis=dict(
            title="datetime",
            titlefont=dict(color='#E0E0E0'),
            tickfont=dict(color='#E0E0E0'),
            gridcolor='#444'
        ),
        yaxis=dict(
            title="usd",
            titlefont=dict(color='#E0E0E0'),
            tickfont=dict(color='#E0E0E0'),
            gridcolor='#444'
        ),
        legend=dict(
            bgcolor='rgba(45, 45, 45, 0.8)',
            bordercolor='#444',
            borderwidth=1,
            font=dict(color='#E0E0E0')
        ),
        hovermode='closest'
    )
    
    fig.update_traces(
        hovertemplate="<b>%{fullData.name}</b><br>time: %{x}<br>value: %{y:.2f}<extra></extra>"
    )
    
    accuracy_text = f"RMSE: {accuracy}" 
    return display_style, auth_message, accuracy_text, loading_output, fig


if __name__ == '__main__':
    app.run_server(debug=True)
