import statease as se
from sklearn.model_selection import KFold
from sklearn.metrics import r2_score
from se360demo import get_data_path
from statease.row_status import RowStatus
import matplotlib.pyplot as plt

delivery_time = get_data_path('delivery-time.dxpx')
se_conn = se.connect()
se_conn.open_design(delivery_time)

factor_names = se_conn.list_factors()
a_fac = se_conn.get_factor(factor_names[0])
b_fac = se_conn.get_factor(factor_names[1])
response = se_conn.get_response(se_conn.list_responses()[0])

def fit(estimation_set, prediction_set, analysis_name):

    prediction_points = []
    prediction_observed = []
    for r in prediction_set:
        prediction_points.append([ a_fac.values[r], b_fac.values[r] ])
        prediction_observed.append(response.values[r])

    se_conn.set_row_status(prediction_set, RowStatus.IGNORED)

    estimate_analysis = se_conn.create_analysis('Delivery Time, y', analysis_name)
    estimate_analysis.set_model('A+B')
    predictions = estimate_analysis.predict(prediction_points, coded=False)

    se_conn.set_row_status(prediction_set, RowStatus.NORMAL)
    return r2_score(prediction_observed, predictions)

# first split the data using the comments field, which contains
# flags to indicate which rows were selected by Montgomery, Peck, and Vining
# using the DUPLEX algorithm
comments = se_conn.get_comments()

estimation_set = []
prediction_set = []
for r in range(0, len(comments)):
    if comments[r] == 'P':
        prediction_set.append(r)
    else:
        estimation_set.append(r)
r2 = fit(estimation_set, prediction_set, 'MPV')
print("MPV R2: {}".format(r2))

# k-fold cross-validation with k=4
n_splits = 4
X = [ [a_fac.values[r], b_fac.values[r]] for r in range(0, len(a_fac.values)) ]
kf = KFold(n_splits=n_splits)
scores = []
split_num = 1
for train, test in kf.split(X):
    score = fit(train.tolist(), test.tolist(), '{} splits, split #{}'.format(kf.n_splits, split_num))
    print("Split {} R2: {}".format(split_num, score))
    split_num += 1
    scores.append(score)

fig, ax = plt.subplots()
labels = [ str(split+1) for split in range(0, n_splits) ]
x = [ split+1 for split in range(0, n_splits) ]
ax.set_xlabel('Fold')
ax.set_ylabel('R²')
colors = [ "#005883" ] * len(scores)

ax.bar(x, scores, tick_label=labels, color=colors)
ax.bar_label(ax.containers[0], fmt='%.4f')
ax.axhline(0, color='grey', linewidth=0.8)
plt.show()
