""" Make all spectrum plot needed, each in a subplot.
"""
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import my_module

# plt.figure(figsize=(19, 11), dpi=100)
plt.subplot2grid((1, 4), (0,0))
image = mpimg.imread('roro.png')
plt.imshow(image)
plt.axis('off')
plt.subplot2grid((1, 4), (0,1), colspan=3)
category = 0
my_module.spectrum_plot('spettri_categorie.csv', category)
plt.tight_layout()
# plt.savefig('all_spectrum.png')
plt.show()
