import requests
import os
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import html
import csv

_PACKAGE_ROOT = os.path.abspath(os.path.dirname(__file__))
def get_data_path(path):
    return os.path.join(_PACKAGE_ROOT, 'data', path)

def get_rain_events_csv():
    '''Use a local csv file for the rain event data, rather than the APIs'''

    flow = {}
    precip = {}
    temp = {}
    with open(get_data_path('rain-events.csv'), newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in spamreader:
            if not row[0] or row[0] == 'date':
                continue
            key = datetime.strptime(row[0], '%Y-%m-%d')
            precip[key] = float(row[1])
            temp[key] = float(row[2])
            flow[key] = float(row[3])

    rain_events = {} 
    rain_start = None
    for k in list(flow.keys()):
        if precip[k] > 0:
            if rain_start:
                rain_events[rain_start]['end_date'] = k
                rain_events[rain_start]['total_precip'] += precip[k]
            else:
                rain_events[k] = {
                    'start_date': k,
                    'end_date': k,
                    'total_precip': precip[k],
                }
                rain_start = k
        else:
            rain_start = None

    for event in rain_events.values():
        # get the diff from the prev days flow to the max up to one day after
        prev_day = event['start_date'] - timedelta(days=1)
        if prev_day not in flow.keys():
            prev_day = event['start_date'] # could be beginning of time series
        next_day = event['end_date'] + timedelta(days=1)
        event['min_flow'] = flow[prev_day]
        event['max_flow'] = event['min_flow']
        event['avg_temp'] = 0
        days = int((next_day - prev_day).days)
        days_with_data = days
        for day in (prev_day + timedelta(n) for n in range(days)):
            if day in flow.keys() and flow[day] > event['max_flow']:
                event['max_flow'] = flow[day]
            if day in temp.keys():
                event['avg_temp'] += temp[day]
            else:
                days_with_data -= 1
        event['avg_temp'] = float(event['avg_temp']) / days_with_data
        event['flow_delta'] = event['max_flow'] - event['min_flow']
    return rain_events, flow, precip, temp

def get_rain_events(year):
    '''Fetches precipitation and water flow data from NOAA and USGS. Accumulates
    consecutive precip days from MSP into "rain events" and matches them up with
    an increase in the flow of Rice Creek'''

    site_id = '05288580' # rice creek USGS site number
    r = requests.get(
        "https://waterservices.usgs.gov/nwis/dv/?format=json&sites={site_id}&startDT={year}-06-15&endDT={year}-10-31&siteStatus=all".format(
            site_id=site_id,
            year=year,
        )
    )

    data = r.json()

    flow_data = data['value']['timeSeries'][0]
    flow_label = html.unescape(flow_data['variable']['variableName'])
    flow = {}
    for v in flow_data['values']:
        for v2 in v['value']:
            key = datetime.fromisoformat(v2['dateTime'])
            flow[key] = float(v2['value'])

    # generate at https://www.ncdc.noaa.gov/cdo-web/token
    token = os.environ['NOAA_TOKEN']
    noaa_station_id = 'GHCND:USW00014922' # MSP
    url = "https://www.ncdc.noaa.gov/cdo-web/api/v2/data?datasetid=GHCND&datatypeid=PRCP&datatypeid=TMAX&limit=1000&stationid={station}&startdate={year}-06-15&enddate={year}-10-31".format(
        station=noaa_station_id,
        year=year,
    )
    r = requests.get(
        url, 
        headers= { 'token': token }
    )

    data = r.json()

    precip = {}
    temp = {}
    for item in data['results']:
        key = datetime.fromisoformat(item['date'])
        # missing some dates in the flow data
        if key not in flow.keys():
            continue
        if item['datatype'] == 'PRCP':
            precip[key] = float(item['value']) / 100.0 / 2.54 # convert from 1/10ths mm to inches
        elif item['datatype'] == 'TMAX':
            temp[key] = float(item['value']) / 10.0 * 1.8 + 32 # convert from 1/10ths celsius to f

    for k in list(flow.keys()):
        if k not in precip.keys():
            flow.pop(k)
            if k in temp.keys():
                temp.pop(k)
        elif k not in temp.keys():
            flow.pop(k)
            if k in precip.keys():
                precip.pop(k)

    rain_events = {} 
    rain_start = None
    for k in list(flow.keys()):
        if precip[k] > 0:
            if rain_start:
                rain_events[rain_start]['end_date'] = k
                rain_events[rain_start]['total_precip'] += precip[k]
            else:
                rain_events[k] = {
                    'start_date': k,
                    'end_date': k,
                    'total_precip': precip[k],
                }
                rain_start = k
        else:
            rain_start = None

    for event in rain_events.values():
        # get the diff from the prev days flow to the max up to one day after
        prev_day = event['start_date'] - timedelta(days=1)
        if prev_day not in flow.keys():
            prev_day = event['start_date'] # could be beginning of time series
        next_day = event['end_date'] + timedelta(days=1)
        event['min_flow'] = flow[prev_day]
        event['max_flow'] = event['min_flow']
        event['avg_temp'] = 0
        days = int((next_day - prev_day).days)
        days_with_data = days
        for day in (prev_day + timedelta(n) for n in range(days)):
            if day in flow.keys() and flow[day] > event['max_flow']:
                event['max_flow'] = flow[day]
            if day in temp.keys():
                event['avg_temp'] += temp[day]
            else:
                days_with_data -= 1
        event['avg_temp'] = float(event['avg_temp']) / days_with_data
        event['flow_delta'] = event['max_flow'] - event['min_flow']

    return rain_events, flow, precip, temp

def plot_raw_data(flow, precip, temp):
    ''' This will plot every day's worth of streamflow data. '''
    dates = [ d.strftime('%Y-%m-%d') for d in flow.keys() ]

    plt.style.use('seaborn-whitegrid')
    plt.set_loglevel('WARNING')
    fig, ax = plt.subplots()
    fig.subplots_adjust(right=0.75)

    ax.plot(dates, flow.values(), alpha=0.6)
    ax.set_xticks(ax.get_xticks()[::14])
    ax.tick_params(axis='y', labelcolor='blue')
    ax.set_ylabel('Streamflow, ft^3/s', color='blue')
    ax.grid(False)

    plt.xticks(rotation=45)
    plt.xlabel('date')

    ax2 = ax.twinx()
    ax2.plot(dates, precip.values(), color='green', alpha=0.6)
    ax2.set_xticks(ax2.get_xticks()[::14])
    ax2.grid(False)
    ax2.tick_params(axis='y', labelcolor='green')
    ax2.set_ylabel('Precipitation, in.', color='green')

    ax3 = ax.twinx()
    ax3.spines.right.set_position(("axes", 1.2))
    ax3.plot(dates, temp.values(), color='orange', alpha=0.6)
    ax3.tick_params(axis='y', labelcolor='orange')
    ax3.set_ylabel('Temp, f', color='orange')
    ax3.set_xticks(ax3.get_xticks()[::14])
    # freezing temp line, not applicable unless the date ranges go beyond summer months
    # ax3.axhline(y=32, color='red', linestyle='--', alpha=0.6)

    plt.show()
