import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
from textwrap import dedent as d
import json

app = dash.Dash()
app.title = "car prices"
app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})  # setting css
df = pd.read_csv('../data/cars.csv', encoding='latin-1')

dropdown_width = "15%"
year_dropdown_width = "8%"

AVAILABLE_MAKES = sorted(df['make'].unique())
AVAILABLE_MODELS = sorted(df['model'].unique())
AVAILABLE_YEARS = sorted(df['year'].unique())

app.layout = html.Div([

    html.Div([
        dcc.Dropdown(
            id='make-dropdown',
            options=[{'label': i, 'value': i} for i in AVAILABLE_MAKES],
            placeholder="Pick a car make"
        )
    ],
        style={'width': dropdown_width, 'display': 'inline-block'}),

    html.Div([
        dcc.Dropdown(
            id='model-dropdown',
            options=[{'label': i, 'value': i} for i in AVAILABLE_MODELS],
            placeholder="Pick a car model"
        )
    ],
        style={'width': dropdown_width, 'display': 'inline-block'}),

    html.Div(["production year:  "], style={'width': dropdown_width, 'text-align': 'right',
                                            'display': 'inline-block', 'vertical-align': 'middle'}),

    html.Div([
        dcc.Dropdown(
            id='year-from-dropdown',
            options=[{'label': i, 'value': i} for i in AVAILABLE_YEARS],
            placeholder="from...",
            value=min(AVAILABLE_YEARS)
        )
    ],
        style={'width': year_dropdown_width, 'display': 'inline-block', 'margin-left': '10px'}),

    html.Div([
        dcc.Dropdown(
            id='year-to-dropdown',
            options=[{'label': i, 'value': i} for i in AVAILABLE_YEARS],
            placeholder="to...",
            value=max(AVAILABLE_YEARS)
        )
    ],
        style={'width': year_dropdown_width, 'display': 'inline-block'}),


    dcc.Graph(id='graph'),

    html.Div([
        dcc.Markdown(d("""
         **Hover Data**

         Mouse over values in the graph.
     """)),
    ], style={
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }, id='hover-data'),


], style={'marginLeft': 50, 'marginRight': 25})


# show only car models from chosen make
@app.callback(
    dash.dependencies.Output('model-dropdown', 'options'),
    [dash.dependencies.Input('make-dropdown', 'value')])
def set_model_options(selected_make):
    if not selected_make:
        return [{'label': i, 'value': i} for i in AVAILABLE_MODELS]
    all_options = dict()
    for make in df['make'].unique():
        filtered_df = df[df['make'] == make]
        all_options[make] = list(filtered_df.model.unique())

    return [{'label': i, 'value': i} for i in all_options[selected_make]]


# show only car makes which sell chosen model
@app.callback(
    dash.dependencies.Output('make-dropdown', 'options'),
    [dash.dependencies.Input('model-dropdown', 'value')])
def set_model_options(selected_model):
    if not selected_model:
        return [{'label': i, 'value': i} for i in AVAILABLE_MAKES]

    all_options = dict()
    for model in df['model'].unique():
        filtered_df = df[df['model'] == model]
        all_options[model] = list(filtered_df.make.unique())

    return [{'label': i, 'value': i} for i in all_options[selected_model]]


# do not choose any model with no chosen make
@app.callback(
    dash.dependencies.Output('model-dropdown', 'value'),
    [dash.dependencies.Input('model-dropdown', 'options'),
     dash.dependencies.Input('make-dropdown', 'value')])
def set_model_value(available_options, selected_make):
    if not selected_make:
        return None
    return available_options[0]['value']


# show only years later than 'from' chosen
@app.callback(
    dash.dependencies.Output('year-to-dropdown', 'options'),
    [dash.dependencies.Input('year-from-dropdown', 'value')])
def set_year_to_options(selected_year):
    all_options = dict()
    for year in df['year']:
        filtered_df = df[(df.year >= selected_year)]
        all_options[year] = list(filtered_df.year.unique())
    return [{'label': i, 'value': i} for i in sorted(all_options[selected_year])]


# show only years earlier than 'to' chosen
@app.callback(
    dash.dependencies.Output('year-from-dropdown', 'options'),
    [dash.dependencies.Input('year-to-dropdown', 'value')])
def set_year_to_options(selected_year):
    all_options = dict()
    for year in df['year']:
        filtered_df = df[(df.year <= selected_year)]
        all_options[year] = list(filtered_df.year.unique())
    return [{'label': i, 'value': i} for i in sorted(all_options[selected_year])]


# show details on hover
@app.callback(
    dash.dependencies.Output('hover-data', 'children'),
    [dash.dependencies.Input('graph', 'hoverData')])
def display_hover_data(hoverData):
    try:
        pd_index = hoverData['points'][0]['customdata']  # accessing customdata key which is a dataframe row index
        car = df.loc[[pd_index]].values
        make = car[0][0]
        model = car[0][1].replace('_', ' ')
        year = car[0][2]
        mileage = car[0][3] + " km"
        fuel = car[0][4]
        body = car[0][5]
        no_accidents = car[0][6]
        price = car[0][7]
        currency = car[0][8]
        price_with_currency = "{:,}".format(price) + " " + currency

        car_data = dict(
            car=make + " " + model,
            price=price_with_currency,
            production_year=year,
            mileage=mileage,
            fuel_type=fuel,
            body=body,
            no_accidents=no_accidents
        )

        return json.dumps(car_data, indent=4)
    except KeyError:
        return None
    except TypeError:
        pass


# update graph data
@app.callback(
    dash.dependencies.Output('graph', 'figure'),
    [
            dash.dependencies.Input('make-dropdown', 'value'),
            dash.dependencies.Input('model-dropdown', 'value'),
            dash.dependencies.Input('year-from-dropdown', 'value'),
            dash.dependencies.Input('year-to-dropdown', 'value'),
    ]
)
def update_figure(selected_make, selected_model, selected_from_year, selected_to_year):
    # filtered_df = df[df.year <= selected_year[1]]
    filtered_df = df[
        (df.make == selected_make)
        & (df.model == selected_model)
        & (df.year <= selected_to_year)
        & (df.year >= selected_from_year)
        # & (df.make.isin(selected_make))   # this is good when we apply multi choice
    ]
    traces = []
    for i in filtered_df.make.unique():
        df_by_make = filtered_df[filtered_df['make'] == i]
        traces.append(go.Scatter(
            x=df_by_make['mileage'],
            y=df_by_make['price'],
            text=["body type: "+str(make) for make in df_by_make['body']],
            mode='markers',
            opacity=0.7,
            marker={
                'size': 12,
                'line': {'width': 0.5, 'color': 'white'}
            },
            name=i,
            customdata=df_by_make.index,
        ))

    return {
        'data': traces,
        'layout': go.Layout(
            xaxis={'type': 'log', 'title': 'Mileage [km]'},
            yaxis={'title': 'Price [PLN]'},
            margin={'l': 50, 'b': 40, 't': 10, 'r': 40},
            legend={'x': 0, 'y': 1},
            hovermode='closest'
        )
    }


if __name__ == '__main__':
    app.run_server()
