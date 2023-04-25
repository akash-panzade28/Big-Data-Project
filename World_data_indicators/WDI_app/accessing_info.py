import json
import pandas as pd
import numpy as np
import matplotlib as mpl #colour
import copy
import time
from PIL import ImageColor
import glob
import os
import sys


def create_api_lookup_dicts(dataset_lookup):
    
    #subset dataset lookup
    df = dataset_lookup[['dataset_raw', 'dataset_label', 'dataset_label']].copy()
    df.columns=['dataset_raw', 'dataset_label', 'api_label']
    
    #drop duplicate rows
    df = df.drop_duplicates()
    
    # make api labels URL path friendly
    df['api_label'] = df.api_label.str.replace(' ','-')
    df['api_label'] = df.api_label.str.replace('%','percent')
    df['api_label'] = df.api_label.str.replace('?','-')
    df['api_label'] = df.api_label.str.replace('+','-')
    df['api_label'] = df.api_label.str.replace(',','-')
    
    # declare new global dicts
    api_dict_raw_to_label={}
    api_dict_label_to_raw={}
    
    # build lookup dictionaries by iterating the DF (ineffecient but will do for now)
    for index,row in df.iterrows():
        api_dict_raw_to_label[row['dataset_raw']]=row['api_label']
        api_dict_label_to_raw[row['api_label']]=row['dataset_raw']
        
    return api_dict_raw_to_label, api_dict_label_to_raw

def import_master_dataset(country_lookup, FAST_LOAD, LOAD_RAW):
    tic = time.perf_counter()
    path = os.getcwd()+"/Datasets/Final_Processed_Data.parquet" 
    pop = pd.read_parquet(path)
    toc = time.perf_counter()
    return pop

def get_regions(countries,gj):
    
    #this is a helper function where I extracted the regions from the json data, and exported it to csv to replace m49 starter file.    
    #create cols
    countries['continent'] = "No continent"
    countries['region_un'] = "No region"
    countries['region_wb'] = "No subregion"
    
    for i in range(0, len(gj['features'])):
        try:
                        
            continent = gj['features'][i]['properties']['continent']
            region_un = gj['features'][i]['properties']['region_un']
            region_wb = gj['features'][i]['properties']['region_wb']
            m49_json = gj['features'][i]['properties']['un_a3']
            
            #set deets
            countries.loc[countries.m49_a3_country == m49_json, 'continent'] = continent
            countries.loc[countries.m49_a3_country == m49_json, 'region_un'] = region_un
            countries.loc[countries.m49_a3_country == m49_json, 'region_wb'] = region_wb
            
            #print(continent)
            #print(region_un)
            #print(region_wb)      
        
        except IndexError as error:
            print("add_regions: Exception thrown attempting to build custom dict from json (expected)")
    
    #print(countries)
    #countries.to_csv(r'C:\Users\Dan\Documents\GitHub\atlas\data\experimental\countries.csv', index = False)    
           
    return

def create_unique_country_list(path):
    
    #read in m49 codes from csv
    c =  pd.read_csv(
       path,
       encoding="utf-8",
       names=["m49_a3_country", "country", "continent", "region_un", "region_wb", "su_a3"],
    )
    
    #cast to string
    c["m49_a3_country"] = c["m49_a3_country"].astype(str) 
    
    #padd the 3 digit m49 country integer with zeros if it less than 100 (i.e. "3" will become "003")
    c['m49_a3_country'] = c['m49_a3_country'].str.zfill(3)  
    
    # delete first row (column headings)
    c = c.iloc[1:,]
    
    return c

def create_dataset_lookup(path):
    
    #read in lookup table of raw datasets and their labels
    d= pd.read_csv(
       path,
       encoding="utf-8",
       names=["dataset_id", "dataset_raw", "dataset_label", "source", "link", "var_type", "nav_cat", "colour", "nav_cat_nest", "tag1", "tag2", "explanatory_note"],
    )
    
    # delete first 1 rows (col headers)
    d = d.iloc[1:,] 
    
    #d['explanatory_note'] = d['explanatory_note'].fillna('')
    
    
        
    return d

