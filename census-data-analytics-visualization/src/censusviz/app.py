from __future__ import annotations

from dash import Dash, Input, Output, dcc, html, dash_table
import pandas as pd

from .analysis import CensusAnalyzer
from .visuals import choropleth, trend_chart, income_distribution_chart, moe_chart


def build_app() -> Dash:
    analyzer = CensusAnalyzer.from_local_data()
    state_summary = analyzer.weighted_national_summary()
    metrics = analyzer.available_metrics()

    app = Dash(__name__)
    app.title = "Census Data Analytics and Visualization"

    app.layout = html.Div(
        style={"fontFamily": "Arial, sans-serif", "padding": "24px", "maxWidth": "1280px", "margin": "0 auto"},
        children=[
            html.H1("Census Data Analytics and Visualization"),
            html.P("Interactive demographic and geographic analysis built around census-style data, survey-weighted summaries, and margin-of-error aware visuals."),
            html.Div(
                style={"display": "grid", "gridTemplateColumns": "repeat(5, 1fr)", "gap": "12px"},
                children=[
                    html.Div([html.H4("Population"), html.P(f"{state_summary['population_total']:,.0f}")], style=_card_style()),
                    html.Div([html.H4("Weighted income"), html.P(f"${state_summary['weighted_median_income']:,.0f}")], style=_card_style()),
                    html.Div([html.H4("Poverty rate"), html.P(f"{state_summary['weighted_poverty_rate']:.2f}%")], style=_card_style()),
                    html.Div([html.H4("Owner occupied"), html.P(f"{state_summary['weighted_owner_occupied_rate']:.2f}%")], style=_card_style()),
                    html.Div([html.H4("Median age"), html.P(f"{state_summary['weighted_median_age']:.2f}")], style=_card_style()),
                ],
            ),
            html.Hr(),
            html.Div(
                style={"display": "flex", "gap": "12px", "alignItems": "center"},
                children=[
                    html.Label("Geography"),
                    dcc.Dropdown(id="geography", options=[{"label": "State", "value": "state"}, {"label": "County", "value": "county"}], value="state", clearable=False, style={"width": "220px"}),
                    html.Label("Metric"),
                    dcc.Dropdown(id="metric", options=[{"label": m.replace('_', ' ').title(), "value": m} for m in metrics], value="median_income", clearable=False, style={"width": "260px"}),
                ],
            ),
            dcc.Graph(id="map-graph"),
            html.Div(style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "18px"}, children=[
                dcc.Graph(id="trend-graph", figure=trend_chart(analyzer)),
                dcc.Graph(id="income-graph", figure=income_distribution_chart(analyzer)),
            ]),
            dcc.Graph(id="moe-graph"),
            html.H3("Top geographies"),
            dash_table.DataTable(id="top-table", page_size=10, style_table={"overflowX": "auto"}, style_cell={"padding": "8px", "textAlign": "left"}),
        ],
    )

    @app.callback(
        Output("map-graph", "figure"),
        Output("moe-graph", "figure"),
        Output("top-table", "data"),
        Output("top-table", "columns"),
        Input("geography", "value"),
        Input("metric", "value"),
    )
    def refresh(geography: str, metric: str):
        frame = analyzer.geography_frame(geography)
        map_fig = choropleth(geography, metric, frame)
        moe_frame = analyzer.margin_of_error_bounds(geography, metric).head(12)
        table = analyzer.top_geographies(metric, geography, n=10)
        table[metric] = table[metric].map(lambda v: f"{v:,.2f}" if isinstance(v, (int, float)) else v)
        return map_fig, moe_chart(moe_frame, metric), table.to_dict("records"), [{"name": col.replace('_', ' ').title(), "id": col} for col in table.columns]

    return app


def _card_style() -> dict[str, str]:
    return {"border": "1px solid #ddd", "borderRadius": "8px", "padding": "12px", "background": "#fafafa"}


def main() -> None:
    app = build_app()
    app.run(host="0.0.0.0", port=8050, debug=False)


if __name__ == "__main__":
    main()
