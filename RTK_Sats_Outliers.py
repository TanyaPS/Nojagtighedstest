"""
Plot af satellitantal for punkter i RTK-målingen i GNSS-nøjagtighedsundersøgelse

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
Find konstanter til outliers
"""
print(('Median af alle differencer: ') + str(statistics.median(df.Difference)))
print(('Median af Hs differencer: ') + str(statistics.median(df[:][(df.Instrument == 'H') & (df.Net == 'H')].Difference)))
print(('Median af Gs differencer: ') + str(statistics.median(df[:][(df.Instrument == 'G') & (df.Net == 'G')].Difference)))

print(('Kvantiler for alle differencer: ') + str(statistics.quantiles(df.Difference, method='inclusive')))
print(('Kvantiler for Hs differencer: ') + str(statistics.quantiles(df[:][(df.Instrument == 'H') & (df.Net == 'H')].Difference, method='inclusive')))
print(('Kvantiler for Gs differencer: ') + str(statistics.quantiles(df[:][(df.Instrument == 'G') & (df.Net == 'G')].Difference, method='inclusive')))

Q1=statistics.quantiles(df.Difference, method='inclusive')[0]
Q3=statistics.quantiles(df.Difference, method='inclusive')[-1]
nedre=Q1-(Q3-Q1)*1.5
oevre=Q3+(Q3-Q1)*1.5

Q1H=statistics.quantiles(df[:][(df.Instrument == 'H') & (df.Net == 'H')].Difference, method='inclusive')[0]
Q3H=statistics.quantiles(df[:][(df.Instrument == 'H') & (df.Net == 'H')].Difference, method='inclusive')[-1]
nedreH=Q1H-(Q3H-Q1H)*1.5
oevreH=Q3H+(Q3H-Q1H)*1.5

Q1G=statistics.quantiles(df[:][(df.Instrument == 'G') & (df.Net == 'G')].Difference, method='inclusive')[0]
Q3G=statistics.quantiles(df[:][(df.Instrument == 'G') & (df.Net == 'G')].Difference, method='inclusive')[-1]
nedreG=Q1G-(Q3G-Q1G)*1.5
oevreG=Q3G+(Q3G-Q1G)*1.5

# Fra Q1 - (Q3-Q1)*1.5  til Q3 + (Q3-Q1)*1.5 (standard for outliers)
print('Interne grænser for alle RTK: Fra ' + str(nedre) + ' til ' + str(oevre))
print('Interne grænser for Hs RTK: Fra ' + str(nedreH) + ' til ' + str(oevreH))
print('Interne grænser for Gs RTK: Fra ' + str(nedreG) + ' til ' + str(oevreG))


"""
Inddeling i kvantiler ift. satellitantal
"""
print('Del ind i satellitter: ' + str(statistics.quantiles(df.Satellitter_gns, n=3, method='inclusive')))


"""
PLOTS
"""

# Satellitantal pr. punkt, farvet efter sektor

df_unik.plot(x='Punkt', y='Satellitter_gns', rot='vertical', c='Sektor', kind='scatter', colormap='plasma').grid(axis='y')
plt.title('Antal satellitter pr. punkt farvelagt efter sektor \n 1: åbent land, 2: lav bebyggelse, 3: høj bebyggelse')
plt.savefig("Figurer/RTK_all_Sats_vs_sektor.png")

# Igen, men diskret farvet, samt figurstørrelse ændret
cmap = mpl.colors.ListedColormap(["navy", "red", "yellow",])
norm = mpl.colors.BoundaryNorm(np.arange(0.5,4.5), cmap.N) 
fig, ax = plt.subplots(figsize=(25,10))
scatter = ax.scatter(x='Punkt', y='Satellitter_gns', c='Sektor', marker='o', data=df_unik,
                cmap=cmap, norm=norm, s=30)

fig.colorbar(scatter, ticks=np.linspace(1,3,3))
plt.xticks(rotation='vertical')
plt.ylabel("Satellitter, gennemsnit")
plt.title('Antal satellitter pr. punkt farvelagt efter sektor \n Blå: åbent land, rød: lav bebyggelse, gul: høj bebyggelse')
plt.savefig("Figurer/RTK_all_Sats_vs_sektor_discrete.png")


