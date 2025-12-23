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

default_df = pd.DataFrame(columns=["day","focus","hours","activations"])

# Status Heute
daily = pd.DataFrame(daily_stats(API_KEY,-1))
if daily.empty:
    daily = default_df
fig_day = px.bar(daily, x="focus", y="hours")

#Status Woche
weekly = pd.DataFrame(weekly_stats(API_KEY,-1))
if weekly.empty:
    weekly = default_df
fig_week = px.bar(weekly, x="focus", y="hours")

app.layout = html.Div(
    children=[
    # Header
    html.Div(
        className="app-header",
        children=[
            html.Div('Time Tracker', className="app-header--title")
        ]
    ),
    html.Div(),

    # Inhalt
    html.Div(
        className="app-container",
        children=[
        html.Div(children="Today:", className="app-container--title"),

        dcc.Graph(
            id='example-graph',
            figure=fig_day
        ),
    ]),
    html.Div(className="spacer"),
    html.Div(
        className="app-container",
        children=[
        html.Div(children="Week:", className="app-container--title"),

        dcc.Graph(
            id='example-graph2',
            figure=fig_week
        ),
    ]),
])

if __name__ == '__main__':
    app.run(debug=True)
