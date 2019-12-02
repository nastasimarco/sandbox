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
even_col = data[data.columns[0::2]]
# Selecting odd columns from DataFrame (containing dev.std values)
odd_col = data[data.columns[1::2]]

# choosing a column (category) and preparing data into np.arrays
j_col = 0 # remember to pick only even columns to have mean values
chosen_col = data[data.columns[j_col]] # 1 column Pandas DataFrame
x_data = np.array(chosen_col.index)
y_data = chosen_col.values
y_errors = odd_col.values[:,j_col]

# making a plot of chosen column (category)
plt.figure()
spectrum_plt = plt.bar(x_data, y_data, yerr=y_errors, capsize=5)
leq_plt = plt.bar(x_data[0], y_data[0], yerr=y_errors[0], capsize=5)
plt.legend((spectrum_plt, leq_plt), ('1/3 octave bands', '$L_{Aeq}$ (dB(A))'))
plot_title = f'Sound pressure spectrum - category: {chosen_col.name[0]}' 
plt.title(plot_title)
plt.xlabel('Frequency bands (Hz)')
plt.ylabel('Sound pressure level (dB)')
# selecting a subset of ticks for x axes of the plot
new_xticks = np.arange(0, len(even_col.index)-1, step=3)
new_ticks_labels = [even_col.index[new_xticks][i].replace("Hz","")
                        for i in range(len(new_xticks))]
plt.xticks(new_xticks, new_ticks_labels)

plt.show()