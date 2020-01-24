""" Make all spectra plot needed, each in a separated figure and save.
"""
import matplotlib.pyplot as plt
import my_module
import time

input_file = 'power_spectra.csv'
fig_size = (8, 4) # in inches
font_size = 12 # for title, xlabel and ylabel
# label_font_size = 10
ticks_font_size = 9 # for ticks labels

y_limits = (0, 115)
# plt.ion()
for i in range(5):
    plt.figure(figsize=fig_size, dpi=100)
    my_module.spectrum_plot(input_file, i)
    ax = plt.gca()
    plot_title = ax.get_title().replace('pressure', 'power')
    ax.set_title(plot_title, fontweight='bold', fontsize=font_size)
    ax.set_ylabel('$L_{W/m}$ (dB)', fontsize=font_size)
    ax.set_xlabel('Frequency bands (Hz)', fontsize=font_size)
    ax.margins(0.01)
    plt.xticks(fontsize=ticks_font_size)
    plt.yticks(fontsize=ticks_font_size)
    plt.ylim(y_limits)
    plt.tight_layout()
    # plt.legend(fontsize=label_font_size)
    output_file = f'spectrum 0{i+1}.png'
    plt.savefig(output_file)
    plt.show()
    # time.sleep(1)
    # plt.close('all')
# plt.ioff()