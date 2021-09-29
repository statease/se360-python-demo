import statease as se
import numpy as np
import calendar
from sklearn.metrics import mean_squared_error, r2_score
from datetime import datetime
from se360demo import get_rain_events_csv, get_data_path
from statease.row_status import RowStatus

rain_events, _, _, _ = get_rain_events_csv()

flow = []
temp = []
precip = []
dates= []
for date, ev in rain_events.items():
    dates.append(date)
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

for year in range(2011, 2022):
    estimation_set = []
    prediction_set = []
    for r in range(0, len(dates)):
        if dates[r].year == year:
            prediction_set.append(r)
        else:
            estimation_set.append(r)

    prediction_points = []
    prediction_observed = []
    for r in prediction_set:
        prediction_points.append([ precip_fac.values[r], temp_fac.values[r] ])
        prediction_observed.append(resp.values[r])

    se_conn.set_row_status(estimation_set, RowStatus.NORMAL)
    se_conn.set_row_status(prediction_set, RowStatus.IGNORED)
    estimate_analysis = se_conn.create_analysis('flow', str(year))
    estimate_analysis.set_model('A+B+AB')

    predictions = estimate_analysis.predict(prediction_points, coded=False)
    mse = mean_squared_error(prediction_observed, predictions)
    r2 = r2_score(prediction_observed, predictions)

    total_precip = 0
    for p in prediction_observed:
        total_precip += p
    obs_avg  = total_precip / len(prediction_observed)

    total_ss = 0
    residual_ss = 0
    for i in range(0, len(predictions)):
        total_ss += pow((prediction_observed[i] - obs_avg), 2)
        residual_ss += pow((predictions[i] - prediction_observed[i]), 2)

    print("{} R2 Pred: {:.4f}, mse: {:.4f}".format(year, r2, mse))

for month in range(6, 11):
    estimation_set = []
    prediction_set = []
    for r in range(0, len(dates)):
        if dates[r].month == month:
            prediction_set.append(r)
        else:
            estimation_set.append(r)

    prediction_points = []
    prediction_observed = []
    for r in prediction_set:
        prediction_points.append([ precip_fac.values[r], temp_fac.values[r] ])
        prediction_observed.append(resp.values[r])

    se_conn.set_row_status(estimation_set, RowStatus.NORMAL)
    se_conn.set_row_status(prediction_set, RowStatus.IGNORED)
    estimate_analysis = se_conn.create_analysis('flow', str(month))
    estimate_analysis.set_model('A+B+AB')

    predictions = estimate_analysis.predict(prediction_points, coded=False)
    mse = mean_squared_error(prediction_observed, predictions)
    r2 = r2_score(prediction_observed, predictions)
    print("{} R2 Pred: {:.4f}, mse: {:.4f}".format(calendar.month_abbr[month], r2, mse))