def get_source(ds_lookup, series):    
    
    source = ds_lookup[ds_lookup['dataset_raw']==series].iloc[0]['source']
       
    return source
  
def get_link(ds_lookup, series):    
    
    link = ds_lookup[ds_lookup['dataset_raw']==series].iloc[0]['link']
       
    return link
        
def check_year(pop, series, year):
           
    # get unique years from series
    df = pop.loc[(pop['Series'] == series)]
    
    # convert to list
    years = pd.DataFrame(pd.unique(df["Year"]), columns=["value"])['value'].tolist()
           
    # return bool if year found
    return int(year) in years
    
def get_years(df):
    # strip out years from dataset and return as dictionary (for control input)
    df = df.sort_values('Year')
    years = pd.DataFrame(pd.unique(df["Year"]), columns=["value"])
    years = years["value"].to_dict()
    #print(years)
    return years

def get_year_slider_index(pop, series, year):
    
    #obtain relevant years for this series
    yr_slider = get_years(pop.loc[(pop['Series'] == series)])
        
    if len(yr_slider) > 0:
        for index in range(len(yr_slider)):  
            if yr_slider[index] == year: return index
            
    #otherwise return most recent    
    return len(yr_slider)-1

def get_year_slider_marks(series, pop, INIT_YEAR_SLIDER_FONTSIZE, INIT_YEAR_SLIDER_FONTCOLOR, year_slider_selected):    
    
    #obtain relevant years for this series and update slider
    year_slider_marks = get_years(pop.loc[(pop['Series'] == series)])
    
    # add styling to year slider        
    year_slider_marks2 = {
                    i: {
                        "label": year_slider_marks[i],
                        "style": {"fontSize": INIT_YEAR_SLIDER_FONTSIZE, 'color':INIT_YEAR_SLIDER_FONTCOLOR, 'fontWeight': 'normal'},
                    }
                    for i in range(0, len(year_slider_marks))
                }   
    
    year_slider_marks=year_slider_marks2     
     
    # shorten year labels if needed
    
    #10-20 = '91 style
    #if len(year_slider_marks) > 10 and len(year_slider_marks) <= 20:
    #    for i in range(0,len(year_slider_marks)):
    #        year_slider_marks[i]['label'] = "'"+str(year_slider_marks[i]['label'])[2:]
    #        #year_slider_marks[i]['style']['fontSize']=12
    
    
    #10-20 = '91 style
    if len(year_slider_marks) > 10 and len(year_slider_marks) <= 20:
        counter = 0
        for i in range(0,len(year_slider_marks)):   
            if i == 0 or i == len(year_slider_marks)-1:              
                continue    
            if counter != 1:
                year_slider_marks[i]['label'] = ""               
                counter = counter + 1
            else:                
                counter = 0
    
    
    
    #20-50 = every 5 yrs
    elif len(year_slider_marks) > 20 and len(year_slider_marks) <= 50:                    
        counter = 0
        for i in range(0,len(year_slider_marks)):   
            if i == 0 or i == len(year_slider_marks)-1:              
                continue    
            if counter != 4:
                year_slider_marks[i]['label'] = ""               
                counter = counter + 1
            else:                
                counter = 0
                
    #50-100 = every 10 yrs
    elif len(year_slider_marks) > 50 and len(year_slider_marks) <= 100:                      
        counter = 0
        for i in range(0,len(year_slider_marks)):  
            if i == 0 or i == len(year_slider_marks)-1:              
                continue   
            if counter != 9:
                year_slider_marks[i]['label'] = ""               
                counter = counter + 1
            else:                
                counter = 0
                
    #100-200 = every 20 yrs
    elif len(year_slider_marks) > 100 and len(year_slider_marks) <= 200:                      
        counter = 0
        for i in range(0,len(year_slider_marks)): 
            if i == 0 or i == len(year_slider_marks)-1:              
                continue 
            if counter != 19:
                year_slider_marks[i]['label'] = ""               
                counter = counter + 1
            else:                
                counter = 0
    
    #200+ = every 50 yrs
    elif len(year_slider_marks) > 200:                      
        counter = 0
        for i in range(0,len(year_slider_marks)):  
            if i == 0 or i == len(year_slider_marks)-1:              
                continue   
            if counter != 49:
                year_slider_marks[i]['label'] = ""               
                counter = counter + 1
            else:                
                counter = 0
    
    
    
    return year_slider_marks

