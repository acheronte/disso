# plotter.py

# Plotting utility to visualise the crossings process.


import os

from pathlib import Path
from bokeh.plotting import figure, show
from bokeh.models import HoverTool, Label
from bokeh.io import output_file, export_svgs


def univariate_time_series(x, y, filename='', **kwargs):
    """ Plots a univariate time-series. """

    # plot data and canvas settings
    p = figure(plot_width=1200, plot_height=500, x_axis_type='datetime')
    p.line(x, y, color='orange', line_width=2.1, legend_label=kwargs.get('main_legend_label', filename))
    p.circle(x, y, color='orange', fill_alpha=0.0)
    if 'mean' in kwargs:
        mean = kwargs['mean']
        mean_series = [mean for _ in range(len(y))]
        p.line(x, mean_series, color='blue', line_width=3.0, legend_label='Mean', line_dash='dotted')
    if 'st_dev' in kwargs:
        st_dev = kwargs['st_dev']
        st_dev_series = [st_dev for _ in range(len(y))]
        p.line(
            x,
            st_dev_series,
            color='green',
            line_width=3.0,
            legend_label='+/- 1 Standard Deviation',
            line_dash='dotted'
        )
        negative_st_dev_series = [-st_dev for _ in range(len(y))]
        p.line(
            x,
            negative_st_dev_series,
            color='green',
            line_width=3.0,
            legend_label='+/- 1 Standard Deviation',
            line_dash='dotted'
        )

    # aesthetics
    if 'number_of_crossings' in kwargs:
        # label independent of data
        number_of_crossings_label = Label(
            x=550,  # x-coordinates
            y=30,  # y-coordinates
            text_font_size='9pt',
            x_units='screen',
            y_units='screen',
            text=f"Crossings = {kwargs['number_of_crossings']}",
            border_line_color=None
        )
        p.add_layout(number_of_crossings_label)

    p.title.text = kwargs.get('plot_title', filename)
    p.title.align = 'center'
    p.toolbar_location = None
    p.outline_line_color = None
    # p.xgrid[0].ticker.desired_num_ticks = 10
    p.yaxis.ticker.num_minor_ticks = 0
    p.xgrid.grid_line_color = None
    p.yaxis.formatter.use_scientific = False
    hover = HoverTool(
        tooltips=[
            ('Date', '@x{%d-%m-%Y}'),
        ],
        formatters={
            'x': 'datetime'
        }
    )
    p.tools = [hover]
    if 'x_axis_label' in kwargs:
        p.xaxis.axis_label = kwargs['x_axis_label']
    if 'y_axis_label' in kwargs:
        p.yaxis.axis_label = kwargs['y_axis_label']
    p.legend.location = kwargs['legend_position']
    p.legend.border_line_alpha = 0.4
    p.legend.border_line_width = 2
    p.legend.label_text_font_size = '14pt'
    p.xaxis.axis_label_text_font_size = '14pt'
    p.yaxis.axis_label_text_font_size = '14pt'
    p.xaxis.axis_label_standoff = 16
    p.yaxis.axis_label_standoff = 8

    # save plot to file and render
    p.output_backend = 'svg'
    output_dir = Path.cwd() / 'plots'
    os.makedirs(output_dir, exist_ok=True)
    output_file('plots/{}.html'.format(filename))
    export_svgs(p, filename=f'plots/{filename}.svg')
    show(p)

if __name__ == '__main__':
    import pandas as pd
    from statistics import mean, stdev

    full_range = pd.read_csv('data.csv')
    full_range['obs'] = pd.to_datetime(full_range['obs'])
    # To visualise different periods simply change the indices in the data variable
    mid_2009 = full_range[7:129]
    univariate_time_series(
        mid_2009['obs'],
        mid_2009['uhat1_2009_2010'],
        filename='eurchf_hist_spread',
        plot_title='EUR/CHF Historical Spread',
        y_axis_label='EUR/CHF Spread',
        x_axis_label='Business days from 01/01/2009 - 30/06/2009',
        main_legend_label='EUR/CHF spread',
        legend_position='top_right',
        mean=mean(mid_2009['uhat1_2009_2010']),
        st_dev=stdev(mid_2009['uhat1_2009_2010']),
    )

    univariate_time_series(
        mid_2009['obs'],
        mid_2009['uhat2_2009_2010'],
        filename='gbpchf_hist_spread',
        plot_title='GBP/CHF Historical Spread',
        y_axis_label='GBP/CHF Historical Spread',
        x_axis_label='Business days from 01/01/2009 - 30/06/2009',
        main_legend_label='GBP/CHF spread',
        legend_position='bottom_right',
        mean=mean(mid_2009['uhat2_2009_2010']),
        st_dev=stdev(mid_2009['uhat2_2009_2010']),
    )

