import statease as se
import matplotlib.pyplot as plt
import numpy as np
from se360demo import get_data_path

rsm_cubic = get_data_path('rsm-cubic.dxpx')
se_conn = se.connect()
se_conn.open_design(rsm_cubic)

analysis_names = se_conn.list_analyses()
factor_count = len(se_conn.list_factors())

# retrieve the two Analysis objects that we will be plotting, and also the A factor
analyses = [ se_conn.get_analysis(analysis_names[0]), se_conn.get_analysis(analysis_names[1]) ]
a_fac = se_conn.get_factor(se_conn.list_factors()[0])

# create a set of 5 labels for the A factor in actual units
x_labels = [ '{:.3f}'.format(x) for x in np.linspace(a_fac.low, a_fac.high, 5) ]
x_ticks = np.linspace(-1, 1, 5)

# generate data from -1 to 1 to use to vary the A factor for prediction
x = np.linspace(-1, 1, 50)

# generate a list of points to predict at, leaving the other factors at the center point
centroid = [ 0 ] * (factor_count - 1)
prediction_points = [ [ tick ] + centroid for tick in x ]

# make predictions with both of the Analysis objects
y1 = analyses[0].predict(prediction_points, coded=True)
y2 = analyses[1].predict(prediction_points, coded=True)

fig, ax = plt.subplots()

ax.set_xticks(x_ticks)
ax.set_xticklabels(x_labels)
ax.set_xlabel('{} ({})'.format(a_fac.name, a_fac.units))

ax.plot(x, y1, 'green', alpha=0.6, label=analyses[0].name)

ax.set_ylabel(analyses[0].name, color='green')
ax.tick_params(axis='y', labelcolor='green')

ax2 = ax.twinx()
ax2.plot(x, y2, 'blue', alpha=0.6, label=analyses[1].name)
ax2.set_ylabel(analyses[1].name, color='blue')
ax2.tick_params(axis='y', labelcolor='blue')

# add lines for predictions where B is set to its high and low
b_low = [ 0 ] * (factor_count - 1)
b_low[0] = -1
prediction_points = [ [ tick ] + b_low for tick in x ]
y3 = analyses[0].predict(prediction_points, coded=True)

ax.plot(x, y3, 'green', linestyle='dashed', alpha=0.6, label='{} B Low'.format(analyses[0].name))

b_high = [ 0 ] * (factor_count - 1)
b_high[0] = 1
prediction_points = [ [ tick ] + b_high for tick in x ]
y4 = analyses[0].predict(prediction_points, coded=True)

ax.plot(x, y4, 'green', linestyle='dotted', alpha=0.6, label='{} B High'.format(analyses[0].name))

fig.legend()

plt.show()
