import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly.express as px

from data_processing import match_title, player_df, stat_df, touch_df

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


def get_pos_class_table(pos_class):
    ppc = pos_class.lower()[:-1]
    out_div_children = []
    for side in ["home", "away"]:
        _df = player_df.loc[
            lambda df: (df["position_class"] == ppc) & (df["side"] == side),
            ["name", "age", "height", "weight"],
        ]
        out_div_children.append(
            html.Div(
                [
                    html.P(side),
                    dash_table.DataTable(
                        id=f"{ppc}-{side}-table",
                        columns=[{"name": i, "id": i} for i in _df.columns],
                        data=_df.to_dict("records"),
                    ),
                ],
                className="six columns",
                style={"padding": 2},
            )
        )
    return [html.H5(pos_class), html.Div(out_div_children, className="row")]


app.layout = html.Div(
    children=[
        html.H1(children=f"Dash app - {match_title}"),
        dcc.Dropdown(
            id="event-dd",
            options=[{"label": e, "value": e} for e in ["all", *touch_df["type"].unique()]],
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        dcc.Graph(
                            id="event-graph",
                            figure=px.scatter(
                                touch_df,
                                x="x",
                                y="y",
                                color="team",
                                hover_data=["type"],
                            ),
                        )
                    ],
                    className="six columns",
                ),
                html.Div(
                    children=[
                        dcc.Graph(
                            id="stat-graph",
                            figure=px.bar(
                                stat_df.pipe(
                                    lambda df: df.groupby("stat")["value"]
                                    .sum()
                                    .rename("sum")
                                    .reset_index()
                                    .merge(df)
                                ).assign(rel=lambda df: df["value"] / df["sum"]),
                                x="stat",
                                y="rel",
                                hover_data=["value"],
                                color="team",
                                barmode="group",
                            ),
                        )
                    ],
                    className="six columns",
                ),
            ],
            className="row",
        ),
        html.Div(
            children=[
                html.Div(get_pos_class_table(pos_class), className="four columns")
                for pos_class in ["Defenders", "Midfielders", "Forwards"]
            ],
            className="row",
        ),
    ]
)


@app.callback(
    dash.dependencies.Output("event-graph", "figure"),
    [dash.dependencies.Input("event-dd", "value")],
)
def update_output(value):

    if (value is None) or (value == "all"):
        filt_df = touch_df
    else:
        filt_df = touch_df.loc[lambda df: df["type"] == value]

    return px.scatter(filt_df, x="x", y="y", color="team", hover_data=["type"])


if __name__ == "__main__":
    app.run_server(debug=True)
