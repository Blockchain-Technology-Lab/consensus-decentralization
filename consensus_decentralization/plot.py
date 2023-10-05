import argparse
import logging
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import seaborn as sns
import numpy as np
from collections import defaultdict
import consensus_decentralization.helper as hlp
import heapq
import colorcet as cc
import pandas as pd


def plot_animated_lines(df, x_label, y_label, filename, path, colors):
    df.index = pd.to_datetime(df.timeframe)
    df.drop(['timeframe'], axis=1, inplace=True)
    num_time_steps = df.shape[0]
    num_lines = df.shape[1]

    fig = plt.figure(figsize=(10, 6))
    plt.xticks(rotation=45, ha="right", rotation_mode="anchor")  # rotate the x-axis values
    plt.subplots_adjust(bottom=0.2, top=0.9)  # ensure the dates (on the x-axis) fit in the screen
    plt.xlabel(x_label)
    plt.ylabel(y_label)

    def animate(i):
        plt.legend(df.columns, frameon=False)  # , loc='upper right')
        p = plt.plot(df[:i].index, df[:i].values)  # note it only returns the dataset, up to the point i
        for line in range(num_lines):
            p[line].set_color(colors[line])  # set the colour of each line

    ani = animation.FuncAnimation(fig, animate, interval=100, frames=num_time_steps, repeat=False)
    filename += ".gif"
    ani.save(f'{str(path)}/{filename}', writer=animation.PillowWriter())
    plt.close(fig)


def plot_lines(data, x_label, y_label, filename, path, xtick_labels, colors, title=''):
    data.plot(figsize=(10, 6), color=colors)
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.legend(frameon=False)
    plt.xticks(ticks=xtick_labels.index, labels=xtick_labels, rotation=45)
    locs, x_labels = plt.xticks()
    for i, label in enumerate(x_labels):
        if i % 5 == 0:  # only keep every 5th xtick label
            continue
        label.set_visible(False)
    filename += ".png"
    plt.savefig(path / filename, bbox_inches='tight')


def plot_stack_area_chart(values, execution_id, path, ylabel, legend_labels, tick_labels, legend):
    """

    :param values: the data to be plotted. numpy array of shape (number of total entities, number of time steps)
    :param path: the path to save the figure to
    """
    fig = plt.figure(figsize=(6, 4))
    num_entities = values.shape[0]
    num_time_steps = values.shape[1]
    col = sns.color_palette(cc.glasbey, n_colors=num_entities)
    plt.stackplot(range(num_time_steps), values, colors=col, edgecolor='face', linewidth=0.0001, labels=legend_labels)
    plt.margins(0)
    plt.xlabel("Time")
    plt.ylabel(ylabel)
    plt.xticks(ticks=range(num_time_steps), labels=tick_labels, rotation=45)
    locs, x_labels = plt.xticks()
    for i, label in enumerate(x_labels):
        if i % 5 == 0:  # only keep every 5th xtick label
            continue
        label.set_visible(False)
    if legend:
        visible_legend_labels = [label for label in legend_labels if not label.startswith('_')]
        if len(visible_legend_labels) > 0:
            max_labels_per_column = 25
            ncols = len(visible_legend_labels) // (max_labels_per_column + 1) + 1
            fig.legend(loc='upper right', bbox_to_anchor=(0.9, -0.1), ncol=ncols, fancybox=True, borderpad=0.2,
                       labelspacing=0.3, handlelength=1)
    filename = "poolDynamics-" + execution_id + ".png"
    plt.savefig(path / filename, bbox_inches='tight')
    plt.close(fig)


def plot_animated_stack_area_chart(values, execution_id, path, ylabel, legend_labels, tick_labels, legend):
    """

    :param values: the data to be plotted. numpy array of shape (number of total entities, number of time steps)
    :param path: the path to save the figure to
    """
    fig = plt.figure(figsize=(6, 4))
    num_entities = values.shape[0]
    num_time_steps = values.shape[1]
    col = sns.color_palette(cc.glasbey, n_colors=num_entities)
    plt.margins(0)
    plt.xlabel("Time")
    plt.ylabel(ylabel)
    plt.xticks(ticks=range(num_time_steps), labels=tick_labels, rotation=45)
    plt.subplots_adjust(bottom=0.2, top=0.9)  # ensure the dates (on the x-axis) fit in the screen
    locs, x_labels = plt.xticks()
    for i, label in enumerate(x_labels):
        if i % 5 == 0:  # only keep every 5th xtick label
            continue
        label.set_visible(False)

    ims = []
    for n in range(1, num_time_steps + 1):
        if legend:
            visible_legend_labels = [label for label in legend_labels if not label.startswith('_')]
            if len(visible_legend_labels) > 0:
                max_labels_per_column = 25
                ncols = len(visible_legend_labels) // (max_labels_per_column + 1) + 1
                fig.legend(loc='upper left', bbox_to_anchor=(0.9, 0.9), ncol=ncols, fancybox=True, shadow=True,
                           borderpad=0.2, labelspacing=0.3, handlelength=1)
        x = list(range(num_time_steps))[:n]
        y = [entity[:n] for entity in values]
        im = plt.stackplot(x, y, colors=col, edgecolor='face', linewidth=0.0001, labels=legend_labels)
        ims.append(im)

    ani = animation.ArtistAnimation(fig, ims, interval=100, repeat_delay=10000)

    filename = "poolDynamics-" + execution_id + ".gif"
    ani.save(f'{str(path)}/{filename}', writer=animation.PillowWriter())
    plt.close(fig)


