import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import matplotlib.patches as mpatches
import os

cartella = 'Sonics/'

files = sorted([f for f in os.listdir(cartella) if f.startswith('es') and f.endswith('.csv')])

h = [] #quota dei vari sonici, 0.5, 2, 5, 10, 20

for file in files:
    lista = []

    with open( cartella+file, encoding='ISO-8859-1') as f:
        for line in f:
            l = line.split(sep=',')
            lista.append(l)
    tipi = [str]*3 + [float]*(len(lista[0])-3) #righe
    dictionary = dict(zip(lista[0],tipi))
    #print(dictionary)
    df = pd.DataFrame(lista[1:],columns=lista[0])
    df = df.astype(dictionary)

    #print(df)
    df.insert(0,'date','2012_'+df.iloc[:,0]+'_'+df.iloc[:,1]+'_'+df.iloc[:,2])    

    df['date'] = pd.to_datetime(df['date'], format='%Y_%j_%H_%M', errors='coerce')

    df = df.dropna(subset=['date'])

    df = df.sort_values(by='date', ignore_index=True)

    df.set_index(df['date'], inplace=True)

    h.append(df)
    #print(df)
    #print(df.index[df.index.duplicated(keep=False)])

all = pd.concat(h, axis=1) #one df with columns' names: *_sn1, *_sn2, *_sn3, *_sn4, *_sn5
#print(all)

################################ find nan
df = all
righe_con_nan = df.isna().any(axis=1)
colonne_con_nan = df.isna().any(axis=0)
risultato = df.loc[righe_con_nan, colonne_con_nan]
print(risultato)

dt = pd.Timedelta('5m')
time_diff = risultato.index.to_series().diff()
is_new_block = time_diff != dt
block_id = is_new_block.cumsum()
intervalli_nan = df.groupby(block_id).apply(
    lambda x: pd.Series({
        'Inizio': x.index[0],
        'Fine': x.index[-1],
        'Numero_Campioni': len(x),
    })
)

print(intervalli_nan)


################################################## PLOT

n = [0.5, 2, 5, 10, 20] #asse y plot in cui abbiamo le varie quote

#decido di prendere in considerazione solo i venti compresi tra SW 235 e NW 315
# perchè i downslope sono circa a W

wdir = all[(all['truewdir_sn1']>260)&(all['truewdir_sn1']<280)].copy()  #direzioni di interesse
#print(wdir)

plt.figure(1)
for i in range(len(wdir)):
    plt.plot([wdir['wsp_sn1'].iloc[i], wdir['wsp_sn2'].iloc[i], wdir['wsp_sn3'].iloc[i], wdir['wsp_sn4'].iloc[i], wdir['wsp_sn5'].iloc[i]], n)
#plt.show()

plt.figure(2)
for i in range(5): 
    #print(i)
    #print(all['date'])
    plt.plot(all.date, all[f'truewdir_sn{i+1}'], label=str(i+1))
    #print(all[f'truewdir_sn{i+1}'])
plt.legend()

plt.figure(3)


plt.show()








