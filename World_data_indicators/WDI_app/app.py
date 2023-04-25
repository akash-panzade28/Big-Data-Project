from . import data_processing as d  # my module
from . import dash_html #index page
import logging
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_deck
from dash_extensions import Download
from dash.exceptions import PreventUpdate 
import pydeck
import json
import copy
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import os
from PIL import ImageColor 
from functools import reduce 
import time
import xlsxwriter 
import plotly
import gc
import warnings
warnings.simplefilter('ignore')  
if not os.path.exists("tmp"): os.mkdir("tmp")  
def init_dashboard(server):
    
    """Create a Plotly Dash dashboard."""
    dash_app = dash.Dash(
        server=server,
        routes_pathname_prefix='/',
        external_stylesheets=[
            dbc.themes.FLATLY 
        ],
        update_title=None          
    )

    dash_app._favicon = ("favicon.ico") 
    dash_app.title = "World Data Indicators"
    dash_app.index_string = dash_html.index_string
    create_dash_layout(dash_app)
    init_callbacks(dash_app)
    return dash_app.server

json_resolution = [
    {'label': 'LOW', 'value': "Datasets/ne_110m.geojson"}]

mapbox_style = ["carto-positron"]

geomap_colorscale = ["auto",'inferno','plasma']

discrete_colorscale = [
    ((0.0, '#792069'), (1.0, '#792069')), #purple
    ((0.0, '#FFBB33'), (1.0, '#FFBB33')), #orangy
    ((0.0, '#00cc96'), (1.0, '#00cc96')), #green (0,204,150)       
    ((0.0, '#EF553B'), (1.0, '#EF553B')), #red (239,85,59)    
    ((0.0, '#636efa'), (1.0, '#636efa')), #blue (99,110,25)         
    ((0.0, '#7F8C8D'), (1.0, '#7F8C8D')), #grey
    ((0.0, '#0dc9b6'), (1.0, '#0dc9b6')), #cyan
    ((0.0, '#eac1c1'), (1.0, '#eac1c1')), #yuk pink
    ((0.0, '#fff8b7'), (1.0, '#fff8b7')), #cream
    ((0.0, '#264f7d'), (1.0, '#264f7d')), #navy blue
    ((0.0, '#95b619'), (1.0, '#95b619')), #yellowy
    ((0.0, '#30f8a1'), (1.0, '#30f8a1')), #yukky green
]

# INIT_BORDER_RES = 0
INIT_COLOR_PALETTE = 39 #fall 28 
INIT_COLOR_PALETTE_REVERSE = True
INIT_MAP_STYLE = 1
INIT_TITLE_H = "7vmin" # "7vh"
INIT_TITLE_DIV_H = "7vmin"
INIT_TITLE_PAD_TOP = "-1vmin"
INIT_TITLE_COL = "black"                                
INIT_TITLE_BG_COL = "white"                               
INIT_TITLE_OPACITY = 0.8                                 
INIT_BUTTON_OPACITY = 0.9                               
INIT_BTN_OUTLINE = False
INIT_YEAR_SLIDER_FONTSIZE = "2vmin"
INIT_YEAR_TITLE_FONTSIZE = "3vmin"
INIT_YEAR_SLIDER_FONTCOLOR = 'yellow'
INIT_SELECTION_H = "2vmin"  #was 2.3
INIT_NAVBAR_H = "9vmin"                                
INIT_NAVBAR_W = "100vw" 
INIT_NAVBAR_FONT_H = "1.6vmin"                        
INIT_NAVBAR_SEARCH_WIDTH ='30vw'
INIT_NAVBAR_SEARCH_FONT = "1.6vmin" 
INIT_RANDOM_BTN_TEXT = "RANDOM"
INIT_RANDOM_BTN_FONT = "2vmin"
INIT_MAP_H = "79vh"                                 
INIT_MAP_W = "100vw"
INIT_BAR_H = "60vmin"
INIT_LINE_H = "60vmin"
INIT_BUBBLE_H = "50vmin"
INIT_SUNBURST_H = "60vh"
INIT_JIGSAW_H = "65vh"
INIT_GLOBE_H = "72vh"
INIT_BUTTON_SIZE = '15vw'
INIT_DROPDOWNITEM_LPAD = 0
INIT_DROPDOWNITEM_RPAD = "6vw"
INIT_SETTINGS_BORDER_CARD_WIDTH = "19vh" 
INIT_SETTINGS_MAP_CARD_WIDTH = "18vh" 
INIT_SETTINGS_DL_CARD_WIDTH = '31.5%'
INIT_UGUIDE_MODAL_W = "70%"
INIT_SETTINGS_MODAL_W = "70%"
INIT_GLOBE_MODAL_W = "70%"
INIT_BAR_MODAL_W = "90%"
INIT_DL_MODAL_W = "70%"
INIT_LINE_MODAL_W = "70%"
INIT_BAR_BUBBLE_W = "70%"
INIT_SUNBURST_MODAL_W = "70%"
INIT_JIGSAW_MODAL_W = "70%"
INIT_ABOUT_MODAL_W = "60%"
INIT_AREA51_NAVBAR_W = '35vw'
INIT_NAVFOOTER_W = '97vw' 
INIT_NAVFOOTER_OFFSET = "5.5vmin" 
INIT_NAVFOOTER_BTN_FONT = "1.35vmin" 
INIT_NAVFOOTER_COMPONENT_MINWIDTH = 400
INIT_SOURCE_POPOVER_FONT = "1.5vmin" 
INIT_SOURCE_FONT = "1.5vmin"
INIT_LATITUDE = 24.32570626067931 
INIT_LONGITUDE = 6.365789817509949
INIT_ZOOM = 1.6637151294876884
INIT_FONT_MASTER = ""
INIT_TITLE_FONT = INIT_FONT_MASTER 
INIT_MODAL_HEADER_FONT_GENERAL = INIT_FONT_MASTER 
INIT_MODAL_HEADER_FONT_UGUIDE = INIT_FONT_MASTER
INIT_MODAL_HEADER_FONT_SETTINGS = INIT_FONT_MASTER
INIT_MODAL_HEADER_FONT_ABOUT = INIT_FONT_MASTER
INIT_MODAL_HEADER_FONT_SIZE = "4vmin"
INIT_MODAL_HEADER_FONT_WEIGHT = "bold"
INIT_MODAL_FOOTER_FONT_SIZE = 12
INIT_SUNBURST_MODAL_HEADER_FONT_SIZE = '3vmin'
INIT_LOADER_DATASET_COLOR = "yellow"
INIT_LOADER_CHART_COLOR = "yellow"
INIT_LOADER_CHART_COMPONENT_COLOR = "yellow"
INIT_LOADER_TYPE = 'dash'


country_lookup = d.create_unique_country_list("Datasets/Countries_Mapping.csv")  

dataset_lookup = d.create_dataset_lookup("Datasets/Datasets_Mapping.csv")

pop = d.import_master_dataset(country_lookup, False, False)

DATASETS = len(pd.unique(pop['Series'])) 
OBSERVATIONS = len(pop.index)
SERIES = pd.unique(pop['Series']) 

api_dict_raw_to_label, api_dict_label_to_raw = d.create_api_lookup_dicts(dataset_lookup)

geojson_LOWRES = d.load_geo_data_JSON(json_resolution[0]['value'])
geojson_globe_land_ne110m = d.load_3d_geo_data_JSON_cleaned("Datasets/ne_110m_land_cultural.geojson") 
geojson_globe_ocean_ne110m = d.load_3d_geo_data_JSON_cleaned("Datasets/ne_110m_ocean.geojson") 
del(geojson_globe_ocean_ne110m['features'][0]['geometry']['coordinates'][12]) 

def create_chart_bar(df, series, dropdown_choices):     
        
    series_label = dataset_lookup.loc[dataset_lookup['dataset_raw'] == series].iloc[0,2]
    df['color'] = "rgb(158,202,225)"
    if dropdown_choices != None:
        for i in range(0,len(dropdown_choices)):
            df.loc[df['Country']==dropdown_choices[i], 'color'] = 'black'

    fig = go.Figure([
        go.Bar(
            x=df['Country'],
            y=df['Value'],            
            hovertemplate="%{x} %{y:}<extra></extra>",
            opacity=0.7,
            )
        ])
    fig.update_traces(            
        marker={'color': df['color']},          
        marker_line_width=0,
        opacity=0.7,
    )  
    
    fig.update_layout({
        'plot_bgcolor': 'white',
        'paper_bgcolor': 'white',        
        },
        yaxis_title=series_label,)   
    
    return fig

def create_chart_line(df, series, dropdown_choices):  
    series_label = dataset_lookup.loc[dataset_lookup['dataset_raw'] == series].iloc[0,2]    
    chartdata = pd.DataFrame(np.sort(pd.unique(df["Year"])), columns=["year"]).copy() 
    if dropdown_choices != None:
        for i in range(0,len(dropdown_choices)):
            chartdata[dropdown_choices[i]] = "hello"
            for j in range(0,len(chartdata)):            
                if chartdata.iloc[j][0] in df[(df['Country']==dropdown_choices[i])].Year.values:
                    chartdata.loc[chartdata.year == chartdata.iloc[j][0], dropdown_choices[i]] = df[(df['Country']==dropdown_choices[i]) & (df['Year']==chartdata.iloc[j][0])].iloc[0][4]
                else:                    
                    chartdata.loc[chartdata.year == chartdata.iloc[j][0], dropdown_choices[i]] = None
    if len(dropdown_choices) <=10: width=3
    elif len(dropdown_choices) > 10 and len(dropdown_choices) <= 40: width=2
    else: width=1
    fig = go.Figure()
    if dropdown_choices != None:
        for k in range(0,len(dropdown_choices)):  
            countryname = [dropdown_choices[k]] * len(chartdata)                        
            fig.add_trace(go.Scatter(
                x=chartdata['year'],
                y=chartdata[dropdown_choices[k]],
                name=dropdown_choices[k], 
                showlegend=True,
                customdata=countryname,
                hovertemplate="%{customdata} %{y:} (%{x})<extra></extra>", 
                connectgaps=True, 
                line=dict(width=width),
            ))
        fig.update_layout(
                       yaxis_title=series_label,                       
                       )
    return fig

def create_chart_geobar(series, year, colorscale, gj, jellybean): 
    df = pop[(pop["Year"] == int(year)) & (pop["Series"] == series)].copy() #memory leak ?
    df['Value'] = df['Value'].astype(float)
    df['fix1'] = "dummmy"
    df['fix2'] = "dummy"
    df['r'] = np.random.randint(0, 255, df.shape[0]).astype(str)
    df['g'] = np.random.randint(0, 255, df.shape[0]).astype(str)
    df['b'] = np.random.randint(0, 255, df.shape[0]).astype(str)        
    df['rgb'] = '[' + df['r'].map(str) + ',' + df['g'].map(str) + ',' + df['b'].map(str) + ']'
    df['f-linear'] = df['Value'] / np.max(df["Value"])
    df = df[df.Value > 0]  
    df['value_log10'] = np.log10(df['Value'], out=np.zeros_like(df['Value']), where=(df['Value']!=0))        
    df = df[df.value_log10 != 0]
    mn = np.min(df["value_log10"])
    mx = np.max(df["value_log10"])
    if mn < 0.0:            
        print("Color correction, translating log vals")
        df['value_log10'] = df['value_log10'] + abs(mn)
    df['f-log'] = df['value_log10'] / np.max(df["value_log10"])            
    if colorscale[0][1][0] != "#":
        print("RGB color array found in map data. Converting to hex")
        for i in range(0,len(colorscale)):              
            red = d.extractRed(colorscale[i][1])
            green = d.extractGreen(colorscale[i][1])
            blue = d.extractBlue(colorscale[i][1])
            hx = '#{:02x}{:02x}{:02x}'.format(red, green , blue)
            colorscale[i][1] = hx   
    
    df['c1'] = df.apply(lambda row : d.extractColorPositions(colorscale, row['f-log'])[0], axis =1).astype(str)
    df['c2'] = df.apply(lambda row : d.extractColorPositions(colorscale, row['f-log'])[1], axis =1).astype(str)
    df['mix'] = df.apply(lambda row : d.extractColorPositions(colorscale, row['f-log'])[2], axis =1).astype(float)
    df['hex'] = df.apply(lambda row : d.colorFader(row['c1'], row['c2'], row['mix']), axis =1) 
    if jellybean == False:
        df['r'] = df.apply(lambda row : ImageColor.getcolor(row['hex'], "RGB")[0], axis =1).astype(str) 
        df['g'] = df.apply(lambda row : ImageColor.getcolor(row['hex'], "RGB")[1], axis =1).astype(str)
        df['b'] = df.apply(lambda row : ImageColor.getcolor(row['hex'], "RGB")[2], axis =1).astype(str)
    
    # setup normalisation bins to tame the height of the polygons (target a max of 5000000, it's a map quirk in deck.gl)        
    mx = np.max(df["Value"])
    norm = 1 #default normalisation multiplier
    if mx < 10:
        norm = 500000
    elif mx < 100:
        norm = 50000
    elif mx < 1000:
        norm = 10000
    elif mx < 10000:
        norm = 1000 #drop to 500?
    elif mx < 100000:
        norm = 50
    elif mx < 1000000:
        norm = 10 #testing
    elif mx < 10000000:
        norm = 1
    elif mx < 100000000:
        norm = 0.1
        
    elevation = "VALUE * {:f}".format(norm) 
    for i in range(0, len(gj['features'])):
        try:
            if gj['features'][i]['properties']['UN_A3'] == '010':
                print("removing antactica from json!")
                del gj['features'][i]
        except IndexError as error:
            print("Area51: Exception thrown trying to remove antactica")
    
    for i in range(0, len(gj['features'])):
        try:                               
            if gj['features'][i]['properties']['UN_A3'] not in df["m49_un_a3"].values:
                gj['features'][i]['COUNTRY'] = gj['features'][i]['properties']['BRK_NAME']              
                gj['features'][i]['VALUE'] = "no data"                    
                gj['features'][i]['properties']['MAPCOLOR7'] = "224" 
                gj['features'][i]['properties']['MAPCOLOR8'] = "224"
                gj['features'][i]['properties']['MAPCOLOR9'] = "224"
            else:             
                gj['features'][i]['COUNTRY'] = df[df["m49_un_a3"]==gj['features'][i]['properties']['UN_A3']].iloc[0,1] #Country name                
                gj['features'][i]['VALUE'] = df[df["m49_un_a3"]==gj['features'][i]['properties']['UN_A3']].iloc[0,4] #value                      
                gj['features'][i]['properties']['MAPCOLOR7'] = df[df["m49_un_a3"]==gj['features'][i]['properties']['UN_A3']].iloc[0,10] #Red
                gj['features'][i]['properties']['MAPCOLOR8'] = df[df["m49_un_a3"]==gj['features'][i]['properties']['UN_A3']].iloc[0,11] #Green
                gj['features'][i]['properties']['MAPCOLOR9'] = df[df["m49_un_a3"]==gj['features'][i]['properties']['UN_A3']].iloc[0,12] #Blue   
        
        except IndexError as error:
            print("Area51: Exception thrown attempting to build custom dict from json (expected)")
    
    mapbox_api_token = os.getenv("MAPBOX_ACCESS_TOKEN")      
            
    LAND_COVER = [
        [[-123.0, 49.196], [-123.0, 49.324], [-123.306, 49.324], [-123.306, 49.196]]
    ]
    
    INITIAL_VIEW_STATE = pydeck.ViewState(
        latitude=30.44, longitude=27.60, zoom=1.3, max_zoom=10, pitch=45, bearing=0
    )  
    
    polygon = pydeck.Layer(
        "PolygonLayer",
        LAND_COVER,
        stroked=False,           
        get_polygon="-",
        get_fill_color=[180, 0, 200, 140], 
    )                
    
    geojson = pydeck.Layer(
        "GeoJsonLayer", 
        gj,           
        opacity=0.8,
        stroked=False,
        filled=True,
        extruded=True,
        wireframe=True,
        pickable=True,
        auto_highlight=True,            
        get_elevation=elevation,
        get_fill_color="[properties.MAPCOLOR7*1,properties.MAPCOLOR8*1,properties.MAPCOLOR9*1]", 
        get_line_color=[255, 255, 255], 
    )
    
    r = pydeck.Deck(
        layers=[polygon, geojson],
        initial_view_state=INITIAL_VIEW_STATE,
        mapbox_key=mapbox_api_token, 
    )
    
    geobar = dash_deck.DeckGL(r.to_json(),
                              id="deck-gl",
                              mapboxKey=r.mapbox_key,
                              tooltip={"text": "{COUNTRY} {VALUE}"},                                 
                              )
    return geobar