def plot_dynamics_per_ledger(ledgers, top_k=-1, animated=False, legend=False):
    for ledger in ledgers:
        path = hlp.OUTPUT_DIR / ledger
        figures_path = path / 'figures'
        if not figures_path.is_dir():
            figures_path.mkdir()

        start_year, end_year = hlp.get_start_end_years()

        end_month = 3
        pool_blocks_by_month = {}  # dictionary of dictionaries (one dictionary for each month under consideration)
        pool_block_share_by_month = {}  # same as above but for fractions instead of absolute values for each month
        for year in range(start_year, end_year + 1):
            for month in range(1, 13):
                timeframe = f'{year}-0{month}' if month < 10 else f'{year}-{month}'
                filename = f'{timeframe}.csv'
                file = path / "blocks_per_entity" / filename
                if not file.is_file():
                    continue  # Only plot timeframes for which mapped data exist
                blocks = hlp.get_blocks_per_entity_from_file(file)
                total_blocks = sum(blocks.values())
                if total_blocks == 0:
                    continue
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
        # values_to_plot = {'absolute_values': pool_blocks_by_month, 'relative_values': pool_block_share_by_month}
        values_to_plot = {'relative_values': pool_block_share_by_month}
        ylabels = {'absolute_values': 'Number of produced blocks', 'relative_values': 'Share of produced blocks (%)'}
        for key, values_by_month in values_to_plot.items():
            pool_blocks = values_by_month.values()
            pool_blocks_by_month_matrix = defaultdict(lambda: [0] * len(pool_blocks))
            for i, values_by_month in enumerate(pool_blocks):
                for entity, blocks in values_by_month.items():
                    pool_blocks_by_month_matrix[entity][i] = blocks
            if key == 'relative_values':
                threshold = 5
                labels = [
                    f"{pool_name if len(pool_name) <= 15 else pool_name[:15] + '..'} "
                    f"({round(max(contributions_list), 1)}%)"
                    if any(contribution > threshold for contribution in contributions_list)
                    else f"_{pool_name}"
                    for (pool_name, contributions_list) in pool_blocks_by_month_matrix.items()
                ]
            else:
                labels = []
            values = np.array(list(pool_blocks_by_month_matrix.values()))
            if animated:
                plot_animated_stack_area_chart(
                    values=values,
                    execution_id=f'{ledger}_{key}_top_{top_k}' if top_k > 0 else f'{ledger}_{key}_all',
                    path=figures_path,
                    ylabel=ylabels[key],
                    legend_labels=labels,
                    tick_labels=months,
                    legend=legend
                )
            else:
                plot_stack_area_chart(
                    values=values,
                    execution_id=f'{ledger}_{key}_top_{top_k}' if top_k > 0 else f'{ledger}_{key}_all',
                    path=figures_path,
                    ylabel=ylabels[key],
                    legend_labels=labels,
                    tick_labels=months,
                    legend=legend
                )


def plot_comparative_metrics(ledgers, metrics, animated=False):
    for metric in metrics:
        figures_path = hlp.OUTPUT_DIR / 'figures'
        if not figures_path.is_dir():
            figures_path.mkdir()
        filename = f'{metric}.csv'
        metric_df = pd.read_csv(hlp.OUTPUT_DIR / filename)
        # only keep rows that contain at least one (non-nan) value in the columns that correspond to the ledgers
        metric_df = metric_df[metric_df.iloc[:, 1:].notna().any(axis=1)]
        ledger_columns_to_keep = [col for col in metric_df.columns if col in ledgers]
        num_lines = metric_df.shape[1]
        colors = sns.color_palette(cc.glasbey, n_colors=num_lines)
        if len(ledger_columns_to_keep) > 0:
            metric_df = metric_df[['timeframe'] + ledger_columns_to_keep]
            if animated:
                plot_animated_lines(
                    df=metric_df,
                    x_label='Time',
                    y_label=metric,
                    filename=f"{metric}_{'_'.join(ledger_columns_to_keep)}",
                    path=figures_path,
                    colors=colors
                )
            else:
                plot_lines(
                    data=metric_df,
                    x_label='Time',
                    y_label=metric,
                    filename=f"{metric}_{'_'.join(ledger_columns_to_keep)}",
                    path=figures_path,
                    xtick_labels=metric_df['timeframe'],
                    colors=colors
                )


def plot(ledgers, metrics, animated):
    logging.info("Creating plots..")
    plot_dynamics_per_ledger(ledgers, animated=False, legend=True)
    plot_comparative_metrics(ledgers, metrics, animated=False)
    if animated:
        plot_dynamics_per_ledger(ledgers, animated=True)
        plot_comparative_metrics(ledgers, metrics, animated=True)


if __name__ == '__main__':
    ledgers = ['bitcoin', 'bitcoin_cash', 'cardano', 'dogecoin', 'ethereum', 'litecoin', 'tezos', 'zcash']
    metrics = ['entropy', 'gini', 'hhi', 'nakamoto_coefficient']
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
    parser.add_argument(
        '--animated',
        action='store_true',
        help='Flag to specify whether to also generate animated plots.'
    )
    args = parser.parse_args()
    plot(args.ledgers, args.metrics, args.animated)
