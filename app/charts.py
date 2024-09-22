import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.font_manager import FontProperties

from app.text_config import get_text

plt.style.use('classic')

charts_config = {
    'cols': 2,
    'legend_field_font_size': 12,
    'legend_title_font': FontProperties(size=14, weight='bold'),
    'pie_title_font': FontProperties(size=14, weight='bold'),
}


def create_daily_report_charts(report_data: pd.DataFrame):
    # Set a Seaborn style
    sns.set_theme(style="whitegrid")

    # Calculate number of rows needed
    n_cols = charts_config['cols']
    n_rows = (len(report_data) + n_cols - 1) // n_cols  # Ceiling division to get the number of rows

    # Create a figure with subplots
    fig, axs = plt.subplots(n_rows, n_cols)
    axs = axs.flatten()  # Flatten the array of axes for easy iteration

    # Define a color palette
    colors = sns.color_palette("Set2")

    # Collect legend data to item object
    items_legend_data = {}

    # Create a pie chart for each item
    for ax, (index, row) in zip(axs, report_data.iterrows()):
        name, tracked_value, goal_value = row

        is_overflow = tracked_value > goal_value

        # for pies: we have 3 branches: overflow, unreached, 50/50
        if is_overflow:
            sizes = [goal_value, tracked_value - goal_value]  # Goal (not visible) and Overflow
            labels = [None, get_text('charts-goal-overdone')]
        elif tracked_value < goal_value:
            sizes = [tracked_value, goal_value - tracked_value]  # Result and Remaining Goal
            labels = [get_text('charts-tracked-value'), get_text('charts-goal-unreached')]
        else:
            sizes = [tracked_value, 0]  # Result and Goal (not visible)
            labels = [get_text('charts-tracked-value'), None]

        # for legend: we have two orders -> overflow and others
        if is_overflow:
            values = [goal_value, tracked_value]
            legend_labels = [get_text('charts-goal-value'), get_text('charts-tracked-value')]
        else:
            values = [tracked_value, goal_value]
            legend_labels = [get_text('charts-tracked-value'), get_text('charts-goal-value')]

        # Custom function for formatting the percentage
        def custom_autopct(pct):
            current_approximated_value = int(pct * sum(sizes) / 100)

            if is_overflow:
                # overflow value
                overflow_value = (tracked_value - goal_value) % goal_value
                return str(overflow_value) if overflow_value == current_approximated_value else ''

            # calculate correct values for case when we have result smaller than goal
            unreached_value = goal_value - tracked_value  # unreached value

            # branch when goal reached
            if tracked_value == goal_value:
                return str(tracked_value) if tracked_value == current_approximated_value else ''
            # branch when tracked value bigger than unreached
            elif tracked_value > unreached_value:
                return str(unreached_value) if unreached_value >= current_approximated_value else str(tracked_value)
            # branch when tracked value lower than unreached
            elif tracked_value < unreached_value:
                return str(tracked_value) if tracked_value >= current_approximated_value else str(unreached_value)
            # branch when 50/50
            else:
                return current_approximated_value

        # Create pie chart
        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=labels,
            autopct=custom_autopct,
            startangle=90,
            colors=colors,
            shadow=True,
            explode=(0.1, 0)
        )
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        ax.set_title(name, fontweight='bold', fontsize=14)

        # Customize the text properties
        for text in autotexts:
            text.set_color('white')
            text.set_fontsize(14)

        # Collect data for the legend
        items_legend_data[name] = {
            'labels': [f'{label}' for label in legend_labels],
            'values': values,
        }

    # Hide any empty subplots if the number of items is less than the total number of subplots
    for i in range(len(report_data), len(axs)):
        axs[i].axis('off')

    # Calculate figure height in inches
    fig_height = fig.get_size_inches()[1]

    # Calculate a step size relative to figure height (adjust scaling factor as needed)
    y_anchor_step = 1 / fig_height  # We can scale this down further if necessary

    # Set starting anchor point at the top of the figure
    y_anchor = 0.8

    for item_name, item_data in items_legend_data.items():
        legend = plt.figlegend(
            [f'{label}: {value}' for label, value in zip(item_data['labels'], item_data['values'])],
            loc='center right',
            fontsize=charts_config['legend_field_font_size'],
            bbox_to_anchor=(1.1, y_anchor),
            frameon=True
        )

        legend.set_title(item_name, prop=charts_config['legend_title_font'])

        y_anchor -= y_anchor_step

    # Adjust layout for better spacing and avoid overlap
    plt.tight_layout(rect=(0, 0, 0.85, 1))  # Adjust the right margin to make space for the legend

    return plt