def create_chart_globe(gj_land, gj_ocean):
    mapbox_api_token = os.getenv("MAPBOX_ACCESS_TOKEN") 
    layers = [
        
        
        pydeck.Layer(
            "GeoJsonLayer",
            id="base-map",
            data=gj_ocean, 
            stroked=False,
            filled=True, 
            pickable=False, 
            auto_highlight=True,
            get_line_color=[60, 60, 60],
            get_fill_color="[properties.red*1,properties.green*1,properties.blue*1]",
            opacity=0.5,
        ),
        
        pydeck.Layer(
            "GeoJsonLayer",
            id="base-map",
            data=gj_land, 
            stroked=False,
            filled=True, 
            pickable=True,
            auto_highlight=True,
            get_line_color=[60, 60, 60],
            get_fill_color="[properties.red*1,properties.green*1,properties.blue*1]",
            opacity=0.5,
        ),    
        
    ]
    
    r = pydeck.Deck(
        views=[pydeck.View(type="_GlobeView", controller=True)], # , width=1500, height=750
        initial_view_state=pydeck.ViewState(latitude=51.47, longitude=0.45, zoom=0.85),
        layers=layers,                  
        parameters={"cull": True}, 
    ) 
    
    globe = dash_deck.DeckGL(
        json.loads(r.to_json()),
        id="deck-gl",
        style={"background-color": "white"},
        #tooltip=True,
        tooltip={"text": "{COUNTRY} {VALUE}"}, 
        mapboxKey=mapbox_api_token, 
    ),
      

    return globe

def create_map_geomap_empty():
    fig = go.Figure(
        go.Choroplethmapbox(        
        )
    )
    fig.update_layout(
        mapbox_style=mapbox_style[0], #default
        mapbox_zoom=INIT_ZOOM,
        mapbox_center={"lat": INIT_LATITUDE, "lon": INIT_LONGITUDE},   
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
    )
    return fig

def create_map_geomap(df, geojson, series, zoom, center, selected_map_location, mapstyle, colorbarstyle, colorpalette_reverse):      

    if series == None: return create_map_geomap_empty()
    var_type = dataset_lookup.loc[dataset_lookup['dataset_raw'] == series].iloc[0,5]        
    if var_type == "discrete":
        print("Discrete data found. Dataframe length is:", len(df))     
        hovertemp = "%{customdata}: %{text}<extra></extra>" 
        fig = go.Figure()
        for i, discrete_classes in enumerate(df['Value'].unique()):
            t = df[df["Value"] == discrete_classes]
            gj = copy.deepcopy(geojson)
            gj['features'].clear()
            for j in range(0,len(geojson['features'])):                
                if geojson['features'][j]['properties']['UN_A3'] in t.m49_un_a3.values:                    
                    gj['features'].append(geojson['features'][j])                
            fig.add_choroplethmapbox(geojson=gj, 
                                     locations=t.m49_un_a3,
                                     z=[i,] * len(t),                                     
                                     featureidkey="properties.UN_A3", 
                                     showlegend=True,
                                     name=discrete_classes,
                                     customdata=t['Country'],  
                                     text=t['Value'],
                                     hovertemplate=hovertemp,
                                     colorscale=discrete_colorscale[i],                                     
                                     showscale=False,
                                     marker_opacity=0.5,
                                     marker_line_width=1)
           
                    
        fig.update_layout(
            mapbox_style=mapstyle,
            mapbox_zoom=zoom,
            mapbox_center=center, #{"lat": -8.7, "lon": 34.5},
            margin={"r": 0, "t": 0, "l": 0, "b": 0},        
        )
        
        return fig
    else:
        hovertemp = "%{customdata} %{text:,.2f}<extra></extra>" 
        if df["Value"].astype(float).mean() > 1000: hovertemp = "%{customdata} %{text:,d}<extra></extra>" 
        fig = go.Figure(
            go.Choroplethmapbox(
                geojson=geojson,
                locations=df.m49_un_a3,                 
                featureidkey="properties.UN_A3",                
                z=np.log10(df['Value'].astype(float)), 
                text=df['Value'],
                customdata=df['Country'],                
                hoverinfo="location+text",
                hovertemplate=hovertemp,             
                colorscale=colorbarstyle,
                reversescale=colorpalette_reverse,
                colorbar= {'ticks': '', 'title': {'text': 'HIGH', 'side': 'top', 'font': {'color': 'yellow', 'size': 16}}, 'showticklabels': False, 'bgcolor': 'rgba(0,0,0,0)', 'outlinewidth':0},
                zauto=True,
                marker_opacity=0.5,
                marker_line_width=1,
            )
        )
        fig.update_layout(
            paper_bgcolor='black',
            plot_bgcolor='black',
            mapbox_style=mapstyle,
            mapbox_zoom=zoom,
            mapbox_center=center,
            margin={"r": 0, "t": 0, "l": 0, "b": 0},              
        )
     
    return fig

def create_dash_layout(app):
    header = create_dash_layout_header()
    navbar = create_dash_layout_navbar()
    body = create_dash_layout_body()                   
    nav_footer = create_dash_layout_nav_footer()    
    dcc_stores = create_dash_layout_dcc_stores()
    hidden_div_triggers = create_dash_hidden_div_triggers()
    js_callback_clientside_blur(app)
    js_callback_clientside_share(app)
    js_callback_clientside_viewport(app)
    api = dcc.Location(id='url', refresh=False) 
    app.layout = html.Div([navbar, header, body, nav_footer, dcc_stores, hidden_div_triggers, api])    
    return app

def js_callback_clientside_blur(dash_app):
        dash_app.clientside_callback(
            """
            function() {
                //alert("Blur function trigger");
                //document.getElementById("some-other-component").focus();
                document.getElementById("about-button").blur();
                document.getElementById("uguide-button").blur();
                document.getElementById("settings-button").blur();
                document.getElementById("download-button").blur();
                document.getElementById("bar-button").blur();
                document.getElementById("line-button").blur();
                document.getElementById("sunburst-button").blur();
                document.getElementById("globe-button").blur();
                document.getElementById("geobar-button").blur();
                document.getElementById("bubble-button").blur();
                document.getElementById("button-userguide-about").blur();
                //document.getElementById("download-popover").blur();
                return {};
            }
            """,
            Output('blur-hidden-div', 'style'),
            Input('about-button', 'n_clicks'),
            Input("uguide-button", 'n_clicks'),
            Input("settings-button", 'n_clicks'),
            Input("bar-button", 'n_clicks'),
            Input("line-button", 'n_clicks'),
            Input('sunburst-button', 'n_clicks'),
            Input("globe-button", 'n_clicks'),
            Input("geobar-button", 'n_clicks'),
            Input("bubble-button", 'n_clicks'),
            Input("button-userguide-about", 'n_clicks'),
            prevent_initial_call=True
        )
        return 

def js_callback_clientside_share(dash_app):
        dash_app.clientside_callback(        
            """
            function(path,label) {
                //alert(label);
                document.title = 'World Indicators - ' + label;
                shareon();            
            }
            """,
            Output('js-social-share-dummy', 'children'),        
            Input('js-social-share-refresh', 'children'),
            State("my-series-label","data"), 
            prevent_initial_call=True
        )
        return

def js_callback_clientside_viewport(dash_app):
    dash_app.clientside_callback(            
        """
        function() {
            //alert("Screen size: "+ screen.width +"x"+ screen.height + " pixels." + "Available screen size: "+ screen.availWidth +"x"+ screen.availHeight );
        
            return {
                'width': screen.width,
                'height': screen.height                 
            }                       
        }
        """,
        Output('js-detected-viewport', 'data'),               
        Input('js-detected-viewport-dummy', 'children'),        
        prevent_initial_call=False
    )
    return

def create_dash_layout_dcc_stores():
    
    dcc_stores = html.Div([
        dcc.Store(id='my-settings_json_store', storage_type='memory'),
        dcc.Store(id='my-settings_mapstyle_store', storage_type='memory'),
        dcc.Store(id='my-settings_colorbar_store', storage_type='memory'),
        dcc.Store(id='my-settings_colorbar_reverse_store', storage_type='memory'),  
        dcc.Store(id='my-series', storage_type='memory'),
        dcc.Store(id='my-series-label', storage_type='memory'),
        dcc.Store(id='my-year', storage_type='memory'),        
        dcc.Store(id='my-selection-m49', storage_type='memory'), #unused, for selecting region of geomap I think        
        dcc.Store(id='my-series-bar', storage_type='memory'),
        dcc.Store(id='my-year-bar', storage_type='memory'),
        dcc.Store(id='my-series-line', storage_type='memory'),        
        dcc.Store(id='my-xseries-bubble', storage_type='memory'),
        dcc.Store(id='my-yseries-bubble', storage_type='memory'),
        dcc.Store(id='my-zseries-bubble', storage_type='memory'),
        dcc.Store(id='my-year-bubble', storage_type='memory'),        
        dcc.Store(id='my-pizza-sunburst', storage_type='memory'),
        dcc.Store(id='my-toppings-sunburst', storage_type='memory'),
        dcc.Store(id='my-year-sunburst', storage_type='memory'),        
        dcc.Store(id="my-url-main-callback", storage_type='memory'),  #stores href data    
        dcc.Store(id="my-url-bar-callback", storage_type='memory'),
        dcc.Store(id="my-url-line-callback", storage_type='memory'),       
        dcc.Store(id="my-url-globe-callback", storage_type='memory'),
        dcc.Store(id="my-url-jigsaw-callback", storage_type='memory'),
        dcc.Store(id="my-url-root", storage_type='memory'),
        dcc.Store(id="my-url-path", storage_type='memory'),
        dcc.Store(id="my-url-series", storage_type='memory'),
        dcc.Store(id="my-url-year", storage_type='memory'),
        dcc.Store(id="my-url-view", storage_type='memory'),
        dcc.Store(id="my-url-map-trigger", storage_type='memory'),
        dcc.Store(id="my-url-bar-trigger", storage_type='memory'),
        dcc.Store(id="my-url-line-trigger", storage_type='memory'),
        dcc.Store(id="my-url-globe-trigger", storage_type='memory'),
        dcc.Store(id="my-url-jigsaw-trigger", storage_type='memory'),
        dcc.Store(id="js-detected-viewport", storage_type='memory'),
        ]) 
    return dcc_stores

def create_dash_hidden_div_triggers():
    triggers = html.Div([
        html.Div("Test div", id="timeslider-hidden-div", style={"display":"none"}), 
        html.Div("Test div", id="settings-hidden-div", style={"display":"none"}),
        html.Div("Test div", id="blur-hidden-div", style={"display":"none"}),
        html.Div("Test div", id="blur-hidden-div-menu", style={"display":"none"}),
        html.Div("Test div", id="js-social-share-refresh", style={"display":"none"}),
        html.Div("Test div", id="js-social-share-dummy", style={"display":"none"}),        
        html.Div("Test div", id="js-detected-viewport-dummy", style={"display":"none"}),

        ],style={"display":"none"})
    return triggers

def create_dash_layout_header():
            
    #title of app in page
    title = html.Div(
        style={"marginBottom": 0,
                                        "marginTop": INIT_TITLE_PAD_TOP,
                                        "marginLeft": 0,
                                        'textAlign': 'center',                                        
                                        'height': INIT_TITLE_DIV_H }, 
        )
   
    
    loader_main = html.Div(
                dcc.Loading(
                type=INIT_LOADER_TYPE,
                color=INIT_LOADER_DATASET_COLOR, 
                children=html.Span("Please select an indicator", id="my-loader-main", style={"marginBottom": 0, "marginTop": 10, "marginLeft": 0, 'textAlign': 'center', 'fontSize': '1vw', 'fontFamily': 'Helvetica', 'fontWeight': '',},), #style of span
                style={'textAlign': 'center' } 
                ),style={'textAlign': 'center', 'position':'absolute', 'bottom':'-37.5vw','left':'68vw', 'color': 'yellow'}, #style of div
    )
     
    header = dbc.Container([
        dbc.Row([
            dbc.Col([title, loader_main]),        
            ])            
        ],
        style={"marginBottom": 0,
               "marginTop": 0,
               "marginLeft": 0,
               "marginRight": 0,
               "max-width": "none",
               "width": "100vw",
               "position": "absolute",
               "z-index": "2",
               }) 
            
    
    return header

def create_dash_layout_navbar():
    navbar = html.Div([
        
        dbc.Row(
                children=create_dash_layout_navbar_menu(),      
                style={'margin-left': '1vw', 'margin-right': '1vw', 'display': 'flex', 'vertical-align': 'top' , 'align-items': 'center', 'justify-content': 'center'  }, 
                className="ml-auto"), 
        ], 
               
        style={"height": INIT_NAVBAR_H,
               "width": INIT_NAVBAR_W,
               "zIndex":2,
               "backgroundColor": 'black',
               'display': 'flex',
               'vertical-align': 'top',
               'align-items': 'center',
               'justify-content': 'center',               
               "marginBottom": 0,
               "marginTop": 0,
               "marginLeft": 0,
               "marginRight": 0,
               
               }, 
        
    )  
    return navbar

def create_dash_layout_navbar_items(nav_cat):
    items = []
    df = dataset_lookup[dataset_lookup['nav_cat']==nav_cat]
    nests = pd.unique(df['nav_cat_nest'])
    if len(nests) == 1 and nests[0] == 'root':
        for i in range(0,len(df)):    
                items.append(
                    dbc.DropdownMenuItem(
                        children=df.iloc[i][2], 
                        id=df.iloc[i][0], 
                        ))
    else:
        for i in range(0,len(nests)):            
            if nests[i] == 'root':
                r = df[df['nav_cat_nest']=='root'] 
                for j in range(0,len(r)):    
                    items.append(
                        dbc.DropdownMenuItem(
                            children=r.iloc[j][2], 
                            id=r.iloc[j][0]   
                            ))
            else:
                items.append(
                    dbc.DropdownMenu(
                        label=nests[i],
                        direction='left',
                        toggle_style={'color':'grey', 'backgroundColor':'white', 'border': '0px', 'fontSize': INIT_NAVBAR_FONT_H, "marginBottom": 0, "marginTop": 0, "marginLeft": INIT_DROPDOWNITEM_LPAD, "marginRight": INIT_DROPDOWNITEM_RPAD,}, 
                        children=create_dash_layout_navbar_items_nests(nests[i], df),  
                    )
                )          
    
    return items

