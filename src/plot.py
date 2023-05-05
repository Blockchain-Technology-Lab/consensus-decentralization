import argparse
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from collections import defaultdict
import src.helpers.helper as hlp
import heapq
import colorcet as cc
import pandas as pd


def plot_lines(data, x_label, y_label, filename, path, xtick_labels, title=''):
    fig = plt.figure(figsize=(10, 5))
    data.plot()
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.legend()
    num_time_steps = data.shape[0]
    plt.xticks(ticks=range(num_time_steps), labels=xtick_labels, rotation=45)
    locs, x_labels = plt.xticks()
    for i, label in enumerate(x_labels):
        if i % 5 == 0:  # only keep every 5th xtick label
            continue
        label.set_visible(False)
    filename += ".png"
    plt.savefig(path / filename, bbox_inches='tight')
    plt.close(fig)


def plot_stack_area_chart(values, execution_id, path, ylabel, legend_labels, tick_labels):
    """

    :param values: the data to be plotted. numpy array of shape (number of total entities, number of time steps)
    :param path: the path to save the figure to
    """
    fig = plt.figure(figsize=(10, 5))
    num_entities = values.shape[0]
    num_time_steps = values.shape[1]
    col = sns.color_palette(cc.glasbey, n_colors=num_entities)
    plt.stackplot(range(num_time_steps), values, colors=col, edgecolor='face', linewidth=0.0001, labels=legend_labels)
    plt.xlim(xmin=0.0, xmax=num_time_steps - 1)
    plt.xlabel("Time")
    plt.ylabel(ylabel)
    plt.xticks(ticks=range(num_time_steps), labels=tick_labels, rotation=45)
    locs, x_labels = plt.xticks()
    for i, label in enumerate(x_labels):
        if i % 5 == 0:  # only keep every 5th xtick label
            continue
        label.set_visible(False)
    if num_entities <= 15:
        plt.legend()
    filename = "poolDynamics-" + execution_id + ".png"
    plt.savefig(path / filename, bbox_inches='tight')
    plt.close(fig)


def plot_dynamics_per_ledger(ledgers):
    for ledger in ledgers:
        print(f'Plotting {ledger} data..')
        path = hlp.OUTPUT_DIR / ledger
        figures_path = path / 'figures'
        if not figures_path.is_dir():
            figures_path.mkdir()
        start_year = 2018
        end_year = 2023
        end_month = 3
        top_k = -1
        pool_blocks_by_month = {}  # dictionary of dictionaries (one dictionary for each month under consideration)
        pool_block_share_by_month = {}  # same as above but for fractions instead of absolute values for each month
        for year in range(start_year, end_year + 1):
            for month in range(1, 13):
                timeframe = f'{year}-0{month}' if month < 10 else f'{year}-{month}'
                filename = f'{timeframe}.csv'
                blocks = hlp.get_blocks_per_entity_from_file(path / filename)
                total_blocks = sum(blocks.values())
                if top_k > 0:
                    top_k_keys_by_values = heapq.nlargest(top_k, blocks, key=blocks.get)
                    pool_blocks_by_month[timeframe] = {key: blocks[key] for key in top_k_keys_by_values}
                else:
                    pool_blocks_by_month[timeframe] = blocks
                pool_block_share_by_month[timeframe] = {e: b * 100 / total_blocks for e, b in
                                                        pool_blocks_by_month[timeframe].items()}
                if year == end_year and month == end_month:
                    break
        months = pool_blocks_by_month.keys()
        values_to_plot = {'absolute_values': pool_blocks_by_month, 'relative_values': pool_block_share_by_month}
        ylabels = {'absolute_values': 'Number of produced blocks', 'relative_values': 'Share of produced blocks (%)'}
        for key, values_by_month in values_to_plot.items():
            pool_blocks = values_by_month.values()
            pool_blocks_by_month_matrix = defaultdict(
                lambda: [0] * len(pool_blocks)
            )
            for i, values_by_month in enumerate(pool_blocks):
                for entity, blocks in values_by_month.items():
                    pool_blocks_by_month_matrix[entity][i] = blocks
            labels = pool_blocks_by_month_matrix.keys()
            values = np.array(list(pool_blocks_by_month_matrix.values()))
            plot_stack_area_chart(
                values=values,
                execution_id=f'{ledger}_{key}_top_{top_k}' if top_k > 0 else f'{ledger}_{key}_all',
                path=figures_path,
                ylabel=ylabels[key],
                legend_labels=labels,
                tick_labels=months
            )


def plot_comparative_metrics(ledgers, metrics):
    for metric in metrics:
        print(f'Plotting {metric}..')
        figures_path = hlp.OUTPUT_DIR / 'figures'
        if not figures_path.is_dir():
            figures_path.mkdir()
        filename = f'{metric}.csv'
        metric_df = pd.read_csv(hlp.OUTPUT_DIR / filename)
        ledger_columns_to_keep = list(set(metric_df.columns) & set(ledgers))
        if len(ledger_columns_to_keep) > 0:
            metric_df = metric_df[['timeframe'] + ledger_columns_to_keep]
            plot_lines(metric_df, x_label='Time', y_label=metric, filename=f"{metric}_{'_'.join(ledger_columns_to_keep)}",
                       path=figures_path, xtick_labels=metric_df['timeframe'])


def plot(ledgers, metrics):
    plot_dynamics_per_ledger(ledgers)
    plot_comparative_metrics(ledgers, metrics)


if __name__ == '__main__':
    ledgers = ['bitcoin', 'bitcoin_cash', 'cardano', 'dash', 'dogecoin', 'ethereum', 'litecoin', 'tezos', 'zcash']
    metrics = ['entropy', 'gini', 'hhi', 'nc']
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--ledgers',
        nargs="*",
        type=str.lower,
        default=ledgers,
        choices=[ledger for ledger in ledgers],
        help='The ledgers whose data will be plotted.'
    )
    parser.add_argument(
        '--metrics',
        nargs="*",
        type=str.lower,
        default=metrics,
        choices=[metric for metric in metrics],
        help='The metrics to plot.'
    )
    args = parser.parse_args()
    plot(args.ledgers, args.metrics)
