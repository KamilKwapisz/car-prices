import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go

app = dash.Dash()
app.title = "car prices"
app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})  # setting css
df = pd.read_csv('cars.csv')

dropdown_width = "15%"
year_dropdown_width = "8%"

available_makes = df['make'].unique()
available_models = df['model'].unique()
available_years = sorted(df['year'].unique())

app.layout = html.Div([

    html.Div([
        dcc.Dropdown(
            id='make-dropdown',
            options=[{'label': i, 'value': i} for i in available_makes],
            placeholder="Pick a car make"
        )
    ],
        style={'width': dropdown_width, 'display': 'inline-block'}),

    html.Div([
        dcc.Dropdown(
            id='model-dropdown',
            options=[{'label': i, 'value': i} for i in available_models],
            placeholder="Pick a car model"
        )
    ],
        style={'width': dropdown_width, 'display': 'inline-block'}),

    html.Div(["production year:  "], style={'width': dropdown_width, 'text-align': 'right',
                                            'display': 'inline-block', 'vertical-align': 'middle'}),

    html.Div([
        dcc.Dropdown(
            id='year-from-dropdown',
            options=[{'label': i, 'value': i} for i in available_years],
            placeholder="from..."
        )
    ],
        style={'width': year_dropdown_width, 'display': 'inline-block', 'margin-left': '10px'}),

    html.Div([
        dcc.Dropdown(
            id='year-to-dropdown',
            options=[{'label': i, 'value': i} for i in available_years],
            placeholder="to..."
        )
    ],
        style={'width': year_dropdown_width, 'display': 'inline-block'}),


    dcc.Graph(id='graph-with-slider'),
    dcc.RangeSlider(
            id='year-slider',
            min=df['year'].min(),
            max=df['year'].max(),
            value=[df['year'].min(), df['year'].max()],
            step=None,
            marks={str(year): str(year) for year in df['year']},
            allowCross=False,
        ),

], style={'marginLeft': 50, 'marginRight': 25})


@app.callback(
    dash.dependencies.Output('model-dropdown', 'options'),
    [dash.dependencies.Input('make-dropdown', 'value')])
def set_model_options(selected_make):
    all_options = dict()
    for make in df['make'].unique():
        filtered_df = df[df['make'] == make]
        all_options[make] = list(filtered_df.model.unique())

    return [{'label': i, 'value': i} for i in all_options[selected_make]]


@app.callback(
    dash.dependencies.Output('model-dropdown', 'value'),
    [dash.dependencies.Input('model-dropdown', 'options')])
def set_model_value(available_options):
    return available_options[0]['value']


@app.callback(
    dash.dependencies.Output('year-to-dropdown', 'options'),
    [dash.dependencies.Input('year-from-dropdown', 'value')])
def set_year_to_options(selected_year):
    all_options = dict()
    for year in df['year']:
        filtered_df = df[(df.year >= selected_year)]
        all_options[year] = list(filtered_df.year.unique())
    return [{'label': i, 'value': i} for i in sorted(all_options[selected_year])]


@app.callback(
    dash.dependencies.Output('year-from-dropdown', 'options'),
    [dash.dependencies.Input('year-to-dropdown', 'value')])
def set_year_to_options(selected_year):
    all_options = dict()
    for year in df['year']:
        filtered_df = df[(df.year <= selected_year)]
        all_options[year] = list(filtered_df.year.unique())
    return [{'label': i, 'value': i} for i in sorted(all_options[selected_year])]


# @app.callback(
#     dash.dependencies.Output('year-to-dropdown', 'value'),
#     [dash.dependencies.Input('year-to-dropdown', 'options')])
# def set_year_to_value(available_options):
#     return available_options[0]['value']


@app.callback(
    dash.dependencies.Output('graph-with-slider', 'figure'),
    [dash.dependencies.Input('year-slider', 'value'),
    dash.dependencies.Input('make-dropdown', 'value'),
    dash.dependencies.Input('model-dropdown', 'value'),
    dash.dependencies.Input('year-from-dropdown', 'value'),
    dash.dependencies.Input('year-to-dropdown', 'value'),
     ])
def update_figure(selected_year, selected_make, selected_model, selected_from_year, selected_to_year):
    # filtered_df = df[df.year <= selected_year[1]]
    filtered_df = df[
        (df.year <= selected_year[1])
        & (df.year >= selected_year[0])
        # & (df.make.isin(selected_make))   # this is good when we apply multi choice
        & (df.make == selected_make)
        & (df.model == selected_model)
        & (df.year <= selected_to_year)
        & (df.year >= selected_from_year)
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
