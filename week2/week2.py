import pandas as pd
import numpy as np
import plotly.express as px
import json

def readjson(filepath):
    with open(filepath, mode='r') as f:
        return json.load(f)

def readDataFrame():
    randomdata = {'CENTRAL': 0.8903601342256143,
                    'SOUTHERN': 0.8642882941363439,
                    'BAYVIEW': 0.925634097746596,
                    'MISSION': 0.7369022697287458,
                    'PARK': 0.9864113307070926,
                    'RICHMOND': 0.5422239624697017,
                    'INGLESIDE': 0.5754056712571605,
                    'TARAVAL': 0.5834730737348696,
                    'NORTHERN': 0.08148199528212985,
                    'TENDERLOIN': 0.37014287986350447}

    randomdata = pd.DataFrame(randomdata,index=[0])
    randomdata = randomdata.T.reset_index()
    randomdata.columns = ['DISTRICT','RATE']
    return randomdata

def main():
    randomdata = readDataFrame()
    sfmap = readjson("SFPd.json")
    fig = px.choropleth_mapbox(data_frame=randomdata,
                            geojson=sfmap, 
                            locations='DISTRICT', 
                            color='RATE', 
                            featureidkey="properties.DISTRICT",
                            color_continuous_scale="viridis",
                            range_color=(0, 1),
                            mapbox_style="carto-darkmatter",
                            zoom=12, 
                            center = {"lat": 37.8088, "lon": -122.4043},
                            opacity=0.5
                            )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.show()

if __name__ == '__main__':
    main()