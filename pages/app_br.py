import dash
import dash_bootstrap_components as dbc
from dash import callback, dcc, html, Input, Output
import plotly.express as px
import polars as pl

dash.register_page(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    path="/br",
)

# dataframe -------------------------------------------------
df = pl.read_parquet("data/ready/michelin.parquet")

# body -------------------------------------------------
layout = dbc.Container(
    [
        html.Div(
            [
                # title -------------------------------------------------
                html.H2(
                    "Descubra seu próximo restaurante favorito",
                    className="title_br",
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
                                            placeholder='Pesquisar restaurantes por Serviços/Instalações (ex. "Estacionamento")',
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
                                            html.Span("Todos", className="button-text"),
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
                                    id="distincao-dropdown",
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
                                                        "Categoria",
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
                                        for col in sorted(df["Award_br"].unique())
                                    ],
                                    value="All",
                                    clearable=True,
                                    multi=False,
                                    placeholder="Selecione a Categoria",
                                ),
                            ],
                            width=2,
                        ),
                        # button price -------------------------------------------------
                        dbc.Col(
                            [
                                dcc.Dropdown(
                                    id="preco-dropdown",
                                    options=[
                                        {
                                            "label": html.Div(
                                                [
                                                    html.I(
                                                        className="fas fa-tag icon",
                                                    ),
                                                    html.Span("Preço"),
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
                                    placeholder="Selecione o Preço",
                                    className="custom-dropdown",
                                ),
                            ],
                            width=2,
                        ),
                        # button cuisine -------------------------------------------------
                        dbc.Col(
                            [
                                dcc.Dropdown(
                                    id="cozinha-dropdown",
                                    options=[
                                        {
                                            "label": html.Div(
                                                [
                                                    html.I(
                                                        className="fas fa-utensils icon",
                                                    ),
                                                    html.Span("Cozinha"),
                                                    html.Div(className="div-line"),
                                                ]
                                            ),
                                            "value": "All",
                                        }
                                    ]
                                    + [
                                        {"label": col, "value": col}
                                        for col in sorted(df["Cuisine_br"].unique())
                                    ],
                                    value="All",
                                    clearable=True,
                                    multi=False,
                                    placeholder="Selecione a Cozinha",
                                    className="custom-dropdown",
                                ),
                            ],
                            width=3,
                        ),
                        # button location -------------------------------------------------
                        dbc.Col(
                            [
                                dcc.Dropdown(
                                    id="localizacao-dropdown",
                                    options=[
                                        {
                                            "label": html.Div(
                                                [
                                                    html.I(
                                                        className="fas fa-earth-americas icon",
                                                    ),
                                                    html.Span("Localização"),
                                                    html.Div(className="div-line"),
                                                ]
                                            ),
                                            "value": "All",
                                        }
                                    ]
                                    + [
                                        {"label": col, "value": col}
                                        for col in sorted(df["Location_br"].unique())
                                    ],
                                    value="All",
                                    clearable=True,
                                    multi=False,
                                    placeholder="Selecione a Localização",
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
                            html.Div(id="restaurante-contador", className="counter"),
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
                                                    id="cards-contador",
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
                                            id="paginacao",
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
                                                id="mapa",
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
        Output("distincao-dropdown", "value"),
        Output("preco-dropdown", "value"),
        Output("cozinha-dropdown", "value"),
        Output("localizacao-dropdown", "value"),
        Output("paginacao", "active_page"),
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
        Output("mapa", "figure"),
        Output("restaurante-contador", "children"),
        Output("cards-contador", "children"),
        Output("paginacao", "max_value"),
        Output("preco-dropdown", "options"),
        Output("cozinha-dropdown", "options"),
        Output("localizacao-dropdown", "options"),
        Output("distincao-dropdown", "options"),
    ],
    [
        Input("distincao-dropdown", "value"),
        Input("preco-dropdown", "value"),
        Input("cozinha-dropdown", "value"),
        Input("localizacao-dropdown", "value"),
        Input("paginacao", "active_page"),
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
    filtered_df = df

    # filter search button -------------------------------------------------
    if search_input:
        filtered_df = filtered_df.with_columns(
            pl.col("FacilitiesAndServices_br").cast(pl.Utf8)
        )

        filtered_df = filtered_df.filter(
            pl.col("FacilitiesAndServices_br").str.contains(search_input, literal=True)
        )

    # filter dropdown -------------------------------------------------
    if price_dropdown and price_dropdown != "All":
        filtered_df = filtered_df.filter(filtered_df["Price_dollar"] == price_dropdown)

    if award_dropdown and award_dropdown != "All":
        filtered_df = filtered_df.filter(filtered_df["Award_br"] == award_dropdown)

    if cuisine_dropdown and cuisine_dropdown != "All":
        filtered_df = filtered_df.filter(filtered_df["Cuisine_br"] == cuisine_dropdown)

    if location_dropdown and location_dropdown != "All":
        filtered_df = filtered_df.filter(
            filtered_df["Location_br"] == location_dropdown
        )

    # update dropdown title -------------------------------------------------
    price_options = [
        {
            "label": html.Div(
                [
                    html.I(className="fas fa-tag icon"),
                    html.Span("Preço"),
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
                    html.Span("Cozinha"),
                    html.Div(className="div-line"),
                ]
            ),
            "value": "All",
        }
    ] + [
        {"label": col, "value": col}
        for col in sorted(filtered_df["Cuisine_br"].unique())
    ]

    location_options = [
        {
            "label": html.Div(
                [
                    html.I(className="fas fa-earth-americas icon"),
                    html.Span("Localização"),
                    html.Div(className="div-line"),
                ]
            ),
            "value": "All",
        }
    ] + [
        {"label": col, "value": col}
        for col in sorted(filtered_df["Location_br"].unique())
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
                        "Categoria",
                        className="text-img",
                    ),
                    html.Div(className="div-line"),
                ]
            ),
            "value": "All",
        }
    ] + [
        {"label": col, "value": col} for col in sorted(filtered_df["Award_br"].unique())
    ]

    # count restaurants -------------------------------------------------
    restaurant_count = len(filtered_df)

    # map -------------------------------------------------
    map_fig = px.scatter_map(
        data_frame=filtered_df,
        lat="Latitude",
        lon="Longitude",
        hover_name="Name",
        custom_data=["Name", "Address", "FacilitiesAndServices_br"],
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
        hovertemplate="<b>  %{customdata[0]} </b><br>"
        + "Endereço: %{customdata[1]} <br>"
        + "Serviços/Facilidades: %{customdata[2]} <br>",
    )

    # page -------------------------------------------------
    page_size = 4
    max_page = -(-len(filtered_df) // page_size)
    active_page = active_page or 1
    start_idx = (active_page - 1) * page_size
    end_idx = start_idx + page_size

    # page active dataframe -------------------------------------------------
    page_df = filtered_df.slice(start_idx, page_size)

    # count restaurants -------------------------------------------------
    first_item = start_idx + 1
    last_item = min(end_idx, restaurant_count)
    counter_text = f"{first_item:,}-{last_item:,} de {restaurant_count:,} restaurantes"

    # create the cards for the current page -------------------------------------------------
    cards = []
    for row in page_df.iter_rows(named=True):
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
                            f"{row['Award_br']} | {row['Award_info_br']}",
                            className="card-text",
                        ),
                        html.P(f"{row['Price']}", className="card-text"),
                        html.P(
                            [html.Em("Cozinha "), row["Cuisine_br"]],
                            className="card-text",
                        ),
                        html.P(f"{row['Location_br']}", className="card-text"),
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
