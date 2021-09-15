"""
Functions for plotting results and descriptive analysis of data.
"""

#%%

from pathlib import Path
from collections import defaultdict

import time
import json
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

RESULTS_DIR = Path(__file__).parents[1] / 'results'

METRIC_FULL_NAME = {
    'Top1_Acc': 'Accuracy',
    'BalAcc': 'Balanced Accuracy',
    'Loss': 'Loss'
    }

def stack_results(results, metric, mode):
    """
    Stacks results for multiple 'experiences' along same axis in df.
    """

    results_dfs = []

    # Get metrics for each training "experience"'s test set
    for i in range(5):
        metric_dict = defaultdict(list)
        for k,v in results[i].items():
            if f'{metric}_Exp/eval_phase/{mode}_stream' in k:
                new_k = k.split('/')[-1].replace('Exp00','Task ').replace('Exp0','Task ')
                metric_dict[new_k] = v[1]

        df = pd.DataFrame.from_dict(metric_dict)
        df.index.rename('Epoch', inplace=True)
        stacked = df.stack().reset_index()
        stacked.rename(columns={'level_1': 'Task', 0: METRIC_FULL_NAME[metric]}, inplace=True)

        results_dfs.append(stacked)

    stacked = pd.concat(results_dfs, sort=False)

    return stacked

def plot_metric(method, model, results, mode, metric, ax=None):
    """
    Plots given metric from dict.
    Stacks multiple plots (i.e. different per-task metrics) over training time.

    `mode`: ['train','test'] (which stream to plot)
    """
    ax = ax or plt.gca()

    stacked = stack_results(results, metric, mode)

    # Only plot task accuracies after examples have been encountered
    # JA: this len() etc will screw up when plotting CI's
    tasks = stacked['Task'].str.split(' ',expand=True)[1].astype(int)
    n_epochs = 15
    stacked = stacked[tasks*n_epochs<=stacked['Epoch'].astype(int)]

    sns.lineplot(data=stacked, x='Epoch', y=METRIC_FULL_NAME[metric], hue='Task', ax=ax)
    ax.set_title(method, size=10)
    ax.set_ylabel(model)
    ax.set_xlabel('')

def clean_subplot(i, j, axes, metric):
    """
    Removes top/rights spines.
    Removes titles/legend.
    Fixes y/metric limits.
    """
    ax = axes[i,j]
    
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    if i>0:
        ax.set_title('')
    if i>0 or j>0:
        try:
            ax.get_legend().remove()
        except AttributeError:
            pass

    if metric == 'Loss':
        ylim = (0,2)
    else:
        ylim = (0,1)
    
    plt.setp(axes, ylim=ylim)

def clean_plot(fig, axes, metric):
    """
    Cleans all subpots. Removes duplicate legends.
    """
    for i in range(len(axes)):
        for j in range(len(axes[0])):
            clean_subplot(i,j,axes,metric)
            
    handles, labels = axes[0,0].get_legend_handles_labels()
    axes[0,0].get_legend().remove()
    fig.legend(handles, labels, loc='center right', title='Task')

def annotate_plot(fig, domain, outcome, metric):
    """
    Adds x/y labels and suptitles.
    """
    try:
        fig.supxlabel('Epoch')
        fig.supylabel(METRIC_FULL_NAME[metric], x=0)
    except AttributeError:
        fig.text(0.5, 0.04, 'Epoch', ha='center')
        fig.text(0.04, 0.5, METRIC_FULL_NAME[metric], va='center', rotation='vertical')

    fig.suptitle(f'Continual Learning model comparison \n'
                 f'Outcome: {outcome} | Domain Increment: {domain}', y=1.1)