def get_series_and_year(df, year, series, ascending):
    #print("Get series. Year %r, series %r, ascending %r", year, series, ascending)
    
    #Subset main dataframe for this series and year as a shallow copy (so we can cast value to Float)
    d = copy.copy(df[(df["Year"] == int(year)) & (df["Series"] == series)]) #This could be a memory leak, or at least seems inefficient.
    
    d['Value'] = d['Value'].astype(float) 
    
    # dropping ALL duplicate values (THIS SHOULDNT BE NEEDED BUT SOME DATASETS MAY BE A LITTLE CORRUPTED. E.g 'Annual mean levels of fine particulate matter in cities, urban population (micrograms per cubic meter)'
    d = d.drop_duplicates(subset ="m49_un_a3")

    d = d.sort_values('Value', ascending=ascending)
    return d

def get_series(df, series, ascending):
    #print("Get series. Series %r, ascending %r", series, ascending)
    d = copy.copy(df[(df["Series"] == series)])
    d['Year'] = d['Year'].astype(int)
    d['Value'] = d['Value'].astype(float)
    d = d.sort_values('Value', ascending=ascending)
    return d

def load_geo_data_JSON(json_path):    
    '''
    #logger.info("Load geo data method called, attempting to load new polygon dataset")
    with open(json_path, "r") as read_file:
        countries_json = json.load(read_file)'''
    
    #with open(json_path, encoding='utf-8') as read_file:
    #    countries_json = json.load(read_file)
    
    countries_json = json.load(open(json_path, 'r', encoding='utf-8'))
    
    return countries_json

def load_3d_geo_data_JSON_cleaned(json_path):    
    #load data    
    gj = json.load(open(json_path, 'r', encoding='utf-8'))
    return gj