def create_dash_layout_navbar_items_nests(nest, df):
    items = []
    r = df[df['nav_cat_nest']==nest] 
    for j in range(0,len(r)):    
        items.append(
            dbc.DropdownMenuItem(                
                children=r.iloc[j][2], #dataset_label
                id=r.iloc[j][0] #dataset_id        
                ))    
    
    return items

def create_dash_layout_navbar_menu():    
    menu_list=[]   
    dd = dataset_lookup.sort_values(by="dataset_label")     
    dd = dd.drop_duplicates(subset=['dataset_raw'])
    
    search_menu_list = []
    for i in range(0,len(dd)):        
        search_menu_list.append({'label': dd.iloc[i][2], 'value': dd.iloc[i][1]})
    yellow_text = html.Div(
    'World Data Indicator',
    style={
        'color': 'yellow',
        'font-weight': 'bold',
        'margin-right': '15vw',
        'font-size': '2vw'
    })
    menu_list.append(yellow_text)
    menu_list.append(
        dcc.Dropdown(
        options=search_menu_list,
        id="nav-search-menu",
        multi=False,
        placeholder=f'Search World Indicator ',
        clearable=True,
        style={
            'margin-right': '10vw',
            'width': '40vw',
            'fontSize': INIT_NAVBAR_SEARCH_FONT,
            'backgroundColor': 'yellow',
            
        }),
        )
    
    nav_cats = pd.unique(dataset_lookup['nav_cat'])
    for i in range(0,len(nav_cats)):
        if nav_cats[i] == "unused":
            display="none"
        else:
            display="block"        
        colour = dataset_lookup.loc[(dataset_lookup['nav_cat'] == nav_cats[i])].iloc[0]['colour'] 
        menu_list.append(
            dbc.DropdownMenu(
                children=create_dash_layout_navbar_items(nav_cats[i]),                
                bs_size="sm",
                label=nav_cats[i], 
                toggle_style={"display":"none" , "color": colour, 'backgroundColor':'#3E3F3A', 'border': '0px', 'fontSize': INIT_NAVBAR_FONT_H, "marginBottom": 0, "marginTop": 0, "marginLeft": INIT_DROPDOWNITEM_LPAD, "marginRight": INIT_DROPDOWNITEM_RPAD,},               
            ))
            
        
        
    menu_list.append(dbc.Button(INIT_RANDOM_BTN_TEXT,  outline=INIT_BTN_OUTLINE, color="danger", id="random-button", style={'display': 'inline-block', 'fontSize': INIT_RANDOM_BTN_FONT, "marginBottom": 0, "marginTop": 0, "marginLeft": INIT_DROPDOWNITEM_LPAD, "marginRight": INIT_DROPDOWNITEM_RPAD,'border':'1px solid yellow','background-color':'black'}, size='50px'),)
       
    return menu_list

def create_dash_layout_body():
    
    body = html.Div(
        children=[
            dcc.Loading(
                type=INIT_LOADER_TYPE,
                color=INIT_LOADER_CHART_COLOR, 
                children=html.Span(id="my-loader-geobar"),
                style={"zIndex":1, 'display': 'flex', 'vertical-align': 'center' , 'align-items': 'center', 'justify-content': 'center', "marginTop": '50vh'},
                ),
            dcc.Loading(                
                type=INIT_LOADER_TYPE,
                color=INIT_LOADER_CHART_COLOR, 
                children=html.Span(id="my-loader-line"),
                style={"zIndex":1, 'display': 'flex', 'vertical-align': 'center' , 'align-items': 'center', 'justify-content': 'center', "marginTop": '50vh'},
            ),
    
            dcc.Loading(                
                type=INIT_LOADER_TYPE,
                color=INIT_LOADER_CHART_COLOR,
                children=html.Span(id="my-loader-globe"),
                style={"zIndex":1, 'display': 'flex', 'vertical-align': 'center' , 'align-items': 'center', 'justify-content': 'center', "marginTop": '50vh'},
                ),
            
            dcc.Loading(                
                type=INIT_LOADER_TYPE,
                color=INIT_LOADER_CHART_COLOR, #hex colour close match to nav bar
                children=html.Span(id="my-loader-bar"),
                style={"zIndex":1, 'display': 'flex', 'vertical-align': 'center' , 'align-items': 'center', 'justify-content': 'center', "marginTop": '50vh'},
            ),

            dcc.Loading(                
                type=INIT_LOADER_TYPE,
                color=INIT_LOADER_CHART_COLOR, #hex colour close match to nav bar
                children=html.Span(id="my-loader-xp"),
                style={"zIndex":1, 'display': 'flex', 'vertical-align': 'center' , 'align-items': 'center', 'justify-content': 'center', "marginTop": '50vh'},
            ),

            dcc.Graph(
                style={"height": INIT_MAP_H, "width": INIT_MAP_W, 'z-index':'2','border':'5px light blue', 'float':'center' }, 
                id="geomap_figure",
                figure = create_map_geomap_empty(),
                config={'displayModeBar': False },              
            )
        ],)
    return body

def create_dash_layout_bargraph_modal():
    
    m =  dbc.Modal(
                [                            
                    dbc.ModalHeader(html.Div(id="bar-graph-modal-title",style={"fontFamily":INIT_MODAL_HEADER_FONT_GENERAL, "fontSize": INIT_MODAL_HEADER_FONT_SIZE, "fontWeight": INIT_MODAL_HEADER_FONT_WEIGHT }), ),                           
                    
                    dbc.ModalBody(html.Div([     
                        dbc.Row([                        
                            dbc.Col([                        
                                html.H5("Select Countries"),
                                dcc.Dropdown(
                                    options=[],
                                    id="bar-graph-dropdown-countrieselector",
                                    multi=True,
                                    placeholder='Select countries or type to search',
                                ),
                            ]),                            
                            dbc.Col([
                                html.H5("Select Indicator"),
                                dcc.Dropdown(
                                    options=[],
                                    id="bar-graph-dropdown-dataset",
                                    multi=False,
                                    placeholder='Select Indicator or type to search',
                                ),
                            ]),
                            dbc.Col([
                                html.H5("Select year"),
                                dcc.Dropdown(
                                    options=[],
                                    id="bar-graph-dropdown-year",
                                    multi=False,
                                    placeholder='Select year',
                                    clearable=False,
                                ),
                            ],width=2),
                        ], style={'marginBottom':10}),
                        dcc.Loading(
                            type=INIT_LOADER_TYPE,
                            color=INIT_LOADER_CHART_COMPONENT_COLOR,              
                            children=html.Span(id="my-loader-bar-refresh"),
                            style={"zIndex":1, 'display': 'flex', 'vertical-align': 'center' , 'align-items': 'center', 'justify-content': 'center', 'paddingTop':50 },
                        ),
                        
                        # the main bargraph
                        dcc.Graph(id='bar-graph',
                                  style={"backgroundColor": "#1a2d46", 'color': '#ffffff', 'height': INIT_BAR_H},
                                  config={'displayModeBar': False },),
                    ])),                           
                    
                    dbc.ModalFooter([
                        html.Div([
                            html.Span("Data source: "),
                            html.Span(id='bar-graph-modal-footer'), 
                            html.Div(dcc.Link(href='', target="_blank", id="bar-graph-modal-footer-link", style={'display':'inline-block'})),
                        ], style={"fontSize": INIT_MODAL_FOOTER_FONT_SIZE, } ),
                       
                            
                        html.Div([                           
                            dbc.Button("Close", id="modal-bar-close", className="mr-1", size=INIT_BUTTON_SIZE),
                        ],className="ml-auto"),                        
                        
                    ]),
                ],
                id="dbc-modal-bar",
                centered=True,
                size="xl",
                style={"max-width": "none", "width": INIT_BAR_MODAL_W, 'max-height': "100vh"} 
            )
    
    return m

def create_dash_layout_linegraph_modal():
    m = dbc.Modal(
            [                            
                dbc.ModalHeader(html.H1(id="line-graph-modal-title",style={"fontFamily":INIT_MODAL_HEADER_FONT_GENERAL, "fontSize": INIT_MODAL_HEADER_FONT_SIZE, "fontWeight": INIT_MODAL_HEADER_FONT_WEIGHT }),),                           
                
                dbc.ModalBody(html.Div([                    
                    dbc.Row([                    
                        
                        dbc.Col([                    
                            html.H5("Select countries"),                            
                            dcc.Dropdown(
                                options=[],
                                value=['United States of America', 'China', 'India', 'United Kingdom'],
                                id="line-graph-dropdown-countries",
                                multi=True,
                                placeholder='Select countries',
                                #style={'max-height': '100px'},
                            ),                             
                            
                            dbc.Button("Select all countries",  outline=True, color="secondary", id="linegraph-allcountries-button", style={"marginLeft": 0, 'marginTop':10, "marginBottom": 0, 'display': 'inline-block', 'opacity':INIT_BUTTON_OPACITY}, size=INIT_BUTTON_SIZE),
                            dbc.Button("Remove all countries",  outline=True, color="secondary", id="linegraph-nocountries-button", style={"marginLeft": 10, 'marginTop':10, "marginBottom": 0, 'display': 'inline-block', 'opacity':INIT_BUTTON_OPACITY}, size=INIT_BUTTON_SIZE),
                            
                             dbc.Tooltip(
                                "Only for the brave!",
                                target='linegraph-allcountries-button',
                                placement='bottom',                
                                ),
                                                        
                        ]),
                        dbc.Col([                        
                            html.H5("Select Indicator"),
                            dcc.Dropdown(
                                options=[],
                                id="line-graph-dropdown-dataset",
                                multi=False,
                                placeholder='Select Indicator or type to search'
                            ),
                        ]),                        
                    ]),                    
                    
                    dcc.Loading(
                        type=INIT_LOADER_TYPE,
                        color=INIT_LOADER_CHART_COMPONENT_COLOR,
                        children=html.Span(id="my-loader-line-refresh"),
                        style={"zIndex":1, 'display': 'flex', 'vertical-align': 'center' , 'align-items': 'center', 'justify-content': 'center', 'paddingTop':100 },
                    ),
                    
                    dcc.Graph(id='line-graph',
                              animate=False,
                              style={"backgroundColor": "#1a2d46", 'color': '#ffffff', 'height': INIT_LINE_H},
                              config={'displayModeBar': False },),])),                           
                
                dbc.ModalFooter([
                    
                    html.Div([   
                        html.Span("Data source: "),
                        html.Span(id='line-graph-modal-footer'),
                        html.Div(dcc.Link(href='', target="_blank", id="line-graph-modal-footer-link")),
                    ], style={'fontSize':INIT_MODAL_FOOTER_FONT_SIZE}), #end div
                    
                    html.Div([
                        dbc.Button("Close", id="modal-line-close", className="mr-1", size=INIT_BUTTON_SIZE)
                        
                    ], className='ml-auto'),                    
                ]), #end footer
                
            ],
            id="dbc-modal-line",
            centered=True,
            size="xl",
            style={"max-width": "none", "width": INIT_LINE_MODAL_W} 
        )
    return m

def create_dash_layout_globe_modal():
    m = dbc.Modal(
                [
                    dbc.ModalHeader(html.Div(html.H1(id="globe-modal-title",style={"fontFamily":INIT_MODAL_HEADER_FONT_GENERAL, "fontSize": INIT_MODAL_HEADER_FONT_SIZE, "fontWeight": INIT_MODAL_HEADER_FONT_WEIGHT })),),
                    
                    dbc.ModalBody([
                        html.Div(id='globe-body', style={'height': INIT_GLOBE_H, },),
                        
                        # loader for globe refreshes
                        dcc.Loading(
                            #id="my-loader-geobar",
                            type=INIT_LOADER_TYPE,
                            color=INIT_LOADER_CHART_COMPONENT_COLOR, #hex colour close match to nav bar ##515A5A
                            children=html.Span(id="my-loader-globe-refresh"),
                            style={"zIndex":1, 'display': 'flex', 'vertical-align': 'center' , 'align-items': 'center', 'justify-content': 'center', },
                        ),
                    
                        
                        ]), 
                    dbc.ModalFooter([                           
                                    html.Div([
                                        html.Span("Data source: "),
                                        html.Span(id='globe-modal-footer'), 
                                        html.Div(dcc.Link(href='', target="_blank", id="globe-modal-footer-link", style={'display':'inline-block'})),
                                    ], style={"fontSize": INIT_MODAL_FOOTER_FONT_SIZE, } ),
                                    html.Div([
                                        dbc.Button("", color="white", id="modal-globe-ne50m", disabled='True',className="mr-1", size=0 ),
                                        dbc.Button("Change Color", color="success", id="modal-globe-jelly", className="mr-1", size=INIT_BUTTON_SIZE),
                                        dbc.Button("Close", id="modal-globe-close", className="mr-1", size=INIT_BUTTON_SIZE ),
                                    ], className="ml-auto", style={'display':'inline-block'}) ,
                        ],),
                    dbc.Tooltip(
                                "Ignore",
                                target='modal-globe-ne50m',
                                placement='top',
                                style={}, 
                    ),
                ],
                id="dbc-modal-globe",
                centered=True,
                size="xl",
                style={"max-width": "none", "width": INIT_GLOBE_MODAL_W} #85%
            )
    return m

def create_dash_layout_geobar_modal():
    m = dbc.Modal(
            [
                dbc.ModalHeader(html.Div([
                    html.H1(id="geobar-modal-title",style={"fontFamily":INIT_MODAL_HEADER_FONT_GENERAL, "fontSize": INIT_MODAL_HEADER_FONT_SIZE, "fontWeight": INIT_MODAL_HEADER_FONT_WEIGHT }),
                    
                ]),),
                
                dbc.ModalBody([                  
                    html.Div(id='geobar-test', style={'height': INIT_JIGSAW_H, 'display': 'flex', 'align-items': 'center', 'justify-content': 'center'},),  
                    
                     # loader for component refreshes
                    dcc.Loading(                        
                        type=INIT_LOADER_TYPE,
                        color=INIT_LOADER_CHART_COMPONENT_COLOR, #hex colour close match to nav bar ##515A5A
                        children=html.Span(id="my-loader-geobar-refresh"),
                        style={"zIndex":1, 'display': 'flex', 'vertical-align': 'center' , 'align-items': 'center', 'justify-content': 'center', },
                    ),
                
                ]), #, 'width': INIT_JIGSAW_W
                
                dbc.ModalFooter([
                            
                            html.Div([
                                html.Span("Data source: "),
                                html.Span(id='geobar-modal-footer'), 
                                html.Div(dcc.Link(href='', target="_blank", id="geobar-modal-footer-link",)),
                            ], style={"fontSize": INIT_MODAL_FOOTER_FONT_SIZE, 'display':'inline-block'} ),
                      
                            html.Div([
                                dbc.Button("Change Color", color="success", id="modal-geobar-jelly", className="mr-1",size=INIT_BUTTON_SIZE),
                                dbc.Button("Close", id="modal-geobar-close", className="mr-1",size=INIT_BUTTON_SIZE),
                            ], className="ml-auto" ), 
                            
                        ]),
                
                
            ],
            id="dbc-modal-geobar",
            centered=True,
            size="xl",
            style={"max-width": "none", "width": INIT_JIGSAW_MODAL_W} #85%
        )
    return m

