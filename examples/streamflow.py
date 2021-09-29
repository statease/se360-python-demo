import statease as se
import plotly.graph_objects as go
import numpy as np
from se360demo import get_rain_events, get_rain_events_csv, get_data_path

# set to true to fetch data from the web API
# this requires a NOAA token - generate at https://www.ncdc.noaa.gov/cdo-web/token
# the token needs to be assigned to an environment variable named NOAA_TOKEN
use_live_data = False

if not use_live_data:
    # load from a CSV file rather than the web API
    rain_events, flow, precip, temp = get_rain_events_csv()
else:
    rain_events = {}
    flow = {}
    precip = {}
    temp = {}
    for year in range(2011, 2022):
        re, f, p, t = get_rain_events(year)
        rain_events.update(re)
        flow.update(f)
        precip.update(p)
        temp.update(t)

# collapse rain events into lists to send to SE360
flow = []
temp = []
precip = []
for date, ev in rain_events.items():
    flow.append(ev['flow_delta'])
    precip.append(ev['total_precip'])
    temp.append(ev['avg_temp'])

empty_file = get_data_path('streamflow-empty.dxpx')
se_conn = se.connect()
se_conn.open_design(empty_file)

precip_fac = se_conn.get_factor('precip')
precip_fac.values = precip

temp_fac = se_conn.get_factor('temp')
temp_fac.values = temp

resp = se_conn.get_response('flow')
resp.values = flow

analysis = se_conn.create_analysis('flow', 'flow (2FI)')
analysis.set_model('A+B+AB')
anova = analysis.get_anova()
print(anova)

x = np.linspace(-1, 1, 40)
y = np.linspace(-1, 1, 40)
z = []

# predict one row of the grid at a time, stepping through the values of A
for i in range(0, x.size):
    prediction_points = [ [ x[i] , yi ] for yi in y ]
    z.append(analysis.predict(prediction_points, coded=True))

# generate a second set of predictions for a cubic model
analysis = se_conn.create_analysis('flow', 'flow (cubic)')
analysis.set_model('A+B+AB+A^2+B^2+A^2B+AB^2+A^3+B^3')

z2 = []

for i in range(0, x.size):
    prediction_points = [ [ x[i] , yi ] for yi in y ]
    z2.append(analysis.predict(prediction_points, coded=True))

fig = go.Figure(data=[
    go.Surface(z=np.transpose(z), x=x, y=y,
      contours=dict(
        x = dict( show=True ),
        y = dict( show=True ),
      ),
    ),
    go.Surface(z=np.transpose(z2), x=x, y=y, showscale=False, opacity=0.5),
])

# add some labels and convert ticks to actual values rather than coded
fig.update_layout(
    title='Streamflow',
    scene=dict(
        xaxis=dict(
            tickmode='array',
            tickvals=np.linspace(-1, 1, 5),
            ticks='outside',
            ticktext=[ '{:.3f}'.format(f) for f in np.linspace(precip_fac.low, precip_fac.high, 5) ]
        ),
        yaxis=dict(
            tickmode='array',
            tickvals=np.linspace(-1, 1, 5),
            ticks='outside',
            ticktext=[ '{:.3f}'.format(f) for f in np.linspace(temp_fac.low, temp_fac.high, 5) ]
        ),
        xaxis_title='{} ({})'.format(precip_fac.name, precip_fac.units),
        yaxis_title='{} ({})'.format(temp_fac.name, temp_fac.units),
        zaxis_title='{} ({})'.format(resp.name, resp.units),
    )
)
fig.show()
