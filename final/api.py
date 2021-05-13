from datetime import datetime
import pandas as pd
import plotly
import plotly.express as px
import plotly.graph_objects as go
import joblib

template = dict(
    layout=go.Layout(activeshape=go.layout.Activeshape(fillcolor='rgba(255,255,255,0)'),
                    colorscale=go.layout.Colorscale(diverging='icefire')
                    )
)

class Fail(BaseException):
    def __init__(self, m):
        self.m = m
    def __str__(self):
        return self.m

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
    data = data.groupby('Yhours').Hourly_Counts.agg('mean')
    data = data.reset_index()
    data['Time'] = data['Yhours'] - data['Yhours'][0]

    return px.bar(data, x='Time'
                  , y='Hourly_Counts'#, hover_data=['mean']
                  , labels={'pop':'mean value of selected sensors'}
                  , template = template
                  , height=400)

def prediction(filePath, dataFrame, timePeriod, sensors=None, ifweather=False, ifprevious=False):
    '''
        filePath: the path to the model file
        df: the using dataframe
        time: [start, end] y-m-d-h
        sensors:arrayLike[int] or None
        ifweather: if use weather
        ifprevious:if use previous data
    '''
    data = dataFrame.drop(['Year'
             , 'Unnamed: 0'
             , 'Sensor_Name'
             , 'latitude'
             , 'longitude'
             ,'Wind_direction'
            ], axis=1)
    data = pd.get_dummies(data, columns=['Sensor_ID'], prefix = ['id'],drop_first=False)

    if ifweather:
        if 'Weather' not in filePath:
            Fail('The file path[{}] is wrong!:Weather'.format(filePath))
        else:
            data = pd.get_dummies(data, columns=['Condition', 'UV'], prefix = ['weather', 'uv'],drop_first=False)
    else:
        data = data.drop([
             'Temperature'
             ,'Humidity'
             
             ,'Wind_speed'
             ,'Pressure'
             ,'Condition'
             ,'UV'	
            ], axis=1)

            
    if ifprevious:
        if 'Previous' not in filePath:
            raise Fail('The file path[{}] is wrong!:Previous'.format(filePath))
    else:
        data = data.drop([
	          'previous1'
             ,'previous2'
            ], axis=1)
    
    if ifprevious and ifweather:
        if 'Weather' not in filePath and 'Previous' not in filePath:
            raise Fail('The file path[{}] is wrong!:Weather & Previous'.format(filePath))
    
    try:
        model = joblib.load(filePath)
    except:
        raise Fail('Cannot load model file!')



    data = dateCheck(data, timePeriod)
   
    oneHot = data.dropna()
    oneHot = oneHot.loc[:,oneHot.columns !='Hourly_Counts']

    predict = model.predict(oneHot)
    data['predict'] = predict
    data = data.groupby('Yhours')[['Hourly_Counts', 'predict']].agg('mean')
    data.reset_index(inplace=True)
    return px.line(data, x=data.index, 
                    y=['Hourly_Counts', 'predict'], 
                    labels={'pop':'prediction Using ML vs actucal data'},
                   template=template,
                    height=400)

if __name__ == '__main__':
    data = pd.read_csv('data/finalWithPreviousCountsandWeather.csv')
    data['Yhours'] = data['Yhours'].astype(int)
    data = data.set_index('Yhours').sort_index()
    modelPath1 = 'data/datawithWeatherandPreviousCounts.pkl'
    modelPath2 = 'data/datawithWeather.pkl'
    returned = prediction(modelPath2, data, ['2019-1-1-0', '2019-1-2-0'], ifweather=True, ifprevious=False)
    