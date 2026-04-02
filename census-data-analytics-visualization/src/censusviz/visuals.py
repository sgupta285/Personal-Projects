from __future__ import annotations

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from .analysis import CensusAnalyzer
from .data_loader import load_geojson


METRIC_LABELS = {
    "population": "Population",
    "median_income": "Median income",
    "poverty_rate": "Poverty rate",
    "owner_occupied_rate": "Owner-occupied housing rate",
    "median_home_value": "Median home value",
    "median_age": "Median age",
}


def choropleth(geography: str, metric: str, frame: pd.DataFrame):
    title = f"{METRIC_LABELS.get(metric, metric)} by {geography.title()}"
    if geography == "state":
        return px.choropleth(
            frame,
            geojson=load_geojson("states.geojson"),
            featureidkey="properties.fips",
            locations="fips",
            color=metric,
            scope="usa",
            hover_name="name",
            title=title,
            color_continuous_scale="Blues",
        )
    return px.choropleth(
        frame,
        geojson=load_geojson("counties.geojson"),
        featureidkey="properties.fips",
        locations="fips",
        color=metric,
        scope="usa",
        hover_name="name",
        title=title,
        color_continuous_scale="Viridis",
    )


def trend_chart(analyzer: CensusAnalyzer):
    trend_df = analyzer.trend_frame()
    return px.line(trend_df, x="year", y="median_income", color="region", markers=True, title="Median income trends")


def income_distribution_chart(analyzer: CensusAnalyzer):
    df = analyzer.income_distribution()
    return px.bar(df, x="income_band", y="share", title="Income distribution", labels={"share": "Share of households (%)"})


def moe_chart(moe_df: pd.DataFrame, metric: str):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=moe_df["name"],
        y=moe_df[metric],
        mode="markers",
        name="estimate",
        error_y=dict(type="data", symmetric=False, array=moe_df["upper"] - moe_df[metric], arrayminus=moe_df[metric] - moe_df["lower"]),
    ))
    fig.update_layout(title=f"Margin of error for {metric}", xaxis_title="Geography", yaxis_title=metric)
    return fig