# ALLE RTK-målinger (difference), så outliers fremgår tydeligt
df.plot(x='Dato', y='Difference', s=1, kind='scatter').grid(axis='y')
plt.title('Alle RTK-målinger')
plt.xlabel('Dato')
plt.ylabel('Differencer [mm]')
ax = plt.gca()
ax.axes.xaxis.set_ticks([])
plt.savefig("Figurer/RTK_all_outliers_Difference.png")

df[:][(df.Difference >= -420) & (df.Difference <= 420)].plot(x='Dato', y='Difference', s=1, kind='scatter').grid(axis='y', zorder=0)
plt.title('Alle RTK-målinger')
plt.xlabel('Dato')
plt.ylabel('Differencer [mm]')
ax = plt.gca()
ax.axes.xaxis.set_ticks([])
plt.savefig("Figurer/RTK_all_outliers_Difference_zoom.png")

df[:][(df.Difference >= -100) & (df.Difference <= 100)].plot(x='Dato', y='Difference', s=1, kind='scatter').grid(axis='y')
plt.title('Alle RTK-målinger')
plt.xlabel('Dato')
plt.ylabel('Differencer [mm]')
ax = plt.gca()
ax.axes.xaxis.set_ticks([])
plt.savefig("Figurer/RTK_all_outliers_Difference_zoommore.png")


# ALLE RTK-målinger (PDOP), så outliers fremgår tydeligt
df.plot(x='Dato', y='PDOP', s=1, kind='scatter').grid(axis='y')
plt.title('Alle RTK-målinger')
plt.xlabel('Dato')
ax = plt.gca()
ax.axes.xaxis.set_ticks([])
plt.savefig("Figurer/RTK_all_outliers_PDOP.png")

df[:][(df.PDOP >= -1) & (df.PDOP <= 5)].plot(x='Dato', y='PDOP', s=1, kind='scatter').grid(axis='y')
plt.title('Alle RTK-målinger')
plt.xlabel('Dato')
ax = plt.gca()
ax.axes.xaxis.set_ticks([])
plt.savefig("Figurer/RTK_all_outliers_PDOP_zoom.png")

df[:][(df.PDOP >= -1) & (df.PDOP <= 2.5)].plot(x='Dato', y='PDOP', s=1, kind='scatter').grid(axis='y')
plt.title('Alle RTK-målinger')
plt.xlabel('Dato')
ax = plt.gca()
ax.axes.xaxis.set_ticks([])
plt.savefig("Figurer/RTK_all_outliers_PDOP_zoommore.png")

# PDOP vist for alle RTK, hvor difference < 100mm
df[:][(df.Difference >= -100) & (df.Difference <= 100)].plot(x='Dato', y='PDOP', s=1, kind='scatter').grid(axis='y')
plt.title('Alle RTK-målinger \n PDOP-værdier for punkter med difference < 100mm')
plt.xlabel('Dato')
ax = plt.gca()
ax.axes.xaxis.set_ticks([])
plt.savefig("Figurer/RTK_all_outliers_PDOP_Difference.png")

# Difference vist for alle RTK, hvor PDOP < 2,5
df[:][(df.PDOP >= -1) & (df.PDOP <= 2.5)].plot(x='Dato', y='Difference', s=1, kind='scatter').grid(axis='y')
plt.title('Alle RTK-målinger \n Difference for punkter med PDOP < 2,5')
plt.xlabel('Dato')
plt.ylabel('Differencer [mm]')
ax = plt.gca()
ax.axes.xaxis.set_ticks([])
plt.savefig("Figurer/RTK_all_outliers_Difference_PDOP.png")

# Difference som funktion af PDOP
df.plot(x='PDOP', y='Difference', s=1, kind='scatter').grid(axis='y')
plt.title('Alle RTK-målinger')
#plt.xlabel('PDOP')
#ax = plt.gca()
#ax.axes.xaxis.set_ticks([])
plt.savefig("Figurer/RTK_all_outliers_PDOP_vs_Difference.png")


#plt.show()