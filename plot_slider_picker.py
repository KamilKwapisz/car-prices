import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go

app = dash.Dash()
app.title = "car prices"
app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})  # setting css
df = pd.read_csv('cars.csv')

available_indicators = df['make'].unique()

app.layout = html.Div([

    html.Div([
        dcc.Dropdown(
            id='make-dropdown',
            options=[{'label': i, 'value': i} for i in available_indicators],
            multi=True,
            placeholder="Pick a car make"
        )
    ],
        style={'width': '24%', 'display': 'inline-block'}),

    dcc.Graph(id='graph-with-slider'),
    dcc.RangeSlider(
        id='year-slider',
        min=df['year'].min(),
        max=df['year'].max(),
        value=[df['year'].min(), df['year'].max()],
        step=None,
        marks={str(year): str(year) for year in df['year']},
        allowCross=False,
    )
], style={'marginLeft': 50, 'marginRight': 25})


@app.callback(
    dash.dependencies.Output('graph-with-slider', 'figure'),
    [dash.dependencies.Input('year-slider', 'value'),
    dash.dependencies.Input('make-dropdown', 'value')
     ])
def update_figure(selected_year, selected_make):
    print(selected_make)
    # filtered_df = df[df.year <= selected_year[1]]
    filtered_df = df[
        (df.year <= selected_year[1])
        & (df.year >= selected_year[0])
        & (df.make.isin(selected_make))
    ]
    traces = []
    for i in filtered_df.make.unique():
        df_by_make = filtered_df[filtered_df['make'] == i]
        traces.append(go.Scatter(
            x=df_by_make['mileage'],
            y=df_by_make['price'],
            text=df_by_make['body'],
            mode='markers',
            opacity=0.7,
            marker={
                'size': 15,
                'line': {'width': 0.5, 'color': 'white'}
            },
            name=i
        ))

    return {
        'data': traces,
        'layout': go.Layout(
            xaxis={'type': 'log', 'title': 'Mileage'},
            yaxis={'title': 'Price'},
            margin={'l': 50, 'b': 40, 't': 10, 'r': 40},
            legend={'x': 0, 'y': 1},
            hovermode='closest'
        )
    }


if __name__ == '__main__':
    app.run_server()
