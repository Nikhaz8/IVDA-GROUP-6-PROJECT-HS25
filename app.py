from dash import Dash, html, dcc, callback, Output, Input, State, ctx
from dash.exceptions import PreventUpdate
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import dash_mantine_components as dmc
import dash_bootstrap_components as dbc



df = pd.read_csv("run_31_final_dataset_2000_2022_complete(1).csv")
df.columns = [c.replace('_', ' ').title() for c in df.columns]
attribute_names = [c for c in df.columns if c not in ['Year', 'Country', 'Continent', 'Item Id', 'Index', 'Iso3']]
attributes = dict(zip(range(0,27), attribute_names))
app = Dash(__name__)
app.title = 'SDG'
app._favicon = '0.png'
app.layout = html.Div([
    html.Div([
        html.Div([
            html.Div('Select an Attribute to Color the Map:'),
            dcc.Dropdown(
                id='attribute', 
                options=list(attribute_names),
                value='Sdg Index Score'
            )
        ],
            style={
                'position': 'relative',
                'width': '20%'
            }
        ),
        html.Div([
            html.Div('Map Scope: '),
            dcc.RadioItems(
                id='map-mode',
                options=['world', 'africa', 'asia', 'europe', 'north america', 'south america'],
                value='world',
                inline=True
            )
        ]),
        html.Div([
            html.Div('Color By:'),
            dcc.RadioItems(
                id='color-mode',
                options=['Continent', 'Score'],
                value='Continent',
                inline=True
            )
        ]),
        html.Div([
            html.Div('Number of Clusters:'),
            dcc.Dropdown(
                id='clusters', 
                options=['2', '3', '4', '5', '6', '7'],
                value='2',
                disabled=True
            )],
            style={
                'position': 'relative'
            }),
    ],
        style={
            'display': 'flex',
            'justify-content': 'space-between',
            'padding': '15px 15px 15px 15px',
            'border': 'solid'
        }),
    html.Div([
        dcc.Graph(id='world-map'),
        dcc.Graph(id='graph')],   
        style={
            'position': 'relative',
            'zIndex': '0',
            'display': 'flex'
        }),
    html.Div([dcc.Slider(
        df['Year'].min(),
        df['Year'].max(),
        step=None,
        value=df['Year'].min(),
        marks={str(year): str(year) for year in df['Year'].unique()},
        id='year-slider'),
        dbc.ButtonGroup(
            children=[
                dbc.Button(
                    style={
                        'backgroundImage': f'url(assets/{i}.png)', 
                        'backgroundSize': 'cover', 
                        'width': f'{150.0/(len(attributes)+1)}%', 
                        'aspectRatio': '1/1', 
                        'position': 'relative',
                        'borderRadius': '4px'
                    }, title=f'{attributes[i]}', id=f'{attributes[i]}', n_clicks=0, className='inactive') for i in range(0,len(attributes))]
                +[dbc.Button('SELECT ALL',
                    style={'width': f'{150.0/(len(attributes)+1)}%', 
                        'aspectRatio': '1/1', 
                        'position': 'relative',
                        'borderRadius': '4px'
                    }, title='toggle all attributes', id='all', n_clicks=0, className='inactive')]
                +[dbc.Button('CLEAR',
                    style={'width': f'{150.0/(len(attributes)+1)}%', 
                        'aspectRatio': '1/1', 
                        'position': 'relative',
                        'borderRadius': '4px'
                    }, title='clear all attributes', id='clear', n_clicks=0, className='inactive')],
            id='attributes',
            style={
                'display': 'flex',
                'flexFlow': 'row wrap',
                'justifyContent': 'center'
            })],
        style={
            'position': 'sticky',
            'bottom': '0',
            'width': '100%',
            'height': '25vh',
            'overflow': 'hidden',
            'zIndex': '100'
        })
    ],
    style={
    })

'''
fig = go.Figure(data=go.Choropleth(
    locations = filtered_df['Iso3'],
    z = filtered_df[dropdown],
    text = filtered_df['Country'],
    colorscale = 'Blues',
    locationmode = 'ISO-3',
    autocolorscale=False,
    marker_line_color='darkgray',
    marker_line_width=0.5,
    scope=scope
))
'''
def generate_map(filtered_df, scope, selected_year, dropdown, clustering=False):
    if clustering:
        map = px.choropleth(
        locations = filtered_df['Iso3'],
        color = filtered_df['Color'],
        hover_name = filtered_df['Country'],
        locationmode = 'ISO-3',
        scope=scope
        )

        map.update_layout(
            geo=dict(
                showframe=True,
                showcoastlines=False,
                projection_type='robinson'
            ),
            coloraxis_colorbar={'title': ''},
            legend={'title': ''}
        )
        return map
    map = px.choropleth(
        locations = filtered_df['Iso3'],
        color = filtered_df['Color'],
        hover_name = filtered_df['Country'],
        locationmode = 'ISO-3',
        scope=scope
    )

    map.update_layout(
        geo=dict(
            showframe=True,
            showcoastlines=False,
            projection_type='robinson'
        ),
        coloraxis_colorbar={'title': ''},
        legend={'title': ''}
    )
    return map

