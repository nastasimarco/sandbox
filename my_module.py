"""
This module contains functions that I found useful.
For now it's generic. Later it would be better to divide the functions
in module with some shared context. For now this will serve.

List of functions:
- spectrum_plot(inputfile, category=0, xticks_step=3)

Author: Marco Nastasi
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def spectrum_plot(inputfile, category=0, xticks_step=3):
    """Read the inputfile of leq and spectrum and return a bar plot with
    errorbars of the selected category.
    - inputfile -- is the .csv file containing the database
    - category -- is an index used to select the category corresponding
    to the chosen column (default 0)
    (es: for Traghetto category input category=4).
    - xticks_step -- select the step of the ticks in the x axis of the
    plot (default=3)
    Requires: pandas, numpy, matplotlib.
    """
    data = pd.read_csv(inputfile,
                       sep=';',
                       header=[0, 1], # column MultiIndex with first 2 rows
                       index_col=[0]) # first column as index

    # renaming column MultiIndex
    new_columns = []
    for i in range(len(data.columns)):
        if i % 2 == 0:
            new_columns += (data.columns[i],)
        else:
            new_columns += [(data.columns[i-1][0], data.columns[i][1])]
    data.set_axis(new_columns, axis='columns', inplace=True)

    # Selecting even columns from DataFrame (containing mean values)
    even_col = data[data.columns[0::2]]
    # Selecting odd columns from DataFrame (containing dev.std values)
    odd_col = data[data.columns[1::2]]

    # choosing a column (category) and preparing data into np.arrays
    j_col = category # used on the reduced DataFrame even_col and odd_col
    chosen_col = even_col[even_col.columns[j_col]] # 1 column pandas DataFrame
    x_data = np.array(chosen_col.index)
    y_data = chosen_col.values
    y_errors = odd_col.values[:, j_col]

    # making a plot of chosen column (category)
    # plt.figure()
    # fig, ax = plt.subplots()
    ax = plt.gca()
    spectrum_plt = ax.bar(x_data, y_data, yerr=y_errors, capsize=5)
    # leq_plt = ax.bar(x_data[0], y_data[0], yerr=y_errors[0], capsize=5)
    leq_plt = ax.bar(x_data[0], y_data[0])
    # plt.legend((spectrum_plt, leq_plt),
    #            ('1/3 octave bands', '$L_{Aeq}$ (dB(A))'))
    ax.legend((spectrum_plt, leq_plt),
              ('1/3 octave bands', 'broadband level (dB(A))'))
    plot_title = f'Sound pressure spectrum - category: {chosen_col.name[0]}'
    ax.set_title(plot_title)
    ax.set_xlabel('Frequency bands (Hz)')
    ax.set_ylabel('Sound pressure level (dB)')
    # selecting a subset of ticks for x axes of the plot
    new_xticks = np.arange(0, len(even_col.index)-1, step=xticks_step)
    new_xticks_labels = [even_col.index[new_xticks][i].replace("Hz", "")
                         for i in range(len(new_xticks))]
    ax.set_xticks(new_xticks)
    ax.set_xticklabels(new_xticks_labels)
    
    def autolabel(rects, voffset):
        """Attach a text label above each bar in *rects*,
         displaying its height.
        """
        for i, rect in enumerate(rects):
            height = rect.get_height()
            x = rect.get_x() + rect.get_width() / 2
            y = height + voffset[i]
            ax.annotate('{}'.format(height),
                        xy=(x, y),
                        xytext=(0, 0.5),  # 0.5 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom',
                        weight='bold',
                        size=6.2)

    autolabel(spectrum_plt, y_errors)
    # fig.tight_layout()

    # plt.show()
    # plt.ion(); plt.show()
