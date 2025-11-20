#!~/unibo/atmLab/env1/ python3
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from windrose import WindroseAxes
import matplotlib.patches as mpatches
import os

cartella = "IOP7"
#20may 12:08 UTC sunset 02:42 UTC
#21may 12:07 UTC sunset 02:43 UTC
i = 0
fig1,ax1=plt.subplots(1,3,figsize=(20,12))

fig = plt.figure(figsize=(12, 10))
ax = WindroseAxes.from_ax(fig=fig)
windspeed = []
dir = []

list_time = []
file_list = os.listdir(cartella)
file_list.sort()
for nome_file in file_list:
    percorso_completo = os.path.join(cartella, nome_file)
    if os.path.isfile(percorso_completo):
        print("File:", percorso_completo)
        i += 1

        lista = []
        with open(percorso_completo, encoding='ISO-8859-1') as f:
            for line in f:
                l = line.split()
                lista.append(l)

        timestamp = datetime.strptime(nome_file[20:33],"%Y%m%d_%H%M")
        
        list_time.append(timestamp)
        # A questo punto, trasformiamo la lista in un DataFrame di pandas, con le colonne nominate come nel file originale.
        df = pd.DataFrame(lista[1:],columns=lista[0], dtype='float')
        #print(df.columns)

        if i < 10:
            ax1[0].plot(df.PTemp,df.Alt_mean, color="green")
            ax1[1].plot(df.Dir,df.Alt_mean, color="green")
            ax1[2].plot(df.Speed,df.Alt_mean, color="green")
            for j in df.Speed:
                windspeed.append(j)
            for j in df.Dir:
                dir.append(j)
        elif i < 18:
            ax1[0].plot(df.PTemp,df.Alt_mean, color="orange")
            ax1[1].plot(df.Dir,df.Alt_mean, color="orange")
            ax1[2].plot(df.Speed,df.Alt_mean, color="orange")
        elif i < 26:
            ax1[0].plot(df.PTemp,df.Alt_mean, color="blue")
            ax1[1].plot(df.Dir,df.Alt_mean, color="blue")
            ax1[2].plot(df.Speed,df.Alt_mean, color="blue")
        elif i >= 26:
            print(timestamp)
            ax1[0].plot(df.PTemp,df.Alt_mean, color="red")
            ax1[1].plot(df.Dir,df.Alt_mean, color="red")
            ax1[2].plot(df.Speed,df.Alt_mean, color="red")

ax1[0].set_xlabel("Temperatura potenziale [$^\circ C$]")
ax1[0].set_ylabel("Altezza dal suolo [m]")
ax1[1].set_xlabel("Direzione vento [$^\circ$]")
ax1[1].set_ylabel("Altezza dal suolo [m]")
ax1[2].set_xlabel("Velocità vento [m/s]")
ax1[2].set_ylabel("Altezza dal suolo [m]")
green_patch = mpatches.Patch(color='green', label='Sunset')
orange_patch = mpatches.Patch(color='orange', label='Fresh night')
blue_patch = mpatches.Patch(color='blue', label='Deep night')
red_patch = mpatches.Patch(color='red', label='Sunrise')
ax1[0].legend(handles=[green_patch, orange_patch, blue_patch, red_patch])

ax.bar(dir, windspeed,  
       normed=True, 
       opening=0.8, 
       edgecolor="white",
       bins=[0, 0.5, 1, 1.5, 2, 2.5, 3, 4],  # Equivalenti di 10, 20, 30, 40, 50, 70 km/h
       cmap=plt.cm.viridis)

# Imposta la legenda
ax.set_legend(title="Velocità vento (m/s)", loc='upper left', bbox_to_anchor=(1.05, 1))

plt.tight_layout()
plt.show()