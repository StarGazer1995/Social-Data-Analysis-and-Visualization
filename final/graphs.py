from datetime import datetime
import pandas
import plotly
import plotly.express as px

def sensorCheck(dataFrame, selectedSensor):
    if selectedSensor != None:
        if isinstance(selectedSensor, list):
            if isinstance(selectedSensor[0], str): 
                data = dataFrame[dataFrame['Sensor_Name'].isin(selectedSensor)]
            if isinstance(selectedSensor[0], int):
                data = dataFrame[dataFrame['Sensor_ID'].isin(selectedSensor)]
        elif isinstance(selectedSensor, int or str):
            if isinstance(selectedSensor, str): 
                data = dataFrame[dataFrame['Sensor_Name'] == selectedSensor]
            if isinstance(selectedSensor, int):
                data = dataFrame[dataFrame['Sensor_ID'] == selectedSensor]
        if data.size<1: #Invalid sensor selection
            print('sensor selection is invalid, selection is redirected to None')
            data = dataFrame
    else:
        data = dataFrame
    return data

def dateCheck(dataFrame, date):
    dt1 = datetime(2019,1,1,0)
    if isinstance(date, str):
        
        try:
            date = list(map(int,date.split('-')))
            dt2 = datetime(date[0],date[1],date[2],0)
        except:
            '''
            If something wrong, the date will be redirected to 2019.1.1
            '''
            print('There is something wrong, developers need to check the input date')
            dt2 = datetime(2019,1,1,0)
        start = dt2 - dt1
        start = start.total_seconds()//3600
        end = start+24
    elif isinstance(date, list):
        start = list(map(int,date[0].split('-')))
        dt2 = datetime(start[0],start[1],start[2], start[3])
        
        endD = list(map(int,date[1].split('-')))
        dt3 = datetime(endD[0],endD[1],endD[2],endD[3])
        if dt3 < dt2:
            raise('Invalid date selection')
        start = dt2 - dt1
        start = int(start.total_seconds()//3600)
        
        end = dt3 - dt1
        end = int(end.total_seconds()//3600)
    else:
        raise('not implemented error')
    return dataFrame.loc[start:end]

def mapUpdate(dataFrame, date=None, selectedSensor=None):
    '''
    This function is implemented for map demomstration
            dataFrame : pandas DataFrame
            date : string : y-m-d[start date]
            selectedSensor: arrayLike[int] or None
    '''
    initLat = -37.8136
    initLon = 144.9631
    zoom = 12
    data = dateCheck(dataFrame, date)
    data = sensorCheck(data, selectedSensor)
    
    px.set_mapbox_access_token('pk.eyJ1Ijoiemhhb2dvbmciLCJhIjoiY2treXVxeXl6MGJzbjJ3cW5qejNwMWxkYyJ9.cPz0LUvg4_tC_mrOqBvZ3A')
    return px.scatter_mapbox(data, lon='longitude', lat='latitude' 
                  ,hover_name='Sensor_Name', hover_data=['Hourly_Counts'], title=date
                  ,color='Hourly_Counts',zoom=12
                 ,animation_frame = data.index,mapbox_style="dark"
                 )

def histUpdate(dataFrame, timePeriod, selectedSensor):
    data = dateCheck(dataFrame, timePeriod)
    data = sensorCheck(data, selectedSensor)
    data = data.groupby('Time').Hourly_Counts.agg('mean')
    return px.bar(x=data.index
                  , y=data.values#, hover_data=['mean']
                  , color=data.values, labels={'pop':'mean value of selected sensors'}
                  , height=400)