def update_3d_geo_data_JSON(df, geojson, colorscale, jellybean, var_type, discrete_colorscale):
    #update a copy of the geojson data to include series specific data from the passed in dataframe (subset) including label names, and colours
        
    #FIRST DO THE COLOUR INTERPOLATION
    
    #fix for removing note and source columns
    df['fix1'] = "dummmy"
    df['fix2'] = "dummy"
    
    #For continuous data we'll do linear color interpolation based on the extracted colorscale from the main map
    if var_type == "continuous" or var_type == "ratio" or var_type == "quantitative":
    
        #cast values to float
        df['Value'] = df['Value'].astype(float)  
        
        #drop values below zero (they cannot be displayed on current choropleth style)
        df = df[df.Value > 0]  
        
        #transform the data values to log10 (zeros introduced where log not computed)
        df['value_log10'] = np.log10(df['Value'], out=np.zeros_like(df['Value']), where=(df['Value']!=0))        
        
        #now drop any rows with zero vals (or it will be affected by subsequent colour interpolation logic)
        df = df[df.value_log10 != 0]       
        
        #translate data range to positive
        mn = np.min(df["value_log10"])
        mx = np.max(df["value_log10"])
        if mn < 0.0:            
            #print("Color correction, translating log vals")
            df['value_log10'] = df['value_log10'] + abs(mn)
        
        #now calculate the 0-1 ratio (normalise)
        df['f-log'] = df['value_log10'] / np.max(df["value_log10"]) #i.e. what proportion is it of the max   
        
        #get colorscale array from mapdata (this is variable length and can switch to RGB from Hex)
        #colorscale = map_data['data'][0]['colorscale'] #an list of colours e.g. [1.1111, #hexcolour]   
        
        if colorscale[0][1][0] != "#":
            #i.e. we have an RGB color array (happens after settings are changed), so convert to hex
            #print("RGB color array found in map data. Converting to hex")
            for i in range(0,len(colorscale)):              
                red = extractRed(colorscale[i][1])
                green = extractGreen(colorscale[i][1])
                blue = extractBlue(colorscale[i][1])
                hx = '#{:02x}{:02x}{:02x}'.format(red, green , blue)
                #print(red, green, blue, hx)
                colorscale[i][1] = hx #replace rgb string with hex string
        
        #print(df['f-log'])
        #print(colorscale)
        
        #based on the value for each row, obtain the two colours and mixing to interpolate between them!
        df['c1'] = df.apply(lambda row : extractColorPositions(colorscale, row['f-log'])[0], axis =1).astype(str)
        df['c2'] = df.apply(lambda row : extractColorPositions(colorscale, row['f-log'])[1], axis =1).astype(str)
        df['mix'] = df.apply(lambda row : extractColorPositions(colorscale, row['f-log'])[2], axis =1).astype(float)
        
        #get hex val by linear interpolation between c1, c2, mix for each row, and also convert this into the component RGB vals (for deck.gl)
        df['hex'] = df.apply(lambda row : colorFader(row['c1'], row['c2'], row['mix']), axis =1) #linear interpolation between two hex colours
        
        df['r'] = df.apply(lambda row : ImageColor.getcolor(row['hex'], "RGB")[0], axis =1).astype(str) #return the red (index 0 of tuple) from the RGB tuble returned by getcolor 
        df['g'] = df.apply(lambda row : ImageColor.getcolor(row['hex'], "RGB")[1], axis =1).astype(str) #return the greeen (index 0 of tuple) from the RGB tuble returned by getcolor 
        df['b'] = df.apply(lambda row : ImageColor.getcolor(row['hex'], "RGB")[2], axis =1).astype(str) #return the blue (index 0 of tuple) from the RGB tuble returned by getcolor 
          
        #print(df.columns)
        #print(colorscale)
    
    #For discrete data, set colour scales based on global lookup
    elif var_type == "discrete":                
        
        #mimic the same df structure as the continuous dataset, so the logic further below works (creating dummy columns)
        df['value_log10'] = "dummy"
        df['f-log'] = "dummy"
        df['c1'] = "dummy"
        df['c2'] = "dummy"
        df['mix'] = "dummy"
        df['hex'] = "dummy"  
        
        #obtain array of discrete categories
        discrete_cats = pd.unique(df['Value'])
       
        #loop through unique discrete categories and set the hex value based on discrete colour scale lookup
        for i in range(0,len(discrete_cats)):                    
            df.loc[df['Value']==discrete_cats[i], 'hex'] = discrete_colorscale[i][0][1]
        
        #Convert the hex value to separate R/G/B values as cols, as this data is needed by pdeck to render the globe        
        df['r'] = df.apply(lambda row : ImageColor.getcolor(row['hex'], "RGB")[0], axis =1).astype(str) #return the red (index 0 of tuple) from the RGB tuble returned by getcolor 
        df['g'] = df.apply(lambda row : ImageColor.getcolor(row['hex'], "RGB")[1], axis =1).astype(str) #return the greeen (index 0 of tuple) from the RGB tuble returned by getcolor 
        df['b'] = df.apply(lambda row : ImageColor.getcolor(row['hex'], "RGB")[2], axis =1).astype(str) #return the blue (index 0 of tuple) from the RGB tuble returned by getcolor 
    
    
    #NOW ADD COLOUR AND SERIES SPECIFIC DATA TO GEOJSON
    
    #deep copy globe geojson
    gj = copy.deepcopy(geojson)
   
    #loop through all 1300 geojson features and set the value based on current series
    for i in range(0, len(gj['features'])):
        try:                               
            
            #At this point, check if country name/val None (i.e. no data in DF), and grab the country name for the properties of the JSON, and set the value to 0            
            #if no data exists for a country in this series, store the country name from json, set val to 0, and set a nice grey colour so it displays on jigsaw
            if gj['features'][i]['properties']['sr_un_a3'] not in df["m49_un_a3"].values:
                #print(gj['features'][i]['properties']['BRK_NAME'])
                #gj['features'][i]['COUNTRY'] = gj['features'][i]['properties']['BRK_NAME'] #grab country name from json              
                gj['features'][i]['VALUE'] = "no data"                    
                
                #Colour ocean blue
                if gj['features'][i]['COUNTRY'] == "Ocean" or gj['features'][i]['COUNTRY'] == "Caspian Sea":
                    gj['features'][i]['properties']['red'] = "134" #ocean blue
                    gj['features'][i]['properties']['green'] = "181"
                    gj['features'][i]['properties']['blue'] = "209"
                
                #Colour all other features missing data as grey
                else:
                    gj['features'][i]['properties']['red'] = "224" #grey
                    gj['features'][i]['properties']['green'] = "224"
                    gj['features'][i]['properties']['blue'] = "224"
                
            else:             
                #set value of current series to this row item in json               
                gj['features'][i]['VALUE'] = df[df["m49_un_a3"]==gj['features'][i]['properties']['sr_un_a3']].iloc[0,4] #set geojson property to the value of the series for that country
                
                #colour the feature for this country based on the interpolated colours
                if jellybean == False:
                    gj['features'][i]['properties']['red']= df[df["m49_un_a3"]==gj['features'][i]['properties']['sr_un_a3']].iloc[0,16]
                    gj['features'][i]['properties']['green']= df[df["m49_un_a3"]==gj['features'][i]['properties']['sr_un_a3']].iloc[0,17]
                    gj['features'][i]['properties']['blue']= df[df["m49_un_a3"]==gj['features'][i]['properties']['sr_un_a3']].iloc[0,18]
         
        except IndexError as error:
            print("Globe: Exception thrown attempting to build custom dict from json (expected)")
         
    
    return gj

