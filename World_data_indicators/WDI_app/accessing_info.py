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
    df = dataset_lookup[['dataset_raw', 'dataset_label', 'dataset_label']].copy()
    df.columns=['dataset_raw', 'dataset_label', 'api_label']
    df = df.drop_duplicates()
    df['api_label'] = df.api_label.str.replace(' ','-')
    df['api_label'] = df.api_label.str.replace('%','percent')
    df['api_label'] = df.api_label.str.replace('?','-')
    df['api_label'] = df.api_label.str.replace('+','-')
    df['api_label'] = df.api_label.str.replace(',','-')
    api_dict_raw_to_label={}
    api_dict_label_to_raw={}
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
        except IndexError as error:
            print("add_regions: Exception thrown attempting to build custom dict from json (expected)")
    return

def create_unique_country_list(path):
    c =  pd.read_csv(
       path,
       encoding="utf-8",
       names=["m49_a3_country", "country", "continent", "region_un", "region_wb", "su_a3"],
    )
    c["m49_a3_country"] = c["m49_a3_country"].astype(str)
    c['m49_a3_country'] = c['m49_a3_country'].str.zfill(3)  
    c = c.iloc[1:,]
    
    return c

def create_dataset_lookup(path):
    d= pd.read_csv(
       path,
       encoding="utf-8",
       names=["dataset_id", "dataset_raw", "dataset_label", "source", "link", "var_type", "nav_cat", "colour", "nav_cat_nest", "tag1", "tag2", "explanatory_note"],
    )
    d = d.iloc[1:,] 
    return d

def get_source(ds_lookup, series):    
    source = ds_lookup[ds_lookup['dataset_raw']==series].iloc[0]['source']
    return source
  
def get_link(ds_lookup, series):    
    
    link = ds_lookup[ds_lookup['dataset_raw']==series].iloc[0]['link']
       
    return link
        
def check_year(pop, series, year):
    df = pop.loc[(pop['Series'] == series)]
    years = pd.DataFrame(pd.unique(df["Year"]), columns=["value"])['value'].tolist()
    return int(year) in years
    
def get_years(df):
    df = df.sort_values('Year')
    years = pd.DataFrame(pd.unique(df["Year"]), columns=["value"])
    years = years["value"].to_dict()
    return years

def get_year_slider_index(pop, series, year):
    yr_slider = get_years(pop.loc[(pop['Series'] == series)])
    if len(yr_slider) > 0:
        for index in range(len(yr_slider)):  
            if yr_slider[index] == year: return index  
    return len(yr_slider)-1

def get_year_slider_marks(series, pop, INIT_YEAR_SLIDER_FONTSIZE, INIT_YEAR_SLIDER_FONTCOLOR, year_slider_selected):    
    year_slider_marks = get_years(pop.loc[(pop['Series'] == series)])     
    year_slider_marks2 = {
                    i: {
                        "label": year_slider_marks[i],
                        "style": {"fontSize": INIT_YEAR_SLIDER_FONTSIZE, 'color':INIT_YEAR_SLIDER_FONTCOLOR, 'fontWeight': 'normal'},
                    }
                    for i in range(0, len(year_slider_marks))
                }   
    
    year_slider_marks=year_slider_marks2     
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
    d = copy.copy(df[(df["Year"] == int(year)) & (df["Series"] == series)])    
    d['Value'] = d['Value'].astype(float) 
    d = d.drop_duplicates(subset ="m49_un_a3")
    d = d.sort_values('Value', ascending=ascending)
    return d

def get_series(df, series, ascending):
    d = copy.copy(df[(df["Series"] == series)])
    d['Year'] = d['Year'].astype(int)
    d['Value'] = d['Value'].astype(float)
    d = d.sort_values('Value', ascending=ascending)
    return d

def load_geo_data_JSON(json_path):    
    countries_json = json.load(open(json_path, 'r', encoding='utf-8'))
    return countries_json

def load_3d_geo_data_JSON_cleaned(json_path):    

    gj = json.load(open(json_path, 'r', encoding='utf-8'))
    return gj

