import pandas as pd
import matplotlib.pyplot as plt
import datetime
import matplotlib.patches as mpatches
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import os
from astral.sun import sun
from astral import LocationInfo
from zoneinfo import ZoneInfo

cartella = 'Sonics/'

files = sorted([f for f in os.listdir(cartella) if f.startswith('es') and f.endswith('.csv')])

h = [] #quota dei vari sonici, 0.5, 2, 5, 10, 20

for file in files:
    #print("###################",file)
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
all = pd.concat(h, axis=1).sort_index() #one df with columns' names: *_sn1, *_sn2, *_sn3, *_sn4, *_sn5
if all.index.tz is None:
    all.index = all.index.tz_localize('UTC') # all in UTC
#print(all)
#print(all.columns)
#print("max timestamp",all.date.max())
#print("min timestamp",all.date.min())

################################ find nan
df = all
righe_con_nan = df.isna().any(axis=1)
colonne_con_nan = df.isna().any(axis=0)
risultato = df.loc[righe_con_nan, colonne_con_nan]
#print(risultato)

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
#print(intervalli_nan)
################################################## Sunset Sunrise
lat = 40.09652
lon = -113.25861

#oggetto LocationInfo, città/regione sono opzionali
city = LocationInfo("ES5", "Utah", "America/Denver", lat, lon)
local_tz = ZoneInfo(city.timezone) # "America/Denver"
# tutti i giorni
unique_days = sorted(list(set(all.index.date)))

sun_schedule = []
for day in unique_days:
    s = sun(city.observer, date=day)
    
    #in UTC
    sunrise_utc = s['sunrise'].astimezone(datetime.timezone.utc)
    sunset_utc = s['sunset'].astimezone(datetime.timezone.utc)
    #in local
    sunrise_local = sunrise_utc.astimezone(local_tz)
    sunset_local = sunset_utc.astimezone(local_tz)
    
    sun_schedule.append({
        'date': day,
        'sunrise_utc': sunrise_utc,
        'sunset_utc': sunset_utc,
        'sunrise_local': sunrise_local,
        'sunset_local': sunset_local
    })
#for item in sun_schedule:
    #print(f"Giorno: {item['date']} | Sunrise: {item['sunrise_utc']} | Sunset: {item['sunset_utc']}")

################################################## PLOT

n = [0.5, 2, 5, 10, 20] #asse y plot in cui abbiamo le varie quote
m = ['0.5m', '2m', '5m', '10m', '20m']

fig = plt.figure(1, figsize=(15,5))
for i in range(4,-1,-1): 
    plt.plot(all.index, all[f'truewdir_sn{i+1}'], label=m[i])
for item in sun_schedule:
    plt.axvline(x=item['sunrise_utc'], color='gray', linestyle='--')
    plt.axvline(x=item['sunset_utc'], color='gray', linestyle='--')
    plt.axvspan(xmin=item['sunset_utc'], 
               xmax=item['sunrise_utc'], 
               color='white',  
               alpha=1,           
               zorder=-1)
plt.axhline(y=180, color='gray', linestyle='--', alpha=0.8)
ax = plt.gca()
ax.set_facecolor("lightyellow")
plt.text(x=0.01,              # 1.0 = Bordo destro (0.0 sarebbe sinistro)
        y=180,        
        s=f'$180^\circ$', 
        color='gray',       
        ha='left',         # Allineamento orizzontale (ancorato a destra)
        va='bottom',        # 'bottom' mette il testo SOPRA la linea
        fontsize=10, 
        fontweight='bold',
        transform=ax.get_yaxis_transform()) # Fondamentale con asse X temporale!
plt.axhline(y=270, color='gray', linestyle='--', alpha=0.8)
ax = plt.gca()
plt.text(x=0.01,              # 1.0 = Bordo destro (0.0 sarebbe sinistro)
        y=270,        
        s=f'$270^\circ$', 
        color='gray',       
        ha='left',         # Allineamento orizzontale (ancorato a destra)
        va='bottom',        # 'bottom' mette il testo SOPRA la linea
        fontsize=10, 
        fontweight='bold',
        transform=ax.get_yaxis_transform()) # Fondamentale con asse X temporale!

plt.legend(loc='upper right')
plt.title("True wind direction over time for vertical levels")
plt.xlabel("Date")
plt.ylabel("Wind dir [$^\circ$]")
plt.savefig("winddir_time.png", bbox_inches='tight', dpi=300)

############################################# select downslope regime
number_of_day = 0 # 3^ giorno su 5
sunset = sun_schedule[number_of_day]['sunset_utc']
sunrise = sun_schedule[number_of_day]['sunrise_utc']
print("Sunset UTC", sunset)
print("Sunrise UTC", sunrise)

nighttime_hour = (sunrise - sunset).total_seconds() / 3600
print("nighttime (h)", nighttime_hour)
hours_start = 10
time_start = sunset + datetime.timedelta(hours=hours_start)
hours_end = 12
time_end = sunset + datetime.timedelta(hours=hours_end)
print("selected hours (h)", (time_end-time_start).total_seconds() / 3600)

wdir = all[ (all.index > time_start) & (all.index < time_end) ].copy()  #direzioni di interesse
n_lines = len(wdir)
hours = hours_end - hours_start

plt.figure(2)
ax = plt.gca()
cmap = plt.cm.viridis
for i in range(n_lines):
    fraction = i / (n_lines - 1) if n_lines > 1 else 0 # divido colormap per il numero di grafici da plottare
    c = cmap(fraction)
    U = [wdir['wsp_sn1'].iloc[i], wdir['wsp_sn2'].iloc[i], wdir['wsp_sn3'].iloc[i], wdir['wsp_sn4'].iloc[i], wdir['wsp_sn5'].iloc[i]]
    plt.plot(U, n, color=c)

norm = mcolors.Normalize(vmin=hours_start, vmax=hours_end) # O usa timestamp reali se preferisci
sm = cm.ScalarMappable(cmap=cmap, norm=norm)
cbar = plt.colorbar(sm, ax=ax, label='Time since Sunset [h]')
plt.title(f"Vertical wind speed profile from SS + {hours_start}h to SS + {hours_end}h")
plt.xlabel("U [m/s]")
plt.ylabel("n [m]")
plt.savefig(f"downU_{number_of_day}d_{hours_start}h_{hours_end}h.png", bbox_inches='tight', dpi=300)

#plt.show()








