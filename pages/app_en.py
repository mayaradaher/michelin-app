import dash
import dash_bootstrap_components as dbc
from dash import callback, dcc, html, Input, Output
import pandas as pd
import plotly.express as px

from sentence_transformers import SentenceTransformer, util
import torch
from Levenshtein import distance


dash.register_page(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    path="/en",
)

# dataframe -------------------------------------------------
df = pd.read_parquet("data/ready/michelin_embedding.parquet")

df["embedding"] = df["embedding"].apply(lambda x: torch.tensor(x, dtype=torch.float16))

model = SentenceTransformer("multi-qa-mpnet-base-dot-v1")

# body -------------------------------------------------
layout = dbc.Container(
    [
        html.Div(
            [
                # title -------------------------------------------------
                html.H2(
                    "Discover your next favorite restaurant",
                    className="title_en",
                ),
                # button search -------------------------------------------------
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Div(
                                    className="icon-container",
                                    children=[
                                        html.I(
                                            className="fas fa-magnifying-glass icon-search"
                                        ),
                                        dcc.Input(
                                            id="search-input",
                                            placeholder='Search restaurants by Address (e.g. "Villarroel 163")',
                                            className="dbc-button",
                                            debounce=True,
                                            style={
                                                "text-indent": "30px",
                                                "height": "58px",
                                                "width": "100%",
                                                "box-shadow": "2px 2px 5px rgba(0, 0, 0, 0.2), -2px -2px 5px rgba(0, 0, 0, 0.1)",
                                            },
                                        ),
                                    ],
                                ),
                            ],
                            className="button-search",
                        ),
                    ]
                ),
                dbc.Row(
                    [
                        # button all -------------------------------------------------
                        dbc.Col(
                            [
                                dbc.Button(
                                    html.Div(
                                        [
                                            html.I(
                                                className="fas fa-check-double icon",
                                            ),
                                            html.Span("All", className="button-text"),
                                        ],
                                    ),
                                    id="all-button",
                                    className="dbc-button",
                                ),
                            ],
                            width=2,
                        ),
                        # button award -------------------------------------------------
                        dbc.Col(
                            [
                                dcc.Dropdown(
                                    id="award-dropdown",
                                    options=[
                                        {
                                            "label": html.Div(
                                                [
                                                    html.Img(
                                                        src="assets/logos/award.png",
                                                        style={
                                                            "height": "20px",
                                                            "margin-right": "10px",
                                                        },
                                                    ),
                                                    html.Span(
                                                        "Award",
                                                        className="text-img",
                                                    ),
                                                    html.Div(className="div-line"),
                                                ]
                                            ),
                                            "value": "All",
                                        }
                                    ]
                                    + [
                                        {"label": col, "value": col}
                                        for col in sorted(df["Award"].unique())
                                    ],
                                    value="All",
                                    clearable=True,
                                    multi=False,
                                    placeholder="Select an Award",
                                ),
                            ],
                            width=2,
                        ),
                        # button price -------------------------------------------------
                        dbc.Col(
                            [
                                dcc.Dropdown(
                                    id="price-dropdown",
                                    options=[
                                        {
                                            "label": html.Div(
                                                [
                                                    html.I(
                                                        className="fas fa-tag icon",
                                                    ),
                                                    html.Span("Price"),
                                                    html.Div(className="div-line"),
                                                ]
                                            ),
                                            "value": "All",
                                        }
                                    ]
                                    + [
                                        {"label": col, "value": col}
                                        for col in sorted(df["Price_dollar"].unique())
                                    ],
                                    value="All",
                                    clearable=True,
                                    multi=False,
                                    placeholder="Select a Price",
                                    className="custom-dropdown",
                                ),
                            ],
                            width=2,
                        ),
                        # button cuisine -------------------------------------------------
                        dbc.Col(
                            [
                                dcc.Dropdown(
                                    id="cuisine-dropdown",
                                    options=[
                                        {
                                            "label": html.Div(
                                                [
                                                    html.I(
                                                        className="fas fa-utensils icon",
                                                    ),
                                                    html.Span("Cuisine"),
                                                    html.Div(className="div-line"),
                                                ]
                                            ),
                                            "value": "All",
                                        }
                                    ]
                                    + [
                                        {"label": col, "value": col}
                                        for col in sorted(df["Cuisine"].unique())
                                    ],
                                    value="All",
                                    clearable=True,
                                    multi=False,
                                    placeholder="Select a Cuisine",
                                    className="custom-dropdown",
                                ),
                            ],
                            width=3,
                        ),
                        # button location -------------------------------------------------
                        dbc.Col(
                            [
                                dcc.Dropdown(
                                    id="location-dropdown",
                                    options=[
                                        {
                                            "label": html.Div(
                                                [
                                                    html.I(
                                                        className="fas fa-earth-americas icon",
                                                    ),
                                                    html.Span("Location"),
                                                    html.Div(className="div-line"),
                                                ]
                                            ),
                                            "value": "All",
                                        }
                                    ]
                                    + [
                                        {"label": col, "value": col}
                                        for col in sorted(df["Location"].unique())
                                    ],
                                    value="All",
                                    clearable=True,
                                    multi=False,
                                    placeholder="Select a Location",
                                    className="custom-dropdown",
                                ),
                            ],
                            width=3,
                        ),
                    ]
                ),
                # counter restaurant -------------------------------------------------
                dbc.Row(
                    [
                        dbc.Col(
                            html.Div(id="restaurant-counter", className="counter"),
                        ),
                    ],
                ),
                dbc.Row(
                    [
                        # cards -------------------------------------------------
                        dbc.Col(
                            [
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            dcc.Loading(
                                                html.Div(
                                                    id="cards-content",
                                                ),
                                                type="circle",
                                                color="#bd2333",
                                            ),
                                        ),
                                    ],
                                ),
                                # pagination -------------------------------------------------
                                dbc.Row(
                                    dbc.Col(
                                        dbc.Pagination(
                                            id="pagination",
                                            max_value=5,
                                            previous_next=True,
                                            size="sm",
                                            fully_expanded=False,
                                        ),
                                    ),
                                ),
                            ],
                        ),
                        # radio buttons map -------------------------------------------------
                        dbc.Col(
                            [
                                dbc.Row(
                                    dbc.Col(
                                        dcc.RadioItems(
                                            id="map-radio",
                                            options=[
                                                {
                                                    "label": "CARTO",
                                                    "value": "light",
                                                },
                                                {
                                                    "label": "Open Street Map",
                                                    "value": "open-street-map",
                                                },
                                                {
                                                    "label": "ESRI",
                                                    "value": "satellite-streets",
                                                },
                                            ],
                                            value="light",
                                            labelStyle={
                                                "display": "inline-block",
                                                "margin-right": "20px",
                                            },
                                        ),
                                    ),
                                    className="radio-buttons",
                                ),
                                # map -------------------------------------------------
                                dbc.Row(
                                    dbc.Col(
                                        dcc.Loading(
                                            dcc.Graph(
                                                id="map",
                                                config={"displayModeBar": False},
                                                className="map",
                                                style={"height": "567px"},
                                            ),
                                            type="circle",
                                            color="#bd2333",
                                        ),
                                        # width=12,
                                    )
                                ),
                            ],
                            # width=6,
                        ),
                    ],
                ),
            ],
            className="page-content",
        )
    ],
    fluid=True,
)


