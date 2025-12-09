import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from windrose import WindroseAxes
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
    df.insert(0,'date',df.iloc[:,0]+'_'+df.iloc[:,1]+'_'+df.iloc[:,2])    

    df['date'] = pd.to_datetime(df['date'], format='%j_%H_%M', errors='coerce')

    df = df.dropna(subset=['date'])

    df.set_index(df['date'], inplace=True)

    h.append(df)
    #print(df)
    #print(df.index[df.index.duplicated(keep=False)])

all = pd.concat(h, axis=1)
#print(all)

n = [0.5, 2, 5, 10, 20] #asse y plot in cui abbiamo le varie quote


plt.figure(1)
plt.plot([all['wsp_sn1'].iloc[0], all['wsp_sn2'].iloc[0], all['wsp_sn3'].iloc[0], all['wsp_sn4'].iloc[0], all['wsp_sn5'].iloc[0]], n)
plt.show()









