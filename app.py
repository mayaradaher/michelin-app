import dash_bootstrap_components as dbc
import dash
from dash import Dash, dcc, html, Input, Output, State

app = Dash(
    __name__,
    use_pages=True,
    title="Michelin Guide",
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
)

server = app.server

# navbar -------------------------------------------------
navbar = dbc.Navbar(
    dbc.Container(
        [
            html.A(
                # logo -------------------------------------------------
                dbc.Row(
                    [
                        dbc.Col(
                            html.Img(
                                src="assets/logos/logo.svg",
                                height="35px",
                            ),
                        ),
                        # title -------------------------------------------------
                        dbc.Col(
                            dbc.NavbarBrand(
                                "Michelin World Guide",
                                className="navbar-title",
                            )
                        ),
                    ],
                ),
                href="#",
                style={"textDecoration": "none"},
            ),
            # icons + language button -------------------------------------------------
            dbc.NavbarToggler(id="navbar-toggler"),
            dbc.Collapse(
                dbc.Nav(
                    [
                        dbc.NavItem(
                            dbc.NavLink(
                                html.I(className="fab fa-github navbar-icon"),
                                href="https://github.com/mayaradaher/challenge-Michelin",
                                target="_blank",
                            )
                        ),
                        dbc.NavItem(
                            dbc.NavLink(
                                html.I(className="fab fa-linkedin navbar-icon"),
                                href="https://linkedin.com/in/mayaradaher",
                                target="_blank",
                            )
                        ),
                        dbc.DropdownMenu(
                            [
                                dbc.DropdownMenuItem(
                                    "English", href="/en", id="LinkOne"
                                ),
                                dbc.DropdownMenuItem("Português", href="/br"),
                            ],
                            nav=True,
                            in_navbar=True,
                            label="Select language",
                            className="nav-item",
                        ),
                    ],
                    className="ms-auto",
                    navbar=True,
                ),
                id="navbar-collapse",
                is_open=False,
                navbar=True,
            ),
        ],
        fluid=True,
        className="navbar",
    ),
    # navbar style -------------------------------------------------
    color="#bd2333",
    dark=True,
    style={"height": "80px", "width": "100%"},
)

content = html.Div(
    className="page-content",
)

footer = dbc.Container(
    dbc.Row(
        dbc.Col(
            html.Hr(
                className="footer",
            ),
        ),
    ),
    fluid=True,
)


@app.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks"), Input("LinkOne", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, nBis, is_open):
    if n or nBis:
        return not is_open
    return is_open


# defining font-awesome and fonts -------------------------------------------------
app.index_string = """
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        {%css%}
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
        <link rel="icon" href="/assets/logos/favicon.svg" type="image/x-icon">
    </head>
    <body>
        {%app_entry%}
        {%config%}
        {%scripts%}
        {%renderer%}
    </body>
</html>

<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto:ital,wght@0,100;0,300;0,400;0,500;0,700;0,900;1,100;1,300;1,400;1,500;1,700;1,900&display=swap');
</style>
"""

# layout -------------------------------------------------
app.layout = html.Div(
    [
        dcc.Location(id="url", pathname="/en"),
        navbar,
        content,
        dash.page_container,
        footer,
    ]
)

if __name__ == "__main__":
    app.run_server(debug=False)
