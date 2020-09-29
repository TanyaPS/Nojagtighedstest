"""
Plot af satellitantal for punkter i RTK-målingen i GNSS-nøjagtighedsundersøgeles

Kør Clean_GNSS_RTK.py først
Scriptet her læser da fra Cleaned_GNSS_RTK.xlsx
"""
import pyexcel
import pandas as pd
from pandas import DataFrame
import matplotlib.pyplot as plt
import matplotlib as mpl
import statistics
import numpy as np

data = pyexcel.get_sheet(file_name="Cleaned_GNSS_RTK.xlsx", name_columns_by_row=0)

punkt = data.column[1]
dato = data.column[2]
ellipsoidehøjde = data.column[3]
ellipsoidehøjdekvalitet = data.column[4]
meas_num = data.column[5]
instrument = data.column[6]
net = data.column[7]
sektor = data.column[8]
satellitter = data.column[9]
satellitter_gns = data.column[10]
difference = data.column[11]
PDOP = data.column[12]



"""
Indlæsning af data i dataframe
"""

data_dict = {'Punkt': punkt, 'Dato': dato, 'Ellipsoidehøjde': ellipsoidehøjde, 'Ellipsoidehøjdekvalitet': ellipsoidehøjdekvalitet,
             'Måling nr.': meas_num, 'Instrument': instrument, 'Net': net, 'Sektor': sektor, 'Satellitter': satellitter, 
             'Satellitter_gns': satellitter_gns, 'Difference': difference, 'PDOP': PDOP}
df = pd.DataFrame(data_dict, columns = ['Punkt','Dato','Ellipsoidehøjde','Ellipsoidehøjdekvalitet','Måling nr.','Instrument','Net',
                                        'Sektor','Satellitter', 'Satellitter_gns', 'Difference', 'PDOP'])


"""
Opdeling til plot
"""

# Unikke punkter (første forekomst gemt)
df_unik=df.drop_duplicates(subset='Punkt', keep='first').sort_values("Satellitter_gns")
# Erstat sektornavn med integer til plotning i farver
df_unik['Sektor']=df_unik['Sektor'].replace(['bykerne', 'hoej bebyg'], 3)
df_unik['Sektor']=df_unik['Sektor'].replace(['erhverv', 'lav bebyg'], 2)
df_unik['Sektor']=df_unik['Sektor'].replace(['land'], 1)


"""
 PLOTS
"""

# Satellitantal pr. punkt, farvet efter sektor

df_unik.plot(x='Punkt', y='Satellitter_gns', rot='vertical', c='Sektor', kind='scatter', colormap='plasma')
plt.title('Antal satellitter pr. punkt farvelagt efter sektor')
plt.savefig("Figurer/Sats_vs_sektor_all.png")

# Igen, men diskret farvet, samt figurstørrelse ændret
cmap = mpl.colors.ListedColormap(["navy", "red", "yellow",])
norm = mpl.colors.BoundaryNorm(np.arange(0.5,4.5), cmap.N) 
fig, ax = plt.subplots(figsize=(25,10))
scatter = ax.scatter(x='Punkt', y='Satellitter_gns', c='Sektor', marker='o', data=df_unik,
                cmap=cmap, norm=norm, s=30)

fig.colorbar(scatter, ticks=np.linspace(1,3,3))
plt.xticks(rotation='vertical')
plt.ylabel("Satellitter, gennemsnit")
plt.title('Antal satellitter pr. punkt farvelagt efter sektor')
plt.savefig("Figurer/Sats_vs_sektor_all_discrete.png")