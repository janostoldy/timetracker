import os

from dash import Dash, html, dcc
import dash_ag_grid as dag
import pandas as pd
import plotly.express as px

# nur zum testen
from dotenv import load_dotenv
load_dotenv()

from api.main import current_focus, daily_stats, weekly_stats, monthly_stats, overall_stats

API_KEY = os.getenv("API_KEY")
app = Dash()

# Status Heute
daily = pd.DataFrame(daily_stats(API_KEY))
fig = px.bar(daily, x="focus", y="hours")

app.layout = html.Div(children=[
    html.Div(
        className="app-header",
        children=[
            html.Div('Time Tracker', className="app-header--title")
        ]
    ),

    html.H2(children='''
        Today:
    '''),

    dcc.Graph(
        id='example-graph',
        figure=fig
    )
])

if __name__ == '__main__':
    app.run(debug=True)