# callback buttom all -------------------------------------------------
@callback(
    [
        Output("award-dropdown", "value"),
        Output("price-dropdown", "value"),
        Output("cuisine-dropdown", "value"),
        Output("location-dropdown", "value"),
        Output("pagination", "active_page"),
    ],
    Input("all-button", "n_clicks"),
)
def all_filters(n_clicks):
    # If the "All" button was not clicked, set "All" as the default value
    if n_clicks is None:
        return "All", "All", "All", "All", 1
    else:
        # If "All" button was clicked, return "All" and active page as 1
        return "All", "All", "All", "All", 1


# callback map and cards -------------------------------------------------
@callback(
    [
        Output("map", "figure"),
        Output("restaurant-counter", "children"),
        Output("cards-content", "children"),
        Output("pagination", "max_value"),
        Output("price-dropdown", "options"),
        Output("cuisine-dropdown", "options"),
        Output("location-dropdown", "options"),
        Output("award-dropdown", "options"),
    ],
    [
        Input("award-dropdown", "value"),
        Input("price-dropdown", "value"),
        Input("cuisine-dropdown", "value"),
        Input("location-dropdown", "value"),
        Input("pagination", "active_page"),
        Input("map-radio", "value"),
        Input("search-input", "value"),
    ],
)
def update_map_cards(
    award_dropdown,
    price_dropdown,
    cuisine_dropdown,
    location_dropdown,
    active_page,
    map_radio,
    search_input,
):
    filtered_df = df.copy()

    # filter search button -------------------------------------------------
    if search_input:
        search_embedding = model.encode(
            search_input, device="cpu", convert_to_tensor=True
        ).to(torch.float16)

        # similarity and Levenshtein distance
        df["similarity"] = df["embedding"].apply(
            lambda x: util.pytorch_cos_sim(search_embedding, x).item()
        )
        df["levenshtein"] = df["Address"].apply(lambda x: distance(search_input, x))

        threshold = 0.6
        filtered_df = df[
            (df["similarity"] >= threshold) | (df["levenshtein"] <= 2)
        ].sort_values(by=["similarity", "levenshtein"], ascending=[False, True])

    # filter dropdown -------------------------------------------------
    if price_dropdown and price_dropdown != "All":
        filtered_df = filtered_df[filtered_df["Price_dollar"] == price_dropdown]

    if award_dropdown and award_dropdown != "All":
        filtered_df = filtered_df[filtered_df["Award"] == award_dropdown]

    if cuisine_dropdown and cuisine_dropdown != "All":
        filtered_df = filtered_df[filtered_df["Cuisine"] == cuisine_dropdown]

    if location_dropdown and location_dropdown != "All":
        filtered_df = filtered_df[filtered_df["Location"] == location_dropdown]

    # update dropdown title -------------------------------------------------
    price_options = [
        {
            "label": html.Div(
                [
                    html.I(className="fas fa-tag icon"),
                    html.Span("Price"),
                    html.Div(className="div-line"),
                ]
            ),
            "value": "All",
        }
    ] + [
        {"label": col, "value": col}
        for col in sorted(filtered_df["Price_dollar"].unique())
    ]

    cuisine_options = [
        {
            "label": html.Div(
                [
                    html.I(className="fas fa-utensils icon"),
                    html.Span("Cuisine"),
                    html.Div(className="div-line"),
                ]
            ),
            "value": "All",
        }
    ] + [
        {"label": col, "value": col} for col in sorted(filtered_df["Cuisine"].unique())
    ]

    location_options = [
        {
            "label": html.Div(
                [
                    html.I(className="fas fa-earth-americas icon"),
                    html.Span("Location"),
                    html.Div(className="div-line"),
                ]
            ),
            "value": "All",
        }
    ] + [
        {"label": col, "value": col} for col in sorted(filtered_df["Location"].unique())
    ]

    award_options = [
        {
            "label": html.Div(
                [
                    html.Img(
                        src="assets/logos/award.png",
                        style={"height": "20px", "margin-right": "10px"},
                    ),
                    html.Span(
                        "Award",
                        className="text-img",
                    ),
                    html.Div(className="div-line"),
                ]
            ),
            "value": "All",
        }
    ] + [{"label": col, "value": col} for col in sorted(filtered_df["Award"].unique())]

    # count restaurants -------------------------------------------------
    restaurant_count = len(filtered_df)

    # map -------------------------------------------------
    map_fig = px.scatter_map(
        data_frame=filtered_df,
        lat="Latitude",
        lon="Longitude",
        hover_name="Name",
        custom_data=["Name", "Address"],
        zoom=1,
        map_style=map_radio,
    )

    map_fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        hoverlabel=dict(
            bgcolor="#FAFAF8",
            bordercolor="gray",
            font_size=13,
            font_family="Roboto",
        ),
    )

    map_fig.update_traces(
        marker=dict(
            color="#bd2333",
            opacity=0.8,
            size=5,
        ),
        # cluster=dict(
        #     enabled=True,
        #     color="#bd2333",
        #     opacity=0.7,
        #     size=20,
        # ),
        hovertemplate="<b> %{customdata[0]} </b><br>" + "%{customdata[1]} <br>",
    )

    # page -------------------------------------------------
    page_size = 4
    max_page = -(-len(filtered_df) // page_size)
    active_page = active_page or 1
    start_idx = (active_page - 1) * page_size
    end_idx = start_idx + page_size

    # page active dataframe -------------------------------------------------
    page_df = filtered_df.iloc[start_idx:end_idx]

    # count restaurants -------------------------------------------------
    first_item = start_idx + 1
    last_item = min(end_idx, restaurant_count)
    counter_text = f"{first_item:,}-{last_item:,} of {restaurant_count:,} restaurants"

    # create the cards for the current page -------------------------------------------------
    cards = []
    for _, row in page_df.iterrows():
        card = dbc.Card(
            [
                dbc.CardBody(
                    [
                        html.Img(
                            src=row["ImageURL"],
                            className="card-img",
                        ),
                        html.H5(row["Name"], className="card-title"),
                        html.P(
                            f"{row['Award']} | {row['Award_info_en']}",
                            className="card-text",
                        ),
                        html.P(f"{row['Price']}", className="card-text"),
                        html.P(
                            [row["Cuisine"], html.Em(" Cuisine")], className="card-text"
                        ),
                        html.P(f"{row['Location']}", className="card-text"),
                    ]
                )
            ],
        )
        cards.append(card)

    # arrange cards into rows with two columns -------------------------------------------------
    card_rows = []
    for i in range(0, len(cards), 2):
        row = dbc.Row(
            [
                dbc.Col(cards[i]),
                (dbc.Col(cards[i + 1]) if i + 1 < len(cards) else dbc.Col()),
            ],
        )
        card_rows.append(row)

    # return -------------------------------------------------
    return (
        map_fig,
        counter_text,
        card_rows,
        max_page,
        price_options,
        cuisine_options,
        location_options,
        award_options,
    )
