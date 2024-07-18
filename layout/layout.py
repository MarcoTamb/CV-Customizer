from dash import html, callback, Output, Input, State, page_container, dcc
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from utils.constants import GITHUB_URL, PLOTLY_LOGO
from datetime import date


links=[
        html.A(
                "GitHub",
                href=GITHUB_URL,
                className='links'
             ),
      ]


app_layout = html.Div(
        [
            dbc.Navbar(
                dbc.Container(
                    [
                        html.A(
                            # Use row and col to control vertical alignment of logo / brand
                            dbc.Row(
                                [
                                    dbc.Col(html.Img(src=PLOTLY_LOGO, height="30px")),
                                    dbc.Col(dbc.NavbarBrand("CV Customizer", className="ms-2")),
                                ],
                                align="center",
                                className="g-0",
                            ),
                            href='/',
                            style={"textDecoration": "none"},
                        ),
                        dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
                        dbc.Collapse(
                            links,
                            id="navbar-collapse",
                            is_open=False,
                            navbar=True,
                        ),
                    ]
                ),
                color="dark",
                dark=True,
            ), 
            page_container, 
            dmc.NotificationProvider(),
        ],
        className='page'
    )



# add callback for toggling the collapse on small screens
@callback(
    Output("navbar-collapse", "is_open"),
    Input("navbar-toggler", "n_clicks"),
    State("navbar-collapse", "is_open"),
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open