countries = set()
@callback(
    Output('graph', 'figure'),
    Output('world-map', 'figure'),
    State('world-map', 'figure'), 
    Input('year-slider', 'value'),
    Input('world-map', 'clickData'),
    Input('graph', 'selectedData'),
    Input('attribute', 'value'),
    Input('color-mode', 'value'),
    Input('map-mode', 'value'),
    Input('clusters', 'value'),
    [Input(f'{attributes[i]}', 'n_clicks') for i in range(0, len(attributes))]
)
def update_graphs(worldmap, selected_year, clicks, selection, dropdown, colormode, scope, n_clusters, *args):
    worldmap = worldmap
    country = ''  

    clickData = clicks
    if clickData is not None:
        country = clickData['points'][0]['location']
        print(country)
        if country not in countries:
            countries.add(country)
        else:
            countries.remove(country)

    selected_attributes = [attributes[index] for index in np.nonzero([0 if s == None else s % 2 for s in args])[0].tolist()]
    filtered_df = df.dropna()
    filtered_df['Color'] = filtered_df['Continent']

    for country in filtered_df['Iso3'].unique():
        if country in countries:
            filtered_df.loc[filtered_df['Iso3'] == country, 'Color'] = filtered_df.loc[filtered_df['Iso3'] == country, 'Continent']
        else:
            filtered_df.loc[filtered_df['Iso3'] == country, 'Color'] = 'Other Countries'
    
    if len(selected_attributes) == 0:
        selected_attributes = ['Sdg Index Score']
    
    if len(selected_attributes) == 1:
        line_df = filtered_df
        filtered_df.loc[filtered_df['Iso3'] == country, 'Color'] = filtered_df.loc[filtered_df['Iso3'] == country, 'Country']
        if (len(countries) > 0):
            line_df = filtered_df.loc[filtered_df['Iso3'].isin(countries)]
            print(countries)
        fig = px.line(
            line_df,
            x='Year',
            y=selected_attributes[0],
            markers=True,
            color='Country'
        )
        fig.update_layout(
            transition_duration=500,
            hovermode='x unified'
        )
        filtered_df = filtered_df[filtered_df.Year == selected_year]
        map = generate_map(filtered_df, scope, selected_year, dropdown)

        return [fig, map]
    
    elif len(selected_attributes) == 2:
        filtered_df = filtered_df[filtered_df.Year == selected_year]
        fig = px.scatter(
            filtered_df,
            x=selected_attributes[0], 
            y=selected_attributes[1],
            size="Population", 
            color="Color", 
            hover_name="Country",
            log_x=False,
            log_y=False, 
            size_max=50
        )
        fig.update_layout(transition_duration=500)

        map = generate_map(filtered_df, scope, selected_year, dropdown)

        return [fig, map]
    
    else:
        filtered_df = filtered_df[filtered_df.Year == selected_year]
        filtered_df = filtered_df.dropna().reset_index()
        '''
        multi_fig = px.scatter_matrix(
            filtered_df, 
            dimensions=selected_attributes,
            color="Continent", 
            hover_name="Country"
        )
        multi_fig.update_traces(
            showupperhalf=False
        )
        multi_fig.update_layout(
            transition_duration=500,
        )
        '''
        X = filtered_df[[column for column in attribute_names if column in selected_attributes]].to_numpy()
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        kmeans = KMeans(n_clusters=int(n_clusters), random_state=42, n_init='auto', verbose=False)
        clusters = kmeans.fit_predict(X_scaled)

        pca = PCA(n_components=2, random_state=42)
        X_pca = pca.fit_transform(X_scaled)
        df_pca = pd.DataFrame(data=X_pca, columns=['PC1', 'PC2'])

        filtered_df = pd.concat([filtered_df, df_pca['PC1']], axis=1)
        filtered_df = pd.concat([filtered_df, df_pca['PC2']], axis=1)
        filtered_df['Cluster'] = ['Cluster ' + str(cluster) for cluster in clusters]
        fig = px.scatter(
            filtered_df,
            x='PC1',
            y='PC2',
            color='Cluster',
            hover_name='Country'
        )

        filtered_df.loc[filtered_df['Iso3'] == country, 'Color'] = filtered_df.loc[filtered_df['Iso3'] == country, 'Cluster']
        filtered_df['Color'] = filtered_df['Cluster']
        map = generate_map(filtered_df, scope, selected_year, dropdown, True)

        return [fig, map]

@callback(
    [[Output(f'{attributes[i]}', 'className') for i in range(0, len(attributes))] + [Output('all', 'className')] + [Output('clear', 'className')] + 
     [Output(f'{attributes[i]}', 'n_clicks') for i in range(0, len(attributes))] + [Output('all', 'n_clicks')] + [Output('clear', 'n_clicks')] + 
     [Output('attribute', 'options')] + 
     [Output('color-mode', 'options')] +
     [Output('clusters', 'disabled')]],
    [[Input(f'{attributes[i]}', 'n_clicks') for i in range(0, len(attributes))] + [Input('all', 'n_clicks')] + [Input('clear', 'n_clicks')]]
)
def update_buttons(*args):
    button_id = ctx.triggered_id
    if(button_id == None):
        raise PreventUpdate
    clicks = [0 if n == None else n for n in list(args)]
    output = ['active' if n % 2 == 1 else 'inactive' for n in clicks]
    options = ['Sdg Index Score']
    colormodes = ['Continent', 'Score']
    disabled = True
    for i in range(1, len(output)-2):
        if (output[i] == 'active'):
            options.append(attribute_names[i])
    if(button_id == 'all'):
        output = ['active'] * len(args)
        clicks = [1] * len(args)
        options = attribute_names
    if(button_id == 'clear'):
        clicks = [0] * len(args)
        output = ['inactive'] * len(args)
        options = attribute_names
    if(len(options) > 3):
        colormodes = ['Continent', 'Score', 'Cluster']
        disabled = False
    return [output + clicks + [options] + [colormodes] + [disabled]]
if __name__ == '__main__':
    app.run(debug=True)