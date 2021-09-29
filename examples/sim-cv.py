import statease as se
from sklearn.model_selection import KFold
from sklearn.metrics import mean_squared_error, r2_score
from se360demo import get_data
import numpy as np
from statease.row_status import RowStatus
import matplotlib.pyplot as plt
from statistics import mean, stdev

#data = get_data('rsm-sim.dxpx')
data = get_data('sin.dxpx')
se_conn = se.connect()
se_conn.open_design(data)

factor_names = se_conn.list_factors()
a_fac = se_conn.get_factor(factor_names[0])
b_fac = se_conn.get_factor(factor_names[1])
response = se_conn.get_response(se_conn.list_responses()[0])

def fit(estimation_set, prediction_set, name, gpm=False):

    print()
    print("Analyzing {}".format(name))

    se_conn.set_row_status(estimation_set, RowStatus.NORMAL)
    se_conn.set_row_status(prediction_set, RowStatus.IGNORED)

    prediction_points = []
    prediction_observed = []
    for r in prediction_set:
        prediction_points.append([ a_fac.values[r], b_fac.values[r] ])
        prediction_observed.append(response.values[r])

    if gpm:
        estimate_analysis = se_conn.create_analysis('R1', name, 'Gaussian Process')
        estimate_analysis.set_model('A+B')
    else:
        estimate_analysis = se_conn.create_analysis('R1', name)
        #estimate_analysis.set_model('A+B+AB+A^2+B^2')
        estimate_analysis.set_model('A+B+AB+A^2+B^2+A^2B+AB^2+A^3+B^3+A^2B^2+A^3B+AB^3+A^4+B^4')

    predictions = estimate_analysis.predict(prediction_points, coded=False)
    print(predictions)

    mse = mean_squared_error(prediction_observed, predictions)
    print("MSE: {}".format(mse))
    return mse

X = [ [a_fac.values[r], b_fac.values[r]] for r in range(0, len(a_fac.values)) ]

def fit_k(n_splits, gpm=False, plot=True):
    kf = KFold(n_splits=n_splits)
    scores = []
    split_num = 1
    for train, test in kf.split(X):
        score = fit(train.tolist(), test.tolist(), '{} {} splits, split #{}'.format('gpm' if gpm else 'ols', kf.n_splits, split_num), gpm)
        split_num += 1
        scores.append(score)

    print()
    print("{} splits scores".format(n_splits))
    print("mean: {:.4f}".format(mean(scores)))
    print("std dev: {:.4f}".format(stdev(scores)))
    print("max: {:.4f}".format(max(scores)))
    print("min: {:.4f}".format(min(scores)))

    if plot:
        fig, ax = plt.subplots()
        labels = [ str(split+1) for split in range(0, n_splits) ]
        ax.set_xlabel('Fold')
        ax.set_ylabel('MSE')
        colors = [ "#005883" if s > 0 else "#F37546" for s in scores ]

        ax.bar(labels, scores, color=colors)
        ax.bar_label(ax.containers[0], fmt='%.4f')
        ax.axhline(0, color='grey', linewidth=0.8)
        plt.show()

    return scores

def plot_multi_bars(ols_scores, glm_scores):

    fig, ax = plt.subplots()
    labels = [ str(split+1) for split in range(0, len(ols_scores)) ]
    x = np.arange(len(labels))
    ax.set_xlabel('Fold')
    ax.set_ylabel('MSE')

    width = 0.35

    ax.bar(x - width / 2, ols_scores, width, color=[ "#005883" ] * len(ols_scores), label='OLS (mean: {:.4f})'.format(mean(ols_scores)))
    ax.bar(x + width / 2, gpm_scores, width, color=[ "#00AEEF" ] * len(ols_scores), label='GPM (mean: {:.4f})'.format(mean(gpm_scores)))
    ax.bar_label(ax.containers[0], fmt='%.3f')
    ax.bar_label(ax.containers[1], fmt='%.3f')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()

    fig.tight_layout()
    plt.show()

ols_scores = fit_k(8, gpm=False, plot=False)
gpm_scores = fit_k(8, gpm=True, plot=False)
plot_multi_bars(ols_scores, gpm_scores)
