# import csv

# with open('spettri_categorie.csv') as csvfile:
#      reader = csv.DictReader(csvfile, dialect='excel')
#      for row in reader:
#         print(row, '\n')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# import string

data = pd.read_csv('spettri_categorie.csv',
                     sep=';',
                     header=[0,1], # column MultiIndex with first 2 rows
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
# even_col = data.loc[data.index, [data.columns[2*i] 
#             for i in range(round(len(data.columns)/2))]]
even_col = data[data.columns[0::2]]
# Selecting odd columns from DataFrame (containing dev.std values)
# odd_col = data.loc[data.index, [data.columns[2*i+1] 
#             for i in range(round(len(data.columns)/2)-1)]]
odd_col = data[data.columns[1::2]]

# making a plot of DataFrame even columns
y_errors = odd_col.values
even_col.plot(marker='o') #, yerr=y_errors[:,0], capsize=10)
plt.title('Sound pressure spectrum')
plt.xlabel('Frequency bands (Hz)')
# selecting a subset of ticks for x axes of the plot
new_xticks = np.arange(0, len(even_col.index)-1, step=3)
new_ticks_labels = [even_col.index[new_xticks][i].replace("Hz","")
                        for i in range(len(new_xticks))]
# plt.xticks(new_xticks, even_col.index[new_xticks])
plt.xticks(new_xticks, new_ticks_labels)
plt.ylabel('Sound pressure level (dB)')

plt.show()