def colorFader(c1,c2,mix=0): 
    #fade (linear interpolate) from color c1 (at mix=0) to c2 (mix=1)
    #c1 and c2 are hex colours, mix variable is a float point between 0 and 1, and colour will be interpolated and a hex colour will be returned
    c1=np.array(mpl.colors.to_rgb(c1))
    c2=np.array(mpl.colors.to_rgb(c2))
    return mpl.colors.to_hex((1-mix)*c1 + mix*c2)
   
def extractRed(rgb_str):
    #rip out the red    
    r = rgb_str.split(",")
    red = r[0].strip("rgb() ") #select red val from the array, and remove zeros    
    return int(red)
    
def extractGreen(rgb_str):
    #rip out the green    
    g = rgb_str.split(",")
    green = g[1].strip() #select red val from the array, and remove zeros    
    return int(green)
    
def extractBlue(rgb_str):
    #rip out the blue
    b = rgb_str.split(",")
    blue = b[2].strip("() ") #select red val from the array, and remove zeros    
    return int(blue)

def extractColorPositions(colorscale, val):
    #this function takes the given colour array and a value, and returns the respective c1, c2, mix vars needed for linear colour interpolation

    colorscale_r = copy.deepcopy(colorscale)
    
    #reverse colorscale
    for i in range(0, len(colorscale)):        
        colorscale_r[(len(colorscale)-1)-i][1] = colorscale[i][1]
    
    colorscale = copy.deepcopy(colorscale_r)
    
    #Find the val position in the colour scale, store the two colours and the mix level to interpolate between them based on val
    for i in range(0, len(colorscale)-1):    
        
        if val <= colorscale[i+1][0]:
            c1 = colorscale[i][1]
            c2 = colorscale[i+1][1]
            mix = (val - colorscale[i][0]) / (colorscale[i+1][0] - colorscale[i][0])    
            #print(c1)
            #print(c2)
            #print(mix)
            return c1, c2, mix
    return    
    