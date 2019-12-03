import matplotlib.pyplot as plt
import my_module

for i in range(5):
    plt.subplot(3,2,i+1)
    my_module.spectrum_plot('spettri_categorie.csv', i)
plt.show()