def plot_all_model_strats(data, domain, outcome, mode, metric, timestamp, savefig=True):
    """
    Pairplot of all models vs strategies.
    """

    # Load results
    with open(RESULTS_DIR / f'results_{data}_{outcome}_{domain}.json', encoding='utf-8') as handle:
        res = json.load(handle)

    models = res.keys()
    strategies = next(iter(res.values())).keys()

    n_rows = len(models)
    n_cols = len(strategies)

    # Experience plots
    fig, axes = plt.subplots(n_rows, n_cols, sharex=True, sharey=True, figsize=(20,20*n_rows/n_cols), squeeze=False, dpi=250)

    for i, model in enumerate(models):
        for j, strategy in enumerate(strategies):
            plot_metric(strategy, model, res[model][strategy], mode, metric, axes[i,j])

    clean_plot(fig, axes, metric)
    annotate_plot(fig, domain, outcome, metric)

    if savefig:
        file_loc = RESULTS_DIR / 'figs' / data / outcome / domain / timestamp
        file_loc.mkdir(parents=True, exist_ok=True)
        plt.savefig(file_loc / f'Exp_{mode}_{metric}.png')
    
    # Stream plots
    fig, axes = plt.subplots(n_rows, 2, sharex=False, sharey=True, gridspec_kw={'width_ratios':[2,1]}, figsize=(2*20/n_cols,20*n_rows/n_cols), squeeze=False, dpi=250)

    for i, model in enumerate(models):
        plot_avg_metric(model, res[model], mode, metric, axes[i,0])
        barplot_avg_metric(model, res[model], mode, metric, axes[i,1])

    clean_plot(fig, axes, metric)
    annotate_plot(fig, domain, outcome, metric)

    if savefig:
        file_loc = RESULTS_DIR / 'figs' / data / outcome / domain / timestamp
        file_loc.mkdir(parents=True, exist_ok=True)
        plt.savefig(file_loc / f'Stream_{mode}_{metric}.png')

def stack_avg_results(results_strats, metric, mode):
    results_dfs = []

    # Get metrics for each training "experience"'s test set
    for i in range(5):
        metric_dict = defaultdict(list)

        # Get avg (stream) metrics for each strategy
        for strat, metrics in results_strats.items():
            for k, v in metrics[i].items():
                if f'{metric}_Stream/eval_phase/{mode}_stream' in k:
                    metric_dict[strat] = v[1]

        df = pd.DataFrame.from_dict(metric_dict)
        df.index.rename('Epoch', inplace=True)
        stacked = df.stack().reset_index()
        stacked.rename(columns={'level_1': 'Strategy', 0: METRIC_FULL_NAME[metric]}, inplace=True)

        results_dfs.append(stacked)

    stacked = pd.concat(results_dfs, sort=False)

    return stacked

def plot_avg_metric(model, results, mode, metric, ax=None):
    """
    Plots given metric from dict.
    Stacks multiple plots (i.e. different strategies' metrics) over training time.

    `mode`: ['train','test'] (which stream to plot)
    """
    ax = ax or plt.gca()

    stacked = stack_avg_results(results, metric, mode)

    sns.lineplot(data=stacked, x='Epoch', y=METRIC_FULL_NAME[metric], hue='Strategy', ax=ax)
    ax.set_title('Average performance over all tasks', size=10)
    ax.set_ylabel(model)
    ax.set_xlabel('')

def barplot_avg_metric(model, results, mode, metric, ax=None):
    ax = ax or plt.gca()

    stacked = stack_avg_results(results, metric, mode)
    stacked = stacked[stacked['Epoch']==stacked['Epoch'].max()]

    sns.barplot(data=stacked, x='Strategy', y=METRIC_FULL_NAME[metric], ax=ax)
    ax.set_title('Final average performance over all tasks', size=10)
    ax.set_xlabel('')

def results_to_latex():
    raise NotImplementedError



# DESCRIPTIVE PLOTS

def plot_demographics():
    """
    Plots demographic information of eICU dataset.
    """

    df = pd.DataFrame() #data_processing.load_eicu(drop_dupes=True)
    _, axes = plt.subplots(3,2, sharey=True, figsize=(18,18), squeeze=False)

    df['gender'].value_counts().plot.bar(ax=axes[0,0], rot=0, title='Gender')
    df['ethnicity'].value_counts().plot.bar(ax=axes[1,0], rot=0, title='Ethnicity')
    df['ethnicity_coarse'].value_counts().plot.bar(ax=axes[1,1], rot=0, title='Ethnicity (coarse)')
    df['age'].plot.hist(bins=20, label='age', ax=axes[0,1], title='Age')
    df['region'].value_counts().plot.bar(ax=axes[2,0], rot=0, title='Region (North America)')
    df['hospitaldischargestatus'].value_counts().plot.bar(ax=axes[2,1], rot=0, title='Outcome')
    plt.show()
    plt.close()

# %%
