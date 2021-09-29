import statease as se
from sklearn.model_selection import KFold
from sklearn.metrics import mean_squared_error
from se360demo import get_data_path
import matplotlib.pyplot as plt
import numpy as np
from statease.row_status import RowStatus
from statistics import mean, stdev

se_conn = se.connect()

def fit(X, estimation_set, prediction_set, model, name, gpm=False):
    '''Fit a subset of X using the estimation_set list, then calculate
    the mean_squared_error of the prediction set.'''

    se_conn.set_row_status(estimation_set, RowStatus.NORMAL)
    se_conn.set_row_status(prediction_set, RowStatus.IGNORED)

    prediction_points = []
    prediction_observed = []
    for r in prediction_set:
        prediction_points.append([ X[r][0], X[r][1] ])
        prediction_observed.append(response.values[r])

    if gpm:
        estimate_analysis = se_conn.create_analysis('R1', name, 'Gaussian Process')
    else:
        estimate_analysis = se_conn.create_analysis('R1', name)
    estimate_analysis.set_model(model)

    predictions = estimate_analysis.predict(prediction_points, coded=False)
    return mean_squared_error(prediction_observed, predictions)

def fit_k(X, model, n_splits, gpm=False, plot=True):
    '''Split X into k folds, fit each one, and return the scores.
    Optionally plot the scores in a bar chart.'''

    kf = KFold(n_splits=n_splits)
    scores = []
    split_num = 1
    for train, test in kf.split(X):
        score = fit(X, train.tolist(), test.tolist(), model, '{} {} splits, split #{}'.format('gpm' if gpm else 'ols', kf.n_splits, split_num), gpm)
        split_num += 1
        scores.append(score)

    print()
    print("{} {} splits".format('GPM' if gpm else 'OLS', n_splits))
    print("mean: {:.4f}".format(mean(scores)))
    print("std dev: {:.4f}".format(stdev(scores)))
    print("max: {:.4f}".format(max(scores)))
    print("min: {:.4f}".format(min(scores)))

    if plot:
        fig, ax = plt.subplots()
        labels = [ str(split+1) for split in range(0, n_splits) ]
        x = range(0, n_splits)
        ax.set_xlabel('Fold')
        ax.set_ylabel('MSE')
        colors = [ "#005883" if s > 0 else "#F37546" for s in scores ]

        ax.bar(x, scores, color=colors, tick_label=labels)
        ax.bar_label(ax.containers[0], fmt='%.4f')
        if gpm:
            ax.set_title('GPM')
        else:
            ax.set_title('OLS')
        plt.show()

    return scores

def plot_multi_bars(ols_scores, glm_scores):
    ''' Plot two sets of scores in the same bar chart. '''

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

# first CV wtih a trig function simulation
data = get_data_path('sin.dxpx')
se_conn.open_design(data)

factor_names = se_conn.list_factors()
a_fac = se_conn.get_factor(factor_names[0])
b_fac = se_conn.get_factor(factor_names[1])
response = se_conn.get_response(se_conn.list_responses()[0])

X = [ [a_fac.values[r], b_fac.values[r]] for r in range(0, len(a_fac.values)) ]
quartic_model = 'A+B+AB+A^2+B^2+A^2B+AB^2+A^3+B^3+A^2B^2+A^3B+AB^3+A^4+B^4'
ols_scores = fit_k(X, quartic_model, 8, gpm=False, plot=False)
gpm_scores = fit_k(X, 'A+B', 8 , gpm=True, plot=False)
plot_multi_bars(ols_scores, gpm_scores)

# second CV with the rsm data
data = get_data_path('rsm-sim.dxpx')
se_conn.open_design(data)

factor_names = se_conn.list_factors()
a_fac = se_conn.get_factor(factor_names[0])
b_fac = se_conn.get_factor(factor_names[1])
response = se_conn.get_response(se_conn.list_responses()[0])

# plot these scores separately, because the scores diverge too much to make the multi-bar chart useful
X = [ [a_fac.values[r], b_fac.values[r]] for r in range(0, len(a_fac.values)) ]
ols_scores = fit_k(X, 'A+B+AB+A^2+B^2', 8, gpm=False, plot=True)
gpm_scores = fit_k(X, 'A+B', 8, gpm=True, plot=True)
