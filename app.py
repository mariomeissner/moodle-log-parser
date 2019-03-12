import sys
import dash
import dash_core_components as dcc
import dash_html_components as html

import strings

print(sys.path)

stylesheet = ["./web/style.css"]
app = dash.Dash(__name__, stylesheet=stylesheet)

vistazo_values = [40, 30, 20, "Febrero"]

app.layout = html.Div(
    children=[
        html.Header(children=html.H1(children="Moodle Log Dashboard")),
        html.Div(
            className="main",
            children=[
                html.H2(children="De un vistazo:"),
                html.Table(
                    [
                        html.Tr(
                            [html.Th(name) for name in strings.VISTAZO_HEADERS]
                        ),
                        html.Tr([html.Td(value) for value in vistazo_values]),
                    ]
                ),
            ],
        ),
    ]
)

if __name__ == "__main__":
    app.run_server(debug=True)