def create_dash_layout_nav_footer():
    nav_footer = html.Div(
        [                  
            dbc.Row(
                [
                    dbc.Col(
                            html.Div([                                     
                                  
                                  dbc.Row([                                                                 
                                  dbc.Button("", outline=INIT_BTN_OUTLINE, color="", className="mr-1", id="download-button", disabled=True, style={"marginLeft": 0, "marginBottom": 10, 'display': 'none', 'opacity':INIT_BUTTON_OPACITY, 'fontSize': INIT_NAVFOOTER_BTN_FONT}, size=INIT_BUTTON_SIZE), #disabled on initial
                                  Download(id='download_dataset_main'),                                  
                                  ]),

                                  dbc.Row([
                                  dbc.Button("",  color="", className="mr-1", id="bubble-button",disabled= True, style={"marginLeft": 0, "marginBottom": 0, 'display': 'none', 'fontSize': 0}),
                                  dbc.Button("",  color="", className="mr-1", id='sunburst-button',disabled= True, style={"marginLeft": 0, "marginBottom": 0, 'display': 'none', 'fontSize': 0}), #disabled on initial                              
                                  dbc.Button("BAR", outline=INIT_BTN_OUTLINE, color="dark", className="mr-1", id="bar-button", style={"marginLeft": 0, "marginBottom": 0, 'display': '', 'fontSize': INIT_NAVFOOTER_BTN_FONT}, size=INIT_BUTTON_SIZE), #disabled on initial 
                                  dbc.Button("LINE", outline=INIT_BTN_OUTLINE, color="dark", className="mr-1", id="line-button", style={"marginLeft": 0, "marginBottom": 0,'display':'',  'fontSize': INIT_NAVFOOTER_BTN_FONT}, size=INIT_BUTTON_SIZE), #disabled on initial 
                                  dbc.Button("GEOBAR", outline=INIT_BTN_OUTLINE, color="dark", className="mr-1", id="geobar-button", style={"marginLeft": 0, "marginBottom": 0, 'display': '', 'fontSize': INIT_NAVFOOTER_BTN_FONT}, size=INIT_BUTTON_SIZE),
                                  dbc.Button("GLOBE", outline=INIT_BTN_OUTLINE, color="dark", className="mr-1", id="globe-button", style={"marginLeft": 0, "marginBottom": 0, 'display': '', 'fontSize': INIT_NAVFOOTER_BTN_FONT}, size=INIT_BUTTON_SIZE),
                                  ]),     
                               
                            ],
                            id = 'button-panel-style',
                            style = {'display': 'inline-block', "marginLeft":"1vw",} 
                            ),                           
                        style={"marginBottom": 5, "marginLeft": 10,'backgroundColor': 'dark', 'width':'40%', 'display':'block', 'minWidth':INIT_NAVFOOTER_COMPONENT_MINWIDTH, }, #formatting for column
                        align='end',                          
                              
                    ),
                    
                    
                    dbc.Tooltip(
                        "Learn how to use this site",
                        target='uguide-button',
                        placement='top',
                        style={},
                    ), 
                                    
                                    
                    dbc.Tooltip(
                        "Compare countries for different Indicators and year",
                        target='bar-button',
                        placement='top',
                        style={},
                    ),
                    
                    dbc.Tooltip(
                        "Compare trends across years for a different indicator",
                        target='line-button',
                        placement='top',
                        style={},
                    ),                    
                    
                    dbc.Tooltip(
                        "View the current map as an interactive 3d globe",
                        target='globe-button',
                        placement='top',
                        style={},
                    ),
                    
                    dbc.Tooltip(
                        "Compare up to three datasets",
                        target='bubble-button',
                        placement='top',
                        style={},
                    ),
                    
                    dbc.Tooltip(
                        "Think of a pie chart on steroids",
                        target='sunburst-button',
                        placement='top',
                        style={},
                    ),
                    
                    dbc.Tooltip(
                        "Turn the current map into a jigsaw puzzle (geo-bar) graph",
                        target='geobar-button',
                        placement='top',
                        style={},
                    ),
                    
                    
                    #Globe view modal                
                    create_dash_layout_globe_modal(),                    
                    
                    #Jigsaw view modal                
                    create_dash_layout_geobar_modal(),                    
                    
                    #Bar graph modal                     
                    create_dash_layout_bargraph_modal(),
                    
                    #Line graph modal                     
                    create_dash_layout_linegraph_modal(),
                    
                               
                    #Year Slider Column
                    dbc.Col([
                    #html.Div([ 
                        
                        html.Div("YEAR", 
                                 style={'fontWeight': 'bold', 'color': 'yellow', 'fontSize': INIT_YEAR_SLIDER_FONTSIZE, 'align-items': 'center', 'justify-content': 'center','display': 'none', 'marginBottom':'0.5vmin', },
                                 id='year-slider-title'), 
                        
                        html.Div([                                
                              
                            dcc.Slider(
                                id='year-slider',
                                min=0,
                                max=0,
                                #marks={ 0: {'label':'2005', 'style':{'color':'red', 'fontSize':12}}}, #dummy data. Overwritten
                                #marks={}, #dummy data. Overwritten
                                marks={0: {'label': '2020', 'style': {'fontSize': 14, 'color': 'yellow', 'fontWeight': 'bold'}}},
                                value=0, 
                                included=False,                                
                                #disabled=True,
                            )],
                            
                            id='year-slider-style', #div id
                            style={'display': 'none'}, #use only one style value, to udpate with callback (initially slider is invisible)
                        ),
                        ], 
                        style={"marginTop": 15, "marginLeft": 0, 'backgroundColor': 'transparent', 'width':'33%', 'display':'inline-block', 'minWidth':INIT_NAVFOOTER_COMPONENT_MINWIDTH}, #use col to move slider down
                        align='end',
                    ),
                    
                    #Data source column
                    dbc.Col(
                    #html.Div(

                        [
                              
                            html.Div([
                                html.Span("", style={'fontSize':'0.8vw'}),
                                html.Span("", id="my-source", style={'fontSize':'0.8vw'}),
                                #html.Span(" "),
                                html.Div(dcc.Link(href='', target="_blank", id="my-source-link", style={'fontSize':INIT_SOURCE_FONT, 'color':'LightBlue'})),
                                #html.Span(")")
                            ], id="source-popover-target", style={"marginBottom": 0, "marginTop": 0, "marginLeft": 0, "marginRight": 0,"fontSize": INIT_SOURCE_POPOVER_FONT, 'color':'yellow'}),
                            
                            dbc.Popover(
                                [
                                dbc.PopoverHeader("Dummy", style={'fontWeight':'bold'}),
                                dbc.PopoverBody("Dummy"),
                                ],
                                id="source-popover",
                                #is_open=False,
                                target="source-popover-target",
                                style={'maxHeight': '4px', 'overflowY': 'auto', },
                                trigger="",
                                placement="top",
                                hide_arrow=False,
                                #style={'backgroundColor': INIT_TITLE_BG_COL, 'opacity': INIT_TITLE_OPACITY,'color':INIT_TITLE_COL, 'width':'100%'}
                            ),                            
                       ],
                    id = 'data-source-style',
                    style = {'display': ''}, #default hidden 
                    align='end',               
                    
                    ),                                                      
                ],                
            ),
            
            
        ],style={
                "width": "100vw",
                "bottom": 0,
                "background-color": "black",
            },
    )
    return nav_footer

