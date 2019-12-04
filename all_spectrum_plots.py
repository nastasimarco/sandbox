""" Make all spectrum plot needed, each in a subplot.
"""
import matplotlib.pyplot as plt
import my_module

plt.figure(figsize=(19, 11), dpi=100)
for i in range(5):
    plt.subplot(3, 2, i+1)
    my_module.spectrum_plot('spettri_categorie.csv', i)
plt.tight_layout()
plt.savefig('all_spectrum.png')
plt.show()