def update_3d_geo_data_JSON(df, geojson, colorscale, jellybean, var_type, discrete_colorscale):
    df['fix1'] = "dummmy"
    df['fix2'] = "dummy"
    if var_type == "continuous" or var_type == "ratio" or var_type == "quantitative":
        df['Value'] = df['Value'].astype(float)
        df = df[df.Value > 0]  
        df['value_log10'] = np.log10(df['Value'], out=np.zeros_like(df['Value']), where=(df['Value']!=0))        
        df = df[df.value_log10 != 0]       
        mn = np.min(df["value_log10"])
        mx = np.max(df["value_log10"])
        if mn < 0.0:            
            df['value_log10'] = df['value_log10'] + abs(mn)
        df['f-log'] = df['value_log10'] / np.max(df["value_log10"]) 
        if colorscale[0][1][0] != "#":
            for i in range(0,len(colorscale)):              
                red = extractRed(colorscale[i][1])
                green = extractGreen(colorscale[i][1])
                blue = extractBlue(colorscale[i][1])
                hx = '#{:02x}{:02x}{:02x}'.format(red, green , blue)
                colorscale[i][1] = hx 
        df['c1'] = df.apply(lambda row : extractColorPositions(colorscale, row['f-log'])[0], axis =1).astype(str)
        df['c2'] = df.apply(lambda row : extractColorPositions(colorscale, row['f-log'])[1], axis =1).astype(str)
        df['mix'] = df.apply(lambda row : extractColorPositions(colorscale, row['f-log'])[2], axis =1).astype(float)
        df['hex'] = df.apply(lambda row : colorFader(row['c1'], row['c2'], row['mix']), axis =1) 
        
        df['r'] = df.apply(lambda row : ImageColor.getcolor(row['hex'], "RGB")[0], axis =1).astype(str) 
        df['g'] = df.apply(lambda row : ImageColor.getcolor(row['hex'], "RGB")[1], axis =1).astype(str) 
        df['b'] = df.apply(lambda row : ImageColor.getcolor(row['hex'], "RGB")[2], axis =1).astype(str) 
        
        df['value_log10'] = "dummy"
        df['f-log'] = "dummy"
        df['c1'] = "dummy"
        df['c2'] = "dummy"
        df['mix'] = "dummy"
        df['hex'] = "dummy"  
        
        discrete_cats = pd.unique(df['Value'])
       
        for i in range(0,len(discrete_cats)):                    
            df.loc[df['Value']==discrete_cats[i], 'hex'] = discrete_colorscale[i][0][1]
        
        df['r'] = df.apply(lambda row : ImageColor.getcolor(row['hex'], "RGB")[0], axis =1).astype(str)
        df['g'] = df.apply(lambda row : ImageColor.getcolor(row['hex'], "RGB")[1], axis =1).astype(str) 
        df['b'] = df.apply(lambda row : ImageColor.getcolor(row['hex'], "RGB")[2], axis =1).astype(str) 

    gj = copy.deepcopy(geojson)
   
    for i in range(0, len(gj['features'])):
        try:                               
            if gj['features'][i]['properties']['sr_un_a3'] not in df["m49_un_a3"].values:        
                gj['features'][i]['VALUE'] = "no data"                    
                if gj['features'][i]['COUNTRY'] == "Ocean" or gj['features'][i]['COUNTRY'] == "Caspian Sea":
                    gj['features'][i]['properties']['red'] = "134" #ocean blue
                    gj['features'][i]['properties']['green'] = "181"
                    gj['features'][i]['properties']['blue'] = "209"
                else:
                    gj['features'][i]['properties']['red'] = "224" #grey
                    gj['features'][i]['properties']['green'] = "224"
                    gj['features'][i]['properties']['blue'] = "224"
                
            else:             
                gj['features'][i]['VALUE'] = df[df["m49_un_a3"]==gj['features'][i]['properties']['sr_un_a3']].iloc[0,4]
                gj['features'][i]['properties']['red']= df[df["m49_un_a3"]==gj['features'][i]['properties']['sr_un_a3']].iloc[0,16]
                gj['features'][i]['properties']['green']= df[df["m49_un_a3"]==gj['features'][i]['properties']['sr_un_a3']].iloc[0,17]
                gj['features'][i]['properties']['blue']= df[df["m49_un_a3"]==gj['features'][i]['properties']['sr_un_a3']].iloc[0,18]
         
        except IndexError as error:
            print("Globe: Exception thrown attempting to build custom dict from json (expected)")
         
    
    return gj

def colorFader(c1,c2,mix=0): 
    c1=np.array(mpl.colors.to_rgb(c1))
    c2=np.array(mpl.colors.to_rgb(c2))
    return mpl.colors.to_hex((1-mix)*c1 + mix*c2)
   
def extractRed(rgb_str):
    #rip out the red    
    r = rgb_str.split(",")
    red = r[0].strip("rgb() ") 
    return int(red)
    
def extractGreen(rgb_str):
    #rip out the green    
    g = rgb_str.split(",")
    green = g[1].strip() 
    return int(green)
    
def extractBlue(rgb_str):
    #rip out the blue
    b = rgb_str.split(",")
    blue = b[2].strip("() ") 
    return int(blue)

def extractColorPositions(colorscale, val):
    colorscale_r = copy.deepcopy(colorscale)
    for i in range(0, len(colorscale)):        
        colorscale_r[(len(colorscale)-1)-i][1] = colorscale[i][1]
    
    colorscale = copy.deepcopy(colorscale_r)
    
    for i in range(0, len(colorscale)-1):    
        
        if val <= colorscale[i+1][0]:
            c1 = colorscale[i][1]
            c2 = colorscale[i+1][1]
            mix = (val - colorscale[i][0]) / (colorscale[i+1][0] - colorscale[i][0])    

            return c1, c2, mix
    return    
    