def init_callbacks(dash_app):


    #COMPLETE INPUT LIST FOR MAIN CALLBACK
    def callback_main_create_inputs():
        #this should return the input chain for this callback
        
        c=[]
        
        #construct input triggers for timeslider and settings changes   
        c.append(Input("timeslider-hidden-div", "children"))
        #c.append(Input('geomap_figure', 'clickData'))
        c.append(Input('my-settings_json_store', 'data')) #these act purely as triggers after apply button pushed (like the hidden div), to call the main callback
        c.append(Input('my-settings_mapstyle_store', 'data')) #these act purely as triggers after apply button pushed (like the hidden div), to call the main callback
        
        #extract array of dataset ids from dataset_lookup   
        ids = dataset_lookup['dataset_id'].to_numpy()
        
        #recursively add input ids for all datasets in dataset_lookup
        for i in range(0,len(ids)):         
            c.append(Input(ids[i],"n_clicks"))                        
        #print(c)
        
        #add random button
        c.append(Input('random-button', "n_clicks"))
        
        #add search menu
        c.append(Input('nav-search-menu', 'value'))
        
        #add api
        c.append(Input('my-url-map-trigger', 'data'))        
        
        return c


    #Main callback for handling dataset selection change
    @dash_app.callback(
        [
            Output("my-series","data"),
            Output("my-series-label","data"),
            Output("geomap_figure", "figure"),
            Output("my-source", "children"),
            Output("my-source-link", "href"),         
            Output("download-button", "style"), #download button                         
            Output("bar-button", "style"),
            Output("line-button", "style"),
            Output("geobar-button", "style"),
            Output("sunburst-button", "style"),
            Output("globe-button", "style"),
            Output("bubble-button", "style"),        
            Output('my-year', "data"),
            Output('my-loader-main', "children"), #used to trigger loader. Use null string "" as output
            Output('button-panel-style', "style"), #used to hide initially
            Output('year-slider-style', "style"), #used to hide initially
            Output('data-source-style', 'style'), #used to hide initially         
            Output("year-slider", "max"),         
            Output("year-slider", "marks"),
            Output("year-slider", "value"),         
            Output("year-slider-title","style"),
            Output("year-slider-title","children"),
            Output("my-selection-m49", "data"), #NEW, to save the m49 location of the selected map
            #Output("my-series-data","data"),         
            Output("my-url-main-callback","data"), #to set url in another callback
            Output("my-url-bar-trigger", "data"),  # chain to bar
            Output("my-url-line-trigger", "data"), # chain to line
            Output("my-url-globe-trigger", "data"),# chain to globe
            Output("my-url-jigsaw-trigger", "data"),# chain to globe
            Output("source-popover","children"), #popover with explanatory notes
            # Output("my-experimental-trigger", "data") #trigger for experimental modal  
        
        ],
        
        callback_main_create_inputs(), #build list of input items programmatically 
        
        [
            State("geomap_figure", "figure"),
            State("year-slider", "marks"),
            State("year-slider", "max"),
            State("year-slider", "value"),
            State("my-series","data"),        
            State("my-series-label","data"),        
            State('my-settings_json_store', 'data'), #allows data intself to be extracted
            State('my-settings_mapstyle_store', 'data'), #allows data intself to be extracted
            State("my-settings_colorbar_store", 'data'),
            State("my-settings_colorbar_reverse_store", 'data'),
            State('nav-search-menu', 'value'), #new
            State("my-selection-m49", "data"), #NEW, to save the m49 location of the selected map
            State("my-url-path", "data"),        
            State("my-url-root", 'data'),
            State('my-url-map-trigger', 'data'),
            State("my-url-series", 'data'),
            State("my-url-year", 'data'),
            State("my-url-view", 'data'),
            State("js-detected-viewport", 'data'),         
    
        ],
        prevent_initial_call=True
    )
    def callback_main(*args):
        ctx = dash.callback_context 
        selection = ctx.triggered[0]["prop_id"].split(".")[0] 
        print("Selection triggered is", selection)
        
        # retrieve dcc component states from states dict
        states = ctx.states
        zoom = states["geomap_figure.figure"]["layout"]["mapbox"]["zoom"]
        center = states["geomap_figure.figure"]["layout"]["mapbox"]["center"]
        series = states["my-series.data"] #this is initially "No data selected"   
        series_label = states["my-series-label.data"] 
        year_slider_marks = states["year-slider.marks"]
        year_slider_max = states["year-slider.max"]
        year_slider_selected = states["year-slider.value"]
        search_menu = states["nav-search-menu.value"]  
        settings_json = states['my-settings_json_store.data']
        settings_mapstyle = states['my-settings_mapstyle_store.data']
        settings_colorpalette = states['my-settings_colorbar_store.data']
        settings_colorpalette_reverse = states['my-settings_colorbar_reverse_store.data']
        selection_m49 = states['my-selection-m49.data']        
        search_query = states['my-url-path.data'] 
        maptrigger = 'map'
        url_view = 'map' 
        url_year = states['my-url-year.data']  #api        
        viewport = states['js-detected-viewport.data'] 

        geojson = geojson_LOWRES    
        mapstyle = mapbox_style[0] #default cartoposition        
        colorbarstyle = geomap_colorscale[2] #39 inferno,  #55 plasma 
        if settings_colorpalette_reverse is None: settings_colorpalette_reverse = INIT_COLOR_PALETTE_REVERSE #i.e. set to default if nothing returned from store
        
        selected_map_location = "none"
        navbtm_btns_style = {'display': 'block', 'marginLeft': "1vw", 'marginBottom':0, 'opacity':INIT_BUTTON_OPACITY,'color':'green'} #used to hide/display entire button panel
        navbtm_yr_style = {'display': 'block', 'marginBottom':5, 'marginRight':30} #display
        navtm_yr_title_style = {'fontWeight': 'bold', 'color': 'yellow', 'fontSize': INIT_YEAR_TITLE_FONTSIZE, 'align-items': 'center', 'justify-content': 'center','display': 'flex', 'marginBottom':'0.5vmin', 'marginRight':30}
        navbtm_source_style = {'display': 'inline-block', 'backgroundColor': 'transparent', 'width':'33%', 'minWidth':INIT_NAVFOOTER_COMPONENT_MINWIDTH} #display source     
        download_btn_style = {"marginBottom": 10, 'display': 'inline-block', 'fontSize': INIT_NAVFOOTER_BTN_FONT} #inline-block is the key to not adding line break!!!
        bar_btn_style = {'display': 'inline-block','position':'relative','left':'0.8vw','bottom':'2vh', 'fontSize':'1vw','border':'1px solid yellow','background-color':'black'} #display!
        line_btn_style = {'display': 'inline-block','position':'relative','left':'1.8vw','bottom':'2vh', 'fontSize': '1vw','border':'1px solid yellow','background-color':'black'} #display!
        geobar_btn_style = {'display': 'inline-block','position':'relative','left':'2.8vw','bottom':'2vh', 'fontSize': '1vw','border':'1px solid yellow','background-color':'black'} #display!
        sunburst_btn_style = { 'display': 'inline-block', 'fontSize': '1vw'} #display!
        globe_btn_style = { 'display': 'inline-block','position':'relative','left':'3.8vw','bottom':'2vh', 'fontSize': '1vw','border':'1px solid yellow','background-color':'black'} #display!
        bubble_btn_style = { 'display': 'inline-block', 'fontSize': '1vw'} #display!
        
        #setup source for normal operation
        if series == None:
            source = "No data selected"
            link = ""
            year=""
        else:            
            source = d.get_source(dataset_lookup, series)
            link = dataset_lookup.loc[dataset_lookup['dataset_raw'] == series].iloc[0,4]     
            year = int(d.get_years(pop.loc[(pop['Series'] == series)])[year_slider_selected]) #expensive            

        if selection == "geomap_figure":
            selected_map_location = ctx.triggered[0]['value']['points'][0]['location'] #this is the M49 code of selected country
            selection_m49 = selected_map_location
        
        #YEAR SLIDER CHANGE
        elif selection == "timeslider-hidden-div":  
            # reset fonts
            for i in range(0,len(year_slider_marks)):
                year_slider_marks[str(i)]['style']['fontWeight']='normal'     
            year_slider_marks[str(year_slider_selected)]['style']['fontWeight']='bold'
            
            
        #SETTINGS CHANGE
        elif selection == "my-settings_json_store":   
            if series == None:
                navbtm_yr_style = {'display': 'none'}
                navtm_yr_title_style = {'fontWeight': 'bold', 'color': INIT_YEAR_SLIDER_FONTCOLOR, 'fontSize': INIT_YEAR_SLIDER_FONTSIZE, 'align-items': 'center', 'justify-content': 'center','display': 'none', 'marginBottom':'0.5vmin',}
                navbtm_source_style = {'display': 'none'}            
                download_btn_style = {'display': 'none'}
                bar_btn_style = {'display': 'none'}
                line_btn_style = {'display': 'none'}
                geobar_btn_style = {'display': 'none'}
                sunburst_btn_style = {'display': 'none'}
                globe_btn_style = {'display': 'none'}
                bubble_btn_style = {'display': 'none'}
        
        # API SEARCH
        elif selection == "my-url-map-trigger":            
            url_view = states['my-url-view.data']  #override
            maptrigger = states['my-url-map-trigger.data']  #override        
            
            if search_query == '/' : raise PreventUpdate()
            
            # split query into a list
            query = search_query.split('/')        
            print("query: ",query,"length:",len(query))          
                    
            # /series/year/map
            if len(query) == 4:
                api_series = query[1]
                api_year = query[2]
            
            else: raise PreventUpdate("Break from main callback. Invalid API input")
                
            # check if series valid
            try:        
                series = api_dict_label_to_raw[api_series]            
            except KeyError as error:
                print("series not found, breaking out of callback")
                raise PreventUpdate()                      
            print("Series query:",series)
            year = api_year
            if year != 'x':            
                year_check = d.check_year(pop, series, year) #expensive
                if year_check == False:
                    print("Year not found in dataset, breaking out of callback")
                    raise PreventUpdate()       
            else:
                # grab years and auto select most recent
                year_dict = d.get_years(pop.loc[(pop['Series'] == series)])
                year_index = list(year_dict)[-1]
                year = year_dict[year_index] 
                
            # update all vars        
            series_label = dataset_lookup.loc[dataset_lookup['dataset_raw'] == series].iloc[0,2]        
            source = d.get_source(dataset_lookup, series)
            link = dataset_lookup.loc[dataset_lookup['dataset_raw'] == series].iloc[0,4]     
            year_slider_marks = d.get_year_slider_marks(series, pop, INIT_YEAR_SLIDER_FONTSIZE, INIT_YEAR_SLIDER_FONTCOLOR, year_slider_selected)
            year_slider_max = len(year_slider_marks)-1                        
            year_slider_selected = d.get_year_slider_index(pop, series, year)
            year_slider_marks[year_slider_selected]['style']['fontWeight']='bold' #mark selected year bold          
        else:
            if selection == 'nav-search-menu':
                if search_menu != None and search_menu != '': series = search_menu
            elif selection == 'random-button':            
                series = SERIES[np.random.randint(0,len(SERIES))] 
            else:
                series = dataset_lookup.loc[dataset_lookup['dataset_id'] == selection].iloc[0,1]
            series_label = dataset_lookup.loc[dataset_lookup['dataset_raw'] == series].iloc[0,2]  
            source = d.get_source(dataset_lookup, series)
            link = dataset_lookup.loc[dataset_lookup['dataset_raw'] == series].iloc[0,4]     
            year_dict = d.get_years(pop.loc[(pop['Series'] == series)])
            if len(year_dict) > 0:
                year_index = list(year_dict)[-1]
                year = year_dict[year_index]
                year_slider_marks = d.get_year_slider_marks(series, pop, INIT_YEAR_SLIDER_FONTSIZE, INIT_YEAR_SLIDER_FONTCOLOR, year_slider_selected)
                year_slider_max = len(year_slider_marks)-1
                year_slider_selected = year_slider_max 
                year_slider_marks[year_slider_selected]['style']['fontWeight']='bold'          
        if series != None:       
                
            if dataset_lookup.loc[dataset_lookup['dataset_raw'] == series].iloc[0,5] == "discrete":
                print("Main callback: discrete dataset found")            
                navbtm_yr_style = {'display': 'block'}            
                geobar_btn_style = {'display': 'none'}
                sunburst_btn_style = {'display': 'none'}
                bar_btn_style = {'display': 'none'}
                line_btn_style = {'display': 'none'}
                bubble_btn_style = {'display': 'none'}        
        if len(year_slider_marks) < 2:
            navbtm_yr_style = {'display': 'none'} #hid
            navtm_yr_title_style = {'fontWeight': 'bold', 'color': INIT_YEAR_SLIDER_FONTCOLOR, 'fontSize': INIT_YEAR_SLIDER_FONTSIZE, 'align-items': 'center', 'justify-content': 'center','display': 'flex', 'marginBottom':'0.5vmin',}
            navbtm_yr_title_val = "YEAR: "+str(year)
        else:
            navbtm_yr_title_val = "YEAR"
        
        # set URL path to return
        root_path = states['my-url-root.data']    
        if url_view == "": url_view = 'map'  
        if series != None: path = api_dict_raw_to_label[series]+"/"+str(year)+'/'+url_view #fix for experimental first load 
        else: path = ""        
        url = root_path+path                     
        if series != None:
            popover_children = [
            dbc.PopoverHeader("Explanatory Notes"),
            dbc.PopoverBody(dataset_lookup.loc[dataset_lookup['dataset_raw'] == series].iloc[0,11]),
            ]
        else: popover_children = []
        
        print('SELECTION is ',selection)
        df = pop.loc[(pop['Series'] == series) & (pop['Year'] == int(year))].sort_values('Country')   
        
        return \
        series, series_label, \
        create_map_geomap(df, geojson, series, zoom, center, selected_map_location, mapstyle, colorbarstyle, settings_colorpalette_reverse), \
        source, link, \
        download_btn_style, bar_btn_style, line_btn_style, geobar_btn_style, sunburst_btn_style, globe_btn_style, bubble_btn_style, \
        year, \
        series_label+" in "+str(year), \
        navbtm_btns_style, navbtm_yr_style, navbtm_source_style,\
        year_slider_max, year_slider_marks, year_slider_selected, navtm_yr_title_style, navbtm_yr_title_val, \
        selection_m49, \
        url, \
        maptrigger, maptrigger, maptrigger, maptrigger, \
        popover_children

    @dash_app.callback(               
                [
                Output('url', 'href'),
                Output('js-social-share-refresh','children'),
                ],
                [
                Input("my-url-main-callback","data"),
                Input("my-url-bar-callback","data"),
                Input("my-url-line-callback","data"),
                Input("my-url-globe-callback","data"),
                Input("my-url-jigsaw-callback","data"),
                
                
                ],  
                prevent_initial_call=True)
    def callback_api_set_URL(url_maincb, url_bar, url_line, url_globe, url_jigsaw):       
        ctx = dash.callback_context 
        trigger = ctx.triggered[0]["prop_id"].split(".")[0] 
        if trigger == 'my-url-main-callback': return url_maincb, url_maincb
        elif trigger == 'my-url-bar-callback': return url_bar, url_bar
        elif trigger == 'my-url-line-callback': return url_line, url_line
        elif trigger == 'my-url-globe-callback': return url_globe, url_line
        elif trigger == 'my-url-jigsaw-callback': return url_jigsaw, url_jigsaw        
        
        return None
    @dash_app.callback([
                Output("my-url-root", 'data'), 
                Output("my-url-path", 'data'),            
                Output("my-url-series", 'data'),
                Output("my-url-year", 'data'),
                Output("my-url-view", 'data'),   
                Output("my-url-map-trigger", "data"),                
                ],
                [
                Input('url', 'href'),               
                ], 
                State('url', 'pathname'),              
                prevent_initial_call=True)
    def callback_api_get_URL(href, pathname):

        blah = href.split('/') 
        root = blah[0]+'//'+blah[2]+'/'
        if len(blah) == 4:
            #print('FIRST LOAD DETECTED')
            series = ""
            year = ""
            view = ""
        else:
            series = blah[3]
            year = blah[4]
            view = blah[5]            
        if view == 'map': maptrigger = 'map'      
        elif view == 'bar': maptrigger = 'bar'
        elif view == 'line': maptrigger = 'line'
        elif view == 'globe': maptrigger = 'globe'
        elif view == 'jigsaw': maptrigger = 'jigsaw'
        else: maptrigger = ''           
        path_chk = '/'+series+'/'+year+'/'+view
        if pathname != '/':
            if pathname != path_chk:
                pathname = '/'

        return root, pathname, series, year, view, maptrigger

    def callback_settings_create_outputs():            
        c=[]
        c.append(Output('settingsbtn-resolution-low', "active"))
        c.append(Output('settingsbtn-resolution-med', "active"))
        c.append(Output('settingsbtn-resolution-high', "active"))     
        c.append(Output('settingsbtn-mapstyle-openstreetmap', "active"))
        c.append(Output('settingsbtn-mapstyle-carto-positron', "active"))
        c.append(Output('settingsbtn-mapstyle-darkmatter', "active"))
        c.append(Output('settingsbtn-mapstyle-stamen-terrain', "active"))
        c.append(Output('settingsbtn-mapstyle-stamen-toner', "active"))
        c.append(Output('settingsbtn-mapstyle-stamen-watercolor', "active"))
  
        for i in geomap_colorscale:
            c.append(Output(i,"active"))

        c.append(Output('settingsbtn-reverse-colorscale', "active"))
        c.append(Output('settingsbtn-normal-colorscale', "active"))    

        return c

    def callback_settings_create_inputs():       
        c=[]    
        c.append(Input('settingsbtn-resolution-low', "n_clicks"))
        c.append(Input('settingsbtn-resolution-med', "n_clicks"))
        c.append(Input('settingsbtn-resolution-high', "n_clicks"))     
        c.append(Input('settingsbtn-mapstyle-openstreetmap', "n_clicks"))
        c.append(Input('settingsbtn-mapstyle-carto-positron', "n_clicks"))
        c.append(Input('settingsbtn-mapstyle-darkmatter', "n_clicks"))
        c.append(Input('settingsbtn-mapstyle-stamen-terrain', "n_clicks"))
        c.append(Input('settingsbtn-mapstyle-stamen-toner', "n_clicks"))
        c.append(Input('settingsbtn-mapstyle-stamen-watercolor', "n_clicks"))    
        c.append(Input("dbc-modal-settings", "is_open")) 
        for i in geomap_colorscale:         
            c.append(Input(i,"n_clicks"))                        

        c.append(Input('settingsbtn-reverse-colorscale', "n_clicks"))
        c.append(Input('settingsbtn-normal-colorscale', "n_clicks"))
        
        return c
    def callback_settings_create_states():        
        c=[]
        c.append(State('settingsbtn-resolution-low', "active")) 
        c.append(State('settingsbtn-resolution-med', "active"))
        c.append(State('settingsbtn-resolution-high', "active"))    
        c.append(State('settingsbtn-mapstyle-openstreetmap', "active"))
        c.append(State('settingsbtn-mapstyle-carto-positron', "active"))
        c.append(State('settingsbtn-mapstyle-darkmatter', "active"))
        c.append(State('settingsbtn-mapstyle-stamen-terrain', "active"))
        c.append(State('settingsbtn-mapstyle-stamen-toner', "active"))
        c.append(State('settingsbtn-mapstyle-stamen-watercolor', "active"))
        c.append(State('my-settings_json_store', 'data'))
        c.append(State('my-settings_mapstyle_store', 'data'))
        c.append(State("my-settings_colorbar_store", 'data'))
        c.append(State("my-settings_colorbar_reverse_store", 'data'))
        for i in geomap_colorscale:
            c.append(State(i,"active"))
        c.append(State('settingsbtn-reverse-colorscale', "active"))
        c.append(State('settingsbtn-normal-colorscale', "active"))
        return c 
    @dash_app.callback(   
        
        callback_settings_create_outputs(), 
        
        callback_settings_create_inputs(),    
        
        callback_settings_create_states(),
            
        prevent_initial_call=True,
    )
    def callback_settings(nbtn_low, nbtn_med, nbtn_high, 
                                nbtn_ms_1, nbtn_ms_2, nbtn_ms_3, nbtn_ms_4, nbtn_ms_5, nbtn_ms_6,
                                settings_modal_open,
                                nc1, nc2, nc3, nc4, nc5, nc6, nc7, nc8, nc9, nc10, nc11, nc12, nc13, nc14, nc15, nc16, nc17, nc18, nc19, nc20, nc21, nc22, nc23, nc24, nc25, nc26, nc27, nc28, nc29, nc30, nc31, nc32, nc33, nc34, nc35, nc36, nc37, nc38, nc39, nc40, nc41, nc42, nc43, nc44, nc45, nc46, nc47, nc48, nc49, nc50, nc51, nc52, nc53, nc54, nc55, nc56, nc57, nc58, nc59, nc60, nc61, nc62, nc63, nc64, nc65, nc66, nc67, nc68, nc69, nc70, nc71, nc72, nc73, nc74, nc75, nc76, nc77, nc78, nc79, nc80, nc81, nc82, nc83, nc84, nc85, nc86, nc87, nc88, nc89, nc90, nc91, nc92, nc93, \
                                nbtn_reverse, nbtn_normal,
                                btn_low_active, btn_med_active, btn_high_active,
                                btn_openstreetmap_active, btn_cartopositron_active, btn_darkmatter_active, btn_stamenterrain_active, btn_stamentoner_active, btn_stamenwatercolor_active,                             
                                settings_json_store, settings_mapstyle_store, settings_colorbar_store, settings_colorbar_reverse_store,
                                nc1a, nc2a, nc3a, nc4a, nc5a, nc6a, nc7a, nc8a, nc9a, nc10a, nc11a, nc12a, nc13a, nc14a, nc15a, nc16a, nc17a, nc18a, nc19a, nc20a, nc21a, nc22a, nc23a, nc24a, nc25a, nc26a, nc27a, nc28a, nc29a, nc30a, nc31a, nc32a, nc33a, nc34a, nc35a, nc36a, nc37a, nc38a, nc39a, nc40a, nc41a, nc42a, nc43a, nc44a, nc45a, nc46a, nc47a, nc48a, nc49a, nc50a, nc51a, nc52a, nc53a, nc54a, nc55a, nc56a, nc57a, nc58a, nc59a, nc60a, nc61a, nc62a, nc63a, nc64a, nc65a, nc66a, nc67a, nc68a, nc69a, nc70a, nc71a, nc72a, nc73a, nc74a, nc75a, nc76a, nc77a, nc78a, nc79a, nc80a, nc81a, nc82a, nc83a, nc84a, nc85a, nc86a, nc87a, nc88a, nc89a, nc90a, nc91a, nc92a, nc93a, \
                                btn_reverse_active, btn_normal_active
                                ):
        
        ctx = dash.callback_context 
        selection = ctx.triggered[0]["prop_id"].split(".")[0]         
        if selection == 'settingsbtn-resolution-low' or selection == 'settingsbtn-resolution-med' or selection == 'settingsbtn-resolution-high':
            print("resolution button push detected")
            if selection == 'settingsbtn-resolution-low':
                print("button low pushed")
                btn_low_active = True
                btn_med_active = False
                btn_high_active = False 
            
            elif selection == 'settingsbtn-resolution-med': 
                print("button med pushed")
                btn_low_active = False
                btn_med_active = True
                btn_high_active = False        
            
            elif selection == 'settingsbtn-resolution-high': 
                print("button high pushed")
                btn_low_active = False
                btn_med_active = False
                btn_high_active = True        
            
            else:
                print("Error with resolution button logic.")

        elif selection == 'settingsbtn-reverse-colorscale' or selection == 'settingsbtn-normal-colorscale':
            if selection == 'settingsbtn-reverse-colorscale':
                btn_reverse_active = True
                btn_normal_active = False
            elif selection == 'settingsbtn-normal-colorscale':
                btn_reverse_active = False
                btn_normal_active = True
        elif selection == 'settingsbtn-mapstyle-openstreetmap' or selection == 'settingsbtn-mapstyle-carto-positron' or selection == 'settingsbtn-mapstyle-darkmatter' or selection == 'settingsbtn-mapstyle-stamen-terrain' or selection =='settingsbtn-mapstyle-stamen-toner' or selection == 'settingsbtn-mapstyle-stamen-watercolor':
            if selection == 'settingsbtn-mapstyle-openstreetmap':
                    print("Btn open street map pushed bitch")
                    btn_openstreetmap_active = True
                    btn_cartopositron_active = False
                    btn_darkmatter_active = False
                    btn_stamenterrain_active = False
                    btn_stamentoner_active = False
                    btn_stamenwatercolor_active = False
                
            elif selection == 'settingsbtn-mapstyle-carto-positron':
                    print("Btn carto positron bitch")
                    btn_openstreetmap_active = False
                    btn_cartopositron_active = True
                    btn_darkmatter_active = False
                    btn_stamenterrain_active = False
                    btn_stamentoner_active = False
                    btn_stamenwatercolor_active = False
                    
            elif selection == 'settingsbtn-mapstyle-darkmatter':
                    print("Btn dark hoe")
                    btn_openstreetmap_active = False
                    btn_cartopositron_active = False
                    btn_darkmatter_active = True
                    btn_stamenterrain_active = False
                    btn_stamentoner_active = False
                    btn_stamenwatercolor_active = False
                    
            elif selection == 'settingsbtn-mapstyle-stamen-terrain':
                    # logger.info("Btn stamen terran yeeeeh")
                    btn_openstreetmap_active = False
                    btn_cartopositron_active = False
                    btn_darkmatter_active = False
                    btn_stamenterrain_active = True
                    btn_stamentoner_active = False
                    btn_stamenwatercolor_active = False
                    
            elif selection == 'settingsbtn-mapstyle-stamen-toner':
                    print("Btn stamen toner!")
                    btn_openstreetmap_active = False
                    btn_cartopositron_active = False
                    btn_darkmatter_active = False
                    btn_stamenterrain_active = False
                    btn_stamentoner_active = True
                    btn_stamenwatercolor_active = False
                    
            elif selection == 'settingsbtn-mapstyle-stamen-watercolor':
                    print("Btn dark hoe")
                    btn_openstreetmap_active = False
                    btn_cartopositron_active = False
                    btn_darkmatter_active = False
                    btn_stamenterrain_active = False
                    btn_stamentoner_active = False
                    btn_stamenwatercolor_active = True

            else:
                print("..")
        
        elif selection == "dbc-modal-settings":
            if settings_modal_open == True:
                if settings_json_store is None:            
                    btn_low_active = True
                    btn_med_active = False
                    btn_high_active = False             
                    
                elif int(settings_json_store) == 0:                
                    btn_low_active = True
                    btn_med_active = False
                    btn_high_active = False
                    
                elif int(settings_json_store) == 1:                
                    btn_low_active = False
                    btn_med_active = True
                    btn_high_active = False   
                    
                elif int(settings_json_store) == 2:                
                    btn_low_active = False
                    btn_med_active = False
                    btn_high_active = True
                    
                #MAPSTYLE
                if settings_mapstyle_store is None:
                    #no json store, so set to default
                    btn_openstreetmap_active = False
                    btn_cartopositron_active = True
                    btn_darkmatter_active = False
                    btn_stamenterrain_active = False
                    btn_stamentoner_active = False
                    btn_stamenwatercolor_active = False
                
                elif int(settings_mapstyle_store) == 0:
                    btn_openstreetmap_active = True
                    btn_cartopositron_active = False
                    btn_darkmatter_active = False
                    btn_stamenterrain_active = False
                    btn_stamentoner_active = False
                    btn_stamenwatercolor_active = False
                    
                elif int(settings_mapstyle_store) == 1:
                    btn_openstreetmap_active = False
                    btn_cartopositron_active = True
                    btn_darkmatter_active = False
                    btn_stamenterrain_active = False
                    btn_stamentoner_active = False
                    btn_stamenwatercolor_active = False
                
                elif int(settings_mapstyle_store) == 2:
                    btn_openstreetmap_active = False
                    btn_cartopositron_active = False
                    btn_darkmatter_active = True
                    btn_stamenterrain_active = False
                    btn_stamentoner_active = False
                    btn_stamenwatercolor_active = False    
                    
                elif int(settings_mapstyle_store) == 3:
                    btn_openstreetmap_active = False
                    btn_cartopositron_active = False
                    btn_darkmatter_active = False
                    btn_stamenterrain_active = True
                    btn_stamentoner_active = False
                    btn_stamenwatercolor_active = False
                    
                elif int(settings_mapstyle_store) == 4:
                    btn_openstreetmap_active = False
                    btn_cartopositron_active = False
                    btn_darkmatter_active = False
                    btn_stamenterrain_active = False
                    btn_stamentoner_active = True
                    btn_stamenwatercolor_active = False
                
                elif int(settings_mapstyle_store) == 5:
                    btn_openstreetmap_active = False
                    btn_cartopositron_active = False
                    btn_darkmatter_active = False
                    btn_stamenterrain_active = False
                    btn_stamentoner_active = False
                    btn_stamenwatercolor_active = True          
                if settings_colorbar_reverse_store is None:
                    btn_reverse_active = INIT_COLOR_PALETTE_REVERSE
                    btn_normal_active = not INIT_COLOR_PALETTE_REVERSE            
                if settings_colorbar_reverse_store is True:                
                    btn_reverse_active = True
                    btn_normal_active = False
                elif settings_colorbar_reverse_store is False:                
                    btn_reverse_active = False
                    btn_normal_active = True   
            else: 
                btn_low_active = True
                btn_med_active = False
                btn_high_active = False             
                btn_openstreetmap_active = True
                btn_cartopositron_active = False
                btn_darkmatter_active = False
                btn_stamenterrain_active = False
                btn_stamentoner_active = False
                btn_stamenwatercolor_active = False
                btn_reverse_active = INIT_COLOR_PALETTE_REVERSE
                btn_normal_active = not INIT_COLOR_PALETTE_REVERSE 
        
        else:
            print("Settings Callback: Input detected for colorpallete, setting active state for palette:",selection)
            
            #set all to false
            nc1a=False
            nc2a=False
            nc3a=False
            nc4a=False
            nc5a=False
            nc6a=False
            nc7a=False
            nc8a=False
            nc9a=False
            nc10a=False
            nc11a=False
            nc12a=False
            nc13a=False
            nc14a=False
            nc15a=False
            nc16a=False
            nc17a=False
            nc18a=False
            nc19a=False
            nc20a=False
            nc21a=False
            nc22a=False
            nc23a=False
            nc24a=False
            nc25a=False
            nc26a=False
            nc27a=False
            nc28a=False
            nc29a=False
            nc30a=False
            nc31a=False
            nc32a=False
            nc33a=False
            nc34a=False
            nc35a=False
            nc36a=False
            nc37a=False
            nc38a=False
            nc39a=False
            nc40a=False
            nc41a=False
            nc42a=False
            nc43a=False
            nc44a=False
            nc45a=False
            nc46a=False
            nc47a=False
            nc48a=False
            nc49a=False
            nc50a=False
            nc51a=False
            nc52a=False
            nc53a=False
            nc54a=False
            nc55a=False
            nc56a=False
            nc57a=False
            nc58a=False
            nc59a=False
            nc60a=False
            nc61a=False
            nc62a=False
            nc63a=False
            nc64a=False
            nc65a=False
            nc66a=False
            nc67a=False
            nc68a=False
            nc69a=False
            nc70a=False
            nc71a=False
            nc72a=False
            nc73a=False
            nc74a=False
            nc75a=False
            nc76a=False
            nc77a=False
            nc78a=False
            nc79a=False
            nc80a=False
            nc81a=False
            nc82a=False
            nc83a=False
            nc84a=False
            nc85a=False
            nc86a=False
            nc87a=False
            nc88a=False
            nc89a=False
            nc90a=False
            nc91a=False
            nc92a=False
            nc93a=False
            
            #conditional ifs 
            if selection == "auto":
                nc1a=True
            elif selection == "aggrnyl":
                nc2a=True
            elif selection == "agsunset":
                nc3a=True
            elif selection == "algae":
                nc4a=True
            elif selection == "amp":
                nc5a=True
            elif selection == "armyrose":
                nc6a=True
            elif selection == "balance":
                nc7a=True
            elif selection == "blackbody":
                nc8a=True
            elif selection == "bluered":
                nc9a=True
            elif selection == "blues":
                nc10a=True
            elif selection == "blugrn":
                nc11a=True
            elif selection == "bluyl":
                nc12a=True
            elif selection == "brbg":
                nc13a=True
            elif selection == "brwnyl":
                nc14a=True
            elif selection == "bugn":
                nc15a=True
            elif selection == "bupu":
                nc16a=True
            elif selection == "burg":
                nc17a=True
            elif selection == "burgyl":
                nc18a=True
            elif selection == "cividis":
                nc19a=True
            elif selection == "curl":
                nc20a=True
            elif selection == "darkmint":
                nc21a=True
            elif selection == "deep":
                nc22a=True
            elif selection == "delta":
                nc23a=True
            elif selection == "dense":
                nc24a=True
            elif selection == "earth":
                nc25a=True
            elif selection == "edge":
                nc26a=True
            elif selection == "electric":
                nc27a=True
            elif selection == "emrld":
                nc28a=True
            elif selection == "fall":
                nc29a=True
            elif selection == "geyser":
                nc30a=True
            elif selection == "gnbu":
                nc31a=True
            elif selection == "gray":
                nc32a=True
            elif selection == "greens":
                nc33a=True
            elif selection == "greys":
                nc34a=True
            elif selection == "haline":
                nc35a=True
            elif selection == "hot":
                nc36a=True
            elif selection == "hsv":
                nc37a=True
            elif selection == "ice":
                nc38a=True
            elif selection == "icefire":
                nc39a=True
            elif selection == "inferno":
                nc40a=True
            elif selection == "jet":
                nc41a=True
            elif selection == "magenta":
                nc42a=True
            elif selection == "magma":
                nc43a=True
            elif selection == "matter":
                nc44a=True
            elif selection == "mint":
                nc45a=True
            elif selection == "mrybm":
                nc46a=True
            elif selection == "mygbm":
                nc47a=True
            elif selection == "oranges":
                nc48a=True
            elif selection == "orrd":
                nc49a=True
            elif selection == "oryel":
                nc50a=True
            elif selection == "peach":
                nc51a=True
            elif selection == "phase":
                nc52a=True
            elif selection == "picnic":
                nc53a=True
            elif selection == "pinkyl":
                nc54a=True
            elif selection == "piyg":
                nc55a=True
            elif selection == "plasma":
                nc56a=True
            elif selection == "plotly3":
                nc57a=True
            elif selection == "portland":
                nc58a=True
            elif selection == "prgn":
                nc59a=True
            elif selection == "pubu":
                nc60a=True
            elif selection == "pubugn":
                nc61a=True
            elif selection == "puor":
                nc62a=True
            elif selection == "purd":
                nc63a=True
            elif selection == "purp":
                nc64a=True
            elif selection == "purples":
                nc65a=True
            elif selection == "purpor":
                nc66a=True
            elif selection == "rainbow":
                nc67a=True
            elif selection == "rdbu":
                nc68a=True
            elif selection == "rdgy":
                nc69a=True
            elif selection == "rdpu":
                nc70a=True
            elif selection == "rdylbu":
                nc71a=True
            elif selection == "rdylgn":
                nc72a=True
            elif selection == "redor":
                nc73a=True
            elif selection == "reds":
                nc74a=True
            elif selection == "solar":
                nc75a=True
            elif selection == "spectral":
                nc76a=True
            elif selection == "speed":
                nc77a=True
            elif selection == "sunset":
                nc78a=True
            elif selection == "sunsetdark":
                nc79a=True
            elif selection == "teal":
                nc80a=True
            elif selection == "tealgrn":
                nc81a=True
            elif selection == "tealrose":
                nc82a=True
            elif selection == "tempo":
                nc83a=True
            elif selection == "temps":
                nc84a=True
            elif selection == "thermal":
                nc85a=True
            elif selection == "tropic":
                nc86a=True
            elif selection == "turbid":
                nc87a=True
            elif selection == "twilight":
                nc88a=True
            elif selection == "viridis":
                nc89a=True
            elif selection == "ylgn":
                nc90a=True
            elif selection == "ylgnbu":
                nc91a=True
            elif selection == "ylorbr":
                nc92a=True
            elif selection == "ylorrd":
                nc93a=True     
            

        return btn_low_active, btn_med_active, btn_high_active, btn_openstreetmap_active, btn_cartopositron_active, btn_darkmatter_active, btn_stamenterrain_active, btn_stamentoner_active, btn_stamenwatercolor_active, \
            nc1a, nc2a, nc3a, nc4a, nc5a, nc6a, nc7a, nc8a, nc9a, nc10a, nc11a, nc12a, nc13a, nc14a, nc15a, nc16a, nc17a, nc18a, nc19a, nc20a, nc21a, nc22a, nc23a, nc24a, nc25a, nc26a, nc27a, nc28a, nc29a, nc30a, nc31a, nc32a, nc33a, nc34a, nc35a, nc36a, nc37a, nc38a, nc39a, nc40a, nc41a, nc42a, nc43a, nc44a, nc45a, nc46a, nc47a, nc48a, nc49a, nc50a, nc51a, nc52a, nc53a, nc54a, nc55a, nc56a, nc57a, nc58a, nc59a, nc60a, nc61a, nc62a, nc63a, nc64a, nc65a, nc66a, nc67a, nc68a, nc69a, nc70a, nc71a, nc72a, nc73a, nc74a, nc75a, nc76a, nc77a, nc78a, nc79a, nc80a, nc81a, nc82a, nc83a, nc84a, nc85a, nc86a, nc87a, nc88a, nc89a, nc90a, nc91a, nc92a, nc93a, \
                btn_reverse_active, btn_normal_active
    

    #COMPLETE STATE LIST FOR SETTINGS APPLY CALLBACK
    def callback_settings_modal_apply_create_states():
        
        c = []
        
        #first add other states required
        c.append(State('settingsbtn-resolution-low', "active")) 
        c.append(State('settingsbtn-resolution-med', "active"))
        c.append(State('settingsbtn-resolution-high', "active"))    
        c.append(State('settingsbtn-mapstyle-openstreetmap', "active"))
        c.append(State('settingsbtn-mapstyle-carto-positron', "active"))
        c.append(State('settingsbtn-mapstyle-darkmatter', "active"))
        c.append(State('settingsbtn-mapstyle-stamen-terrain', "active"))
        c.append(State('settingsbtn-mapstyle-stamen-toner', "active"))
        c.append(State('settingsbtn-mapstyle-stamen-watercolor', "active"))
        
        #now add colorscale states
        for i in geomap_colorscale:
            c.append(State(i,"active"))
        #print(c)
        
        #Add reverse button
        c.append(State('settingsbtn-reverse-colorscale', "active"))
        c.append(State('settingsbtn-normal-colorscale', "active"))
        
        return c


    #Settings modal apply button trigger 
    @dash_app.callback(                      
        [    
        Output('my-settings_json_store', 'data'),
        Output('my-settings_mapstyle_store', 'data'),
        Output("my-settings_colorbar_store", 'data'),
        Output('my-settings_colorbar_reverse_store', 'data'),
        ],
        Input("modal-settings-apply", "n_clicks"),
        
        callback_settings_modal_apply_create_states(),
        
        prevent_initial_call=True,
    )
    def callback_settings_modal_apply(n1,
                                    btn_low_active, btn_med_active, btn_high_active,
                                    btn_openstreetmap_active, btn_cartopositron_active, btn_darkmatter_active, btn_stamenterrain_active, btn_stamentoner_active, btn_stamenwatercolor_active,
                                    nc1a, nc2a, nc3a, nc4a, nc5a, nc6a, nc7a, nc8a, nc9a, nc10a, nc11a, nc12a, nc13a, nc14a, nc15a, nc16a, nc17a, nc18a, nc19a, nc20a, nc21a, nc22a, nc23a, nc24a, nc25a, nc26a, nc27a, nc28a, nc29a, nc30a, nc31a, nc32a, nc33a, nc34a, nc35a, nc36a, nc37a, nc38a, nc39a, nc40a, nc41a, nc42a, nc43a, nc44a, nc45a, nc46a, nc47a, nc48a, nc49a, nc50a, nc51a, nc52a, nc53a, nc54a, nc55a, nc56a, nc57a, nc58a, nc59a, nc60a, nc61a, nc62a, nc63a, nc64a, nc65a, nc66a, nc67a, nc68a, nc69a, nc70a, nc71a, nc72a, nc73a, nc74a, nc75a, nc76a, nc77a, nc78a, nc79a, nc80a, nc81a, nc82a, nc83a, nc84a, nc85a, nc86a, nc87a, nc88a, nc89a, nc90a, nc91a, nc92a, nc93a,
                                    btn_reverse_active, btn_normal_active
                                    ):

        dcc_settings_json = 0
        dcc_settings_mapstyle = INIT_MAP_STYLE
        dcc_settings_colorbar = INIT_COLOR_PALETTE      
        dcc_settings_colorbar_reverse = INIT_COLOR_PALETTE_REVERSE
        if btn_low_active == True:
            print("Setting dcc store setting json to LOW")
            dcc_settings_json = 0
        elif btn_med_active == True:
            print("Setting dcc store setting json to MED")
            dcc_settings_json = 1
        elif btn_high_active == True:
            print("Setting dcc store setting json to HIGH")
            dcc_settings_json = 2
            
        #logic for map style
        if btn_openstreetmap_active == True:
            print("Setting dcc store setting mapstyle to openstreet")
            dcc_settings_mapstyle = 0
        elif btn_cartopositron_active == True:
            print("Setting dcc store setting mapstyle to cartro")
            dcc_settings_mapstyle = 1
        elif btn_darkmatter_active == True:
            print("Setting dcc store setting mapstyle to darky")
            dcc_settings_mapstyle = 2
        elif btn_stamenterrain_active == True:
            print("Setting dcc store setting mapstyle to stamenterrain")
            dcc_settings_mapstyle = 3
        elif btn_stamentoner_active == True:
            print("Setting dcc store setting mapstyle to stamentoner")
            dcc_settings_mapstyle = 4
        elif btn_stamenwatercolor_active == True:
            print("Setting dcc store setting mapstyle to stamenwatercolour")
            dcc_settings_mapstyle = 5
    
        #logic for colorbar
        if nc1a==True: dcc_settings_colorbar = 0
        elif nc2a==True: dcc_settings_colorbar = 1 
        elif nc3a==True: dcc_settings_colorbar = 2
        elif nc4a==True: dcc_settings_colorbar = 3
        elif nc5a==True: dcc_settings_colorbar = 4
        elif nc6a==True: dcc_settings_colorbar = 5
        elif nc7a==True: dcc_settings_colorbar = 6
        elif nc8a==True: dcc_settings_colorbar = 7
        elif nc9a==True: dcc_settings_colorbar = 8
        elif nc10a==True: dcc_settings_colorbar = 9
        elif nc11a==True: dcc_settings_colorbar = 10
        elif nc12a==True: dcc_settings_colorbar = 11
        elif nc13a==True: dcc_settings_colorbar = 12
        elif nc14a==True: dcc_settings_colorbar = 13
        elif nc15a==True: dcc_settings_colorbar = 14
        elif nc16a==True: dcc_settings_colorbar = 15
        elif nc17a==True: dcc_settings_colorbar = 16
        elif nc18a==True: dcc_settings_colorbar = 17
        elif nc19a==True: dcc_settings_colorbar = 18
        elif nc20a==True: dcc_settings_colorbar = 19
        elif nc21a==True: dcc_settings_colorbar = 20
        elif nc22a==True: dcc_settings_colorbar = 21
        elif nc23a==True: dcc_settings_colorbar = 22
        elif nc24a==True: dcc_settings_colorbar = 23
        elif nc25a==True: dcc_settings_colorbar = 24
        elif nc26a==True: dcc_settings_colorbar = 25
        elif nc27a==True: dcc_settings_colorbar = 26
        elif nc28a==True: dcc_settings_colorbar = 27
        elif nc29a==True: dcc_settings_colorbar = 28
        elif nc30a==True: dcc_settings_colorbar = 29
        elif nc31a==True: dcc_settings_colorbar = 30
        elif nc32a==True: dcc_settings_colorbar = 31
        elif nc33a==True: dcc_settings_colorbar = 32
        elif nc34a==True: dcc_settings_colorbar = 33
        elif nc35a==True: dcc_settings_colorbar = 34
        elif nc36a==True: dcc_settings_colorbar = 35
        elif nc37a==True: dcc_settings_colorbar = 36
        elif nc38a==True: dcc_settings_colorbar = 37
        elif nc39a==True: dcc_settings_colorbar = 38
        elif nc40a==True: dcc_settings_colorbar = 39
        elif nc41a==True: dcc_settings_colorbar = 40
        elif nc42a==True: dcc_settings_colorbar = 41
        elif nc43a==True: dcc_settings_colorbar = 42
        elif nc44a==True: dcc_settings_colorbar = 43
        elif nc45a==True: dcc_settings_colorbar = 44
        elif nc46a==True: dcc_settings_colorbar = 45
        elif nc47a==True: dcc_settings_colorbar = 46
        elif nc48a==True: dcc_settings_colorbar = 47
        elif nc49a==True: dcc_settings_colorbar = 48
        elif nc50a==True: dcc_settings_colorbar = 49
        elif nc51a==True: dcc_settings_colorbar = 50
        elif nc52a==True: dcc_settings_colorbar = 51
        elif nc53a==True: dcc_settings_colorbar = 52
        elif nc54a==True: dcc_settings_colorbar = 53
        elif nc55a==True: dcc_settings_colorbar = 54
        elif nc56a==True: dcc_settings_colorbar = 55
        elif nc57a==True: dcc_settings_colorbar = 56
        elif nc58a==True: dcc_settings_colorbar = 57
        elif nc59a==True: dcc_settings_colorbar = 58
        elif nc60a==True: dcc_settings_colorbar = 59
        elif nc61a==True: dcc_settings_colorbar = 60
        elif nc62a==True: dcc_settings_colorbar = 61
        elif nc63a==True: dcc_settings_colorbar = 62
        elif nc64a==True: dcc_settings_colorbar = 63
        elif nc65a==True: dcc_settings_colorbar = 64
        elif nc66a==True: dcc_settings_colorbar = 65
        elif nc67a==True: dcc_settings_colorbar = 66
        elif nc68a==True: dcc_settings_colorbar = 67
        elif nc69a==True: dcc_settings_colorbar = 68
        elif nc70a==True: dcc_settings_colorbar = 69
        elif nc71a==True: dcc_settings_colorbar = 70
        elif nc72a==True: dcc_settings_colorbar = 71
        elif nc73a==True: dcc_settings_colorbar = 72
        elif nc74a==True: dcc_settings_colorbar = 73
        elif nc75a==True: dcc_settings_colorbar = 74
        elif nc76a==True: dcc_settings_colorbar = 75
        elif nc77a==True: dcc_settings_colorbar = 76
        elif nc78a==True: dcc_settings_colorbar = 77
        elif nc79a==True: dcc_settings_colorbar = 78
        elif nc80a==True: dcc_settings_colorbar = 79
        elif nc81a==True: dcc_settings_colorbar = 80
        elif nc82a==True: dcc_settings_colorbar = 81
        elif nc83a==True: dcc_settings_colorbar = 82
        elif nc84a==True: dcc_settings_colorbar = 83
        elif nc85a==True: dcc_settings_colorbar = 84
        elif nc86a==True: dcc_settings_colorbar = 85
        elif nc87a==True: dcc_settings_colorbar = 86
        elif nc88a==True: dcc_settings_colorbar = 87
        elif nc89a==True: dcc_settings_colorbar = 88
        elif nc90a==True: dcc_settings_colorbar = 89
        elif nc91a==True: dcc_settings_colorbar = 90
        elif nc92a==True: dcc_settings_colorbar = 91
        elif nc93a==True: dcc_settings_colorbar = 92   
        
        #logic for reverse button group
        if btn_reverse_active==True: dcc_settings_colorbar_reverse = True
        elif btn_normal_active==True: dcc_settings_colorbar_reverse = False
        
        return dcc_settings_json, dcc_settings_mapstyle, dcc_settings_colorbar, dcc_settings_colorbar_reverse


    @dash_app.callback(                      
        Output("timeslider-hidden-div", "children"),    
        Input("year-slider", "value"),    
        prevent_initial_call=True,
    )
    def callback_year_slider_change(year_index):
        return "dummy"


    #Bar graph modal
    @dash_app.callback(
        [
        Output("dbc-modal-bar", "is_open"),
        Output('bar-graph', 'figure'),
        Output("bar-graph-modal-title", "children"),
        Output("bar-graph-modal-footer", "children"),
        Output("bar-graph-modal-footer-link", "href"),
        Output('my-loader-bar', "children"), #used to trigger loader. Use null string "" as output
        Output('bar-graph-dropdown-countrieselector', 'options'),
        Output('bar-graph-dropdown-dataset', 'options'), 
        Output('bar-graph-dropdown-year', 'options'),
        Output('my-series-bar','data'),
        Output('my-year-bar','data'),     
        Output("my-url-bar-callback","data"),
        Output('my-loader-bar-refresh','children'),
        ],
        [
        Input("my-url-bar-trigger", "data"), 
        Input("bar-button", "n_clicks"), 
        Input("modal-bar-close", "n_clicks"),
        Input("bar-graph-dropdown-countrieselector", "value"),
        Input("bar-graph-dropdown-dataset", "value"),
        Input('bar-graph-dropdown-year','value'),     
        ],
        [
        State("dbc-modal-bar", "is_open"),
        State("my-series", "data"), 
        State("year-slider", "value"),  
        State("year-slider", "marks"),     
        State('bar-graph-dropdown-year','options'),
        State('url','href'),
        State("my-url-view", 'data'),       
        State("my-url-series", 'data'),
        State("my-url-year", 'data'),
        ],
        prevent_initial_call=True
    )

    def callback_toggle_modal_bar(bar_trigger, n1, n2, dropdown_countrieselector, dropdown_dataset, dropdown_year, is_open, series, yearid, yeardict, dropdown_year_list, href, url_view, url_series, url_year):

        ctx = dash.callback_context 
        trigger = ctx.triggered[0]["prop_id"].split(".")[0] 
        if trigger == 'modal-bar-close': return not is_open, {}, None,None,None,None,[],[],[], None, None, None, None   
        
        if trigger == 'my-url-bar-trigger':
            if url_view == '' or url_view == None or bar_trigger != 'bar': 
                raise PreventUpdate()
            else:
                series = api_dict_label_to_raw[url_series]
                year = url_year                   
                series_label = dataset_lookup.loc[dataset_lookup['dataset_raw'] == series].iloc[0,2]  
                source = d.get_source(dataset_lookup, series)
                link = dataset_lookup.loc[dataset_lookup['dataset_raw'] == series].iloc[0,4]
                bar_graph_title = series_label+" in "+year  
                df = d.get_series_and_year(pop, year, series, False)           
        elif trigger == 'bar-button':
            year = str(d.get_years(pop.loc[(pop['Series'] == series)])[yearid])            
            series_label = dataset_lookup.loc[dataset_lookup['dataset_raw'] == series].iloc[0,2]  
            source = d.get_source(dataset_lookup, series)
            link = dataset_lookup.loc[dataset_lookup['dataset_raw'] == series].iloc[0,4]
            bar_graph_title = series_label+" in "+year  
            df = d.get_series_and_year(pop, year, series, False)  
        elif trigger == 'bar-graph-dropdown-dataset':     
            if dropdown_dataset != None: 
                series = dropdown_dataset        
            
            series_label = dataset_lookup.loc[dataset_lookup['dataset_raw'] == series].iloc[0,2] 
            source = d.get_source(dataset_lookup, series)
            link = dataset_lookup.loc[dataset_lookup['dataset_raw'] == series].iloc[0,4]
            df = d.get_series(pop, series, False)
            df['Value'] = df['Value'].astype(float)
            year = np.max(pd.unique(df["Year"]))
            if dropdown_year != None and dropdown_year != "":
                availyrs = np.sort(pd.unique(df["Year"]))           
                if str(dropdown_year) in availyrs:
                    year = str(dropdown_year)     
            df = df[(df["Year"] == year)].sort_values(by="Value", ascending=False)   
            bar_graph_title = series_label+" in "+str(year) 
        elif trigger == 'bar-graph-dropdown-countrieselector': 
            if dropdown_dataset == None or dropdown_dataset == '': 
                if dropdown_year == None or dropdown_year == '':
                    year = d.get_years(pop.loc[(pop['Series'] == series)])[yearid]
                else:
                    year = dropdown_year
                series_label = dataset_lookup.loc[dataset_lookup['dataset_raw'] == series].iloc[0,2] 
                source = d.get_source(dataset_lookup, series)
                link = dataset_lookup.loc[dataset_lookup['dataset_raw'] == series].iloc[0,4]
                bar_graph_title = series_label+" in "+str(year)
            else:
                series = dropdown_dataset            
                series_label = dataset_lookup.loc[dataset_lookup['dataset_raw'] == series].iloc[0,2]                
                source = d.get_source(dataset_lookup, series)
                link = dataset_lookup.loc[dataset_lookup['dataset_raw'] == series].iloc[0,4]    
                df = d.get_series(pop, series, False)          
                if dropdown_year == None or dropdown_year == '':
                    year = np.max(pd.unique(df["Year"]))
                else:
                    year = dropdown_year               
                bar_graph_title = series_label+" in "+str(year)     
            df = d.get_series_and_year(pop, str(year), series, False)               
            
        elif trigger == 'bar-graph-dropdown-year':          
            if dropdown_dataset != None and dropdown_dataset != '':
                series = dropdown_dataset
            if dropdown_year == None:
                years = np.sort(pd.unique(pd.DataFrame(pop[(pop['Series']==series)], columns=['Year'])['Year'].astype(int)))
                year = str(years[-1])
            else:
                year = str(dropdown_year)                     
            series_label = dataset_lookup.loc[dataset_lookup['dataset_raw'] == series].iloc[0,2]   

            source = d.get_source(dataset_lookup, series)
            link = dataset_lookup.loc[dataset_lookup['dataset_raw'] == series].iloc[0,4]
            bar_graph_title = series_label+" in "+year        
            df = d.get_series_and_year(pop, year, series, False)     
        dd = dataset_lookup[(dataset_lookup['var_type']!='discrete')].sort_values(by="dataset_label").drop_duplicates(subset=['dataset_raw'])   
        dropdown_ds=[]
        for i in range(0,len(dd)):        
            dropdown_ds.append({'label': dd.iloc[i][2], 'value': dd.iloc[i][1]})
        dd = np.sort(pd.unique(df["Country"])) 
        dropdown_countries=[]
        for i in range(0,len(dd)):
            dropdown_countries.append({'label': dd[i], 'value': dd[i]})     
        dropdown_years=[]
        years = np.sort(pd.unique(pd.DataFrame(pop[(pop['Series']==series)], columns=['Year'])['Year'].astype(int)))    
        for i in range(0,len(years)):
                dropdown_years.append({'label': years[i], 'value': years[i]})   
        blah = href.split('/') 
        root = blah[0]+'//'+blah[2]+'/'
        url_bar = root + api_dict_raw_to_label[series] + '/' + str(year) + '/bar'
        
        if trigger == 'bar-graph-dropdown-dataset' or trigger == 'bar-graph-dropdown-countrieselector' or trigger == 'bar-graph-dropdown-year': is_open = not is_open
        
        return not is_open, create_chart_bar(df, series, dropdown_countrieselector), bar_graph_title, source, link, "", dropdown_countries, dropdown_ds, dropdown_years, series, year, url_bar, ''
    


    #Line graph modal
    @dash_app.callback(
        [
        Output("dbc-modal-line", "is_open"),
        Output('line-graph', 'figure'),
        Output("line-graph-modal-title", "children"),
        Output("line-graph-modal-footer", "children"),
        Output("line-graph-modal-footer-link", "href"),
        Output('my-loader-line', "children"), #used to trigger loader. Use null string "" as output
        Output('line-graph-dropdown-countries', 'options'),
        Output('line-graph-dropdown-dataset', 'options'),
        Output('my-series-line', 'data'),
        Output("my-url-line-callback","data"),
        Output('my-loader-line-refresh','children'),     
        ],
        [
        Input("my-url-line-trigger", "data"), 
        Input("line-button", "n_clicks"), 
        Input("modal-line-close", "n_clicks"),
        Input("line-graph-dropdown-countries", "value"),
        Input('line-graph-dropdown-dataset', 'value'),
        ],
        [
        State("dbc-modal-line", "is_open"),
        State("my-series", "data"), #super useful. Use state of selections as global vars via state.
        State("year-slider", "value"),  
        State("year-slider", "marks"),
        State("my-url-series", 'data'),
        State('url','href'),  
        State("my-url-view", 'data'),
        State("my-url-year", 'data'),
                    
        ],
        prevent_initial_call=True
    )
    def callback_toggle_modal_line(line_trigger, n1, n2, dd_country_choices, dd_dataset_choice, is_open, series, yearid, yeardict, url_series, href, url_view, url_year):
        ctx = dash.callback_context 
        trigger = ctx.triggered[0]["prop_id"].split(".")[0] 
        if trigger == 'modal-line-close': return not is_open, {}, None,None,None,None, [],[], None,None,None
        if trigger == 'my-url-line-trigger':     
            if url_view == '' or line_trigger != 'line': 
                raise PreventUpdate()
            else: series=api_dict_label_to_raw[url_series]
        elif dd_dataset_choice!='' and dd_dataset_choice!=None: series = dd_dataset_choice      
        series_label = dataset_lookup.loc[dataset_lookup['dataset_raw'] == series].iloc[0,2]    
        source = d.get_source(dataset_lookup, series)
        link = dataset_lookup.loc[dataset_lookup['dataset_raw'] == series].iloc[0,4] 
        graph_title = series_label
        df = pop[(pop["Series"] == series)].sort_values(by="Country", ascending=True)
        df["Value"] = df["Value"].astype(float)
        df["Year"] = df["Year"].astype(int)
        ddc = np.sort(pd.unique(df["Country"]))
        dd_country_list=[]    
        for i in range(0,len(ddc)):
            dd_country_list.append({'label': ddc[i], 'value': ddc[i]})     
        ddd = dataset_lookup[(dataset_lookup['var_type']!='discrete')].sort_values(by="dataset_label").drop_duplicates(subset=['dataset_raw'])     
        dd_dataset_list=[]   
        for i in range(0,len(ddd)):        
            dd_dataset_list.append({'label': ddd.iloc[i][2], 'value': ddd.iloc[i][1]})    
        blah = href.split('/') 
        root = blah[0]+'//'+blah[2]+'/'
        url = root + api_dict_raw_to_label[series] + '/' + 'x/line'          

        if trigger == 'line-graph-dropdown-countries' or trigger == 'line-graph-dropdown-dataset': is_open = not is_open
        
        return not is_open, create_chart_line(df, series, dd_country_choices), graph_title, source, link, "", dd_country_list, dd_dataset_list, series, url, ''  

    #Globe view modal callback
    @dash_app.callback([
        Output("dbc-modal-globe", "is_open"),
        Output("globe-body","children"),
        Output('my-loader-globe', "children"), #used to trigger loader. Use null string "" as output  
        Output("globe-modal-title", "children"),
        Output('globe-modal-footer', 'children'),
        Output('globe-modal-footer-link', 'children'),
        Output('my-loader-globe-refresh','children'),
        Output("my-url-globe-callback","data"),
        ],
        [
        Input("my-url-globe-trigger", "data"), 
        Input("globe-button", "n_clicks"), 
        Input("modal-globe-close", "n_clicks"),
        Input("modal-globe-jelly", "n_clicks"),
        Input("modal-globe-ne50m", "n_clicks"),
        ],
        [
        State("dbc-modal-globe", "is_open"),
        State("my-series", "data"), 
        State("year-slider", "value"),  
        State("year-slider", "marks"),
        State('my-settings_json_store', 'data'),
        State("geomap_figure", "figure"),
        State("my-settings_colorbar_reverse_store", 'data'),
        State("my-url-series", 'data'),
        State('url','href'),  
        State("my-url-view", 'data'),
        State("my-url-year", 'data'),
        ], 
        prevent_initial_call=True,
    )
    def callback_toggle_modal_globe(globe_trigger, n1, n2, n3, n4, is_open, series, yearid, yeardict, settings_json, map_data, colorbar_reverse, url_series, href, url_view, url_year):
        
        ctx = dash.callback_context 
        trigger = ctx.triggered[0]["prop_id"].split(".")[0]
        if trigger == 'modal-globe-close': return not is_open, {}, None,None,None,None,None,None
        
        if trigger == 'my-url-globe-trigger':
            if globe_trigger != 'globe':
                raise PreventUpdate()
            else:
                year = url_year
                series = api_dict_label_to_raw[url_series]            
                
        else: year = str(d.get_years(pop.loc[(pop['Series'] == series)])[yearid])
        
        # set variables
        series_label = dataset_lookup.loc[dataset_lookup['dataset_raw'] == series].iloc[0,2]  
        source = d.get_source(dataset_lookup, series)
        link = dataset_lookup.loc[dataset_lookup['dataset_raw'] == series].iloc[0,4] 
        var_type = dataset_lookup.loc[dataset_lookup['dataset_raw'] == series].iloc[0,5]  
        title = series_label+" ["+str(year)+"]"  
        jellybean = False
        high_res = False    
        
        try:
            continuous_colorscale = map_data['data'][0]['colorscale'] #a list of colours e.g. [1.1111, #hexcolour] (does not reverse)
        except KeyError as error:
            print("Breaking out of globe callback. Map not ready")
            raise PreventUpdate()
        
        if colorbar_reverse == None: colorbar_reverse = INIT_COLOR_PALETTE_REVERSE
            
        if colorbar_reverse == False:
            csr = copy.deepcopy(continuous_colorscale)        
            csr = csr[::-1]      
            for i in range(0,len(csr)): continuous_colorscale[i][1] = csr[i][1]  
        
        if trigger == 'modal-globe-jelly':  jellybean = True        
        if trigger == 'modal-globe-ne50m':  high_res = True
                    
        blah = href.split('/') 
        root = blah[0]+'//'+blah[2]+'/'
        url = root + api_dict_raw_to_label[series] + '/'+str(year)+'/globe'
                
        df = pop[(pop["Year"] == int(year)) & (pop["Series"] == series)].copy()  

        gj_land = d.update_3d_geo_data_JSON(df, geojson_globe_land_ne110m, continuous_colorscale, jellybean, var_type, discrete_colorscale) 
        gj_ocean = d.update_3d_geo_data_JSON(df, geojson_globe_ocean_ne110m, continuous_colorscale, jellybean, var_type, discrete_colorscale)

        globe = create_chart_globe(gj_land, gj_ocean) 
        
        if trigger == 'modal-globe-jelly' or trigger == 'modal-globe-ne50m': is_open = not is_open
                
        return not is_open, globe, "", title, source, link, "", url
        



    @dash_app.callback(
        [
        Output("dbc-modal-geobar", "is_open"),
        Output("geobar-test","children"),
        Output("geobar-modal-title", "children"),
        Output('my-loader-geobar', "children"), #used to trigger loader. Use null string "" as output
        Output('geobar-modal-footer', 'children'),        
        Output('geobar-modal-footer-link', 'children'),    
        Output("my-url-jigsaw-callback","data"),
        Output('my-loader-geobar-refresh','children'),
        ],
        [
        Input("my-url-jigsaw-trigger", "data"), 
        Input("geobar-button", "n_clicks"), 
        Input("modal-geobar-close", "n_clicks"),
        Input("modal-geobar-jelly", "n_clicks"),    
        ],
        [
        State("dbc-modal-geobar", "is_open"),
        State("my-series", "data"),
        State("year-slider", "value"),  
        State("year-slider", "marks"),
        State('my-settings_json_store', 'data'),
        State("geomap_figure", "figure"),
        State("my-settings_colorbar_reverse_store", 'data'),
        State('url','href'),  
        State("my-url-series", 'data'),
        State("my-url-view", 'data'),
        State("my-url-year", 'data'),        
        ], 
        prevent_initial_call=True,
    )
    def callback_toggle_modal_jigsaw(jigsaw_trigger, n1, n2, n3, is_open, series, yearid, yeardict, settings_json, map_data, colorbar_reverse,href, url_series, url_view, url_year):
        
        ctx = dash.callback_context 
        trigger = ctx.triggered[0]["prop_id"].split(".")[0]
        
        if trigger == 'modal-geobar-close': return not is_open, {}, None,None,None,None,None,None
    
        
        if trigger == 'my-url-jigsaw-trigger':
            if jigsaw_trigger != 'jigsaw':
                raise PreventUpdate()
            else:
                year = url_year
                series = api_dict_label_to_raw[url_series]  
        
        else: year = str(d.get_years(pop.loc[(pop['Series'] == series)])[yearid])
        
        series_label = dataset_lookup.loc[dataset_lookup['dataset_raw'] == series].iloc[0,2]  
        source = d.get_source(dataset_lookup, series)
        link = dataset_lookup.loc[dataset_lookup['dataset_raw'] == series].iloc[0,4] 
        title = series_label+" ["+str(year)+"]"    
        jellybean = False         
            
        colorscale = map_data['data'][0]['colorscale'] 

        if colorbar_reverse == None:  colorbar_reverse = INIT_COLOR_PALETTE_REVERSE        
        
        if colorbar_reverse == False:
            csr = copy.deepcopy(colorscale)        
            csr = csr[::-1]      
            for i in range(0,len(csr)):
                colorscale[i][1] = csr[i][1] 
        gj = copy.deepcopy(geojson_LOWRES)
            
        if trigger == 'modal-geobar-jelly': jellybean = True           
        
        # build url    
        blah = href.split('/') 
        root = blah[0]+'//'+blah[2]+'/'
        url = root + api_dict_raw_to_label[series] + '/'+str(year)+'/jigsaw'        

        # build figure  
        geobar = create_chart_geobar(series, year, colorscale, gj, jellybean)        
        
        # keep modal open in these conditions
        if trigger == 'modal-geobar-jelly': is_open = not is_open 
            
        return not is_open, geobar, title, "", source, link, url,'' 
        
    @dash_app.callback(
        Output("nav-search-menu", 'value'),
        Input("my-series",'data'),
        #State(),
        prevent_initial_call=True
        )
    def callback_clear_search_menu_helper(data):        
        return "hi"

    @dash_app.callback(
        [Output('bar-graph-dropdown-dataset', 'value'),
        Output('bar-graph-dropdown-year', 'value'),
        ],
        [Input("bar-button", "n_clicks"),
        Input("bar-graph-dropdown-dataset", "options"),     
        ],
        [State('bar-graph-dropdown-dataset', 'value'),
        State('bar-graph-dropdown-year', 'value'),
        ],
        prevent_initial_call=True
    )
    def callback_toggle_modal_bar_clear_dropdown_helper(n, options, val, valyr):

        ctx = dash.callback_context 
        trigger = ctx.triggered[0]["prop_id"].split(".")[0]
        if trigger == 'bar-button':
            return "",""
        
        else:
            if val == None:
                return "",""
            else:
                return val, valyr 

    @dash_app.callback(
        [Output('line-graph-dropdown-dataset', 'value'), ],
        [Input("line-button", "n_clicks"), ],
        [State('line-graph-dropdown-dataset', 'value'), ],
        prevent_initial_call=True
    )
    def callback_toggle_modal_line_clear_dropdown_helper(n,val):
        return [""]


    @dash_app.callback(
        [
        Output("line-graph-dropdown-countries", "value"), 
        #Output('line-graph','style'),
        ],
        [    
        Input("linegraph-allcountries-button", "n_clicks"), 
        Input("linegraph-nocountries-button", "n_clicks"),  
        ],
        [     
        State('line-graph-dropdown-countries', 'options'),           
        ],
        prevent_initial_call=True
    )
    def callback_toggle_modal_line_allcountries_helper(n1,n2, countries_options):
        ctx = dash.callback_context 
        trigger = ctx.triggered[0]["prop_id"].split(".")[0] 
        
        if trigger == 'linegraph-allcountries-button':
            style={"backgroundColor": "#1a2d46", 'color': '#ffffff', 'height': 1000}
            countries=[]
            for i in range(0,len(countries_options)):
                countries.append(countries_options[i]['label'])            
            return [countries] #, style
        
        elif trigger == 'linegraph-nocountries-button':
            style={"backgroundColor": "#1a2d46", 'color': '#ffffff', 'height': INIT_BAR_H}
            return [''] #, style
