import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go

app = dash.Dash()
app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})
df = pd.read_csv('cars.csv')

app.layout = html.Div([
    dcc.Graph(
        id='life-exp-vs-gdp',
        figure={
            'data': [
                go.Scatter(
                    x=df[df['make'] == i]['mileage'],
                    y=df[df['make'] == i]['price'],
                    text=df[df['make'] == i]['year'],
                    mode='markers',
                    opacity=0.7,
                    marker={
                        'size': 15,
                        'line': {'width': 0.5, 'color': 'white'}
                    },
                    name=i
                ) for i in df.make.unique()
            ],
            'layout': go.Layout(
                xaxis={'type': 'log', 'title': 'Mileage'},
                yaxis={'title': 'Price'},
                margin={'l': 60, 'b': 40, 't': 10, 'r': 50},
                legend={'x': 0, 'y': 1},
                hovermode='closest'
            )
        }
    )
])


if __name__ == '__main__':
    app.run_server()