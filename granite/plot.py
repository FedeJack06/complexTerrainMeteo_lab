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
print(all.columns)
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
for item in sun_schedule:
   print(f"Giorno: {item['date']} | Sunrise: {item['sunrise_utc']} | Sunset: {item['sunset_utc']}")

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
plt.tight_layout()
plt.savefig("winddir_time.png", bbox_inches='tight', dpi=300)

############################################# select downslope regime
number_of_day = 0 # 3^ giorno su 5
sunset = sun_schedule[number_of_day]['sunset_utc']
sunrise = sun_schedule[number_of_day]['sunrise_utc']
#print("Sunset UTC", sunset)
#print("Sunrise UTC", sunrise)

nighttime_hour = (sunrise - sunset).total_seconds() / 3600
#print("nighttime (h)", nighttime_hour)
hours_start = 10
time_start = sunset + datetime.timedelta(hours=hours_start)
hours_end = 12
time_end = sunset + datetime.timedelta(hours=hours_end)
#print("selected hours (h)", (time_end-time_start).total_seconds() / 3600)

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
plt.tight_layout()
plt.savefig(f"downU_{number_of_day}d_{hours_start}h_{hours_end}h.png", bbox_inches='tight', dpi=300)


############################################# box U(n)
datasetU = [] # [ [0.5 2 5 10 20], [day 2], ...  ] divided by night
for item in sun_schedule:
    list = [] #all levels in one night
    for i in range(5):
        list.append( all[f'wsp_sn{i+1}'][ (all.index > item['sunset_utc']) & (all.index < item['sunrise_utc']) ])
    datasetU.append(list)

all_u_night = [] #[0.5 2 5 10 20] for all night
for i in range(5):
    level_list = [] #all night, one level
    for n_night in range(len(datasetU)):
        level_list.append(datasetU[n_night][i])
    all_u_night.append( pd.concat(level_list, axis=0).sort_index() )#df all night, one level
datasetU.append(all_u_night)

fig, axes = plt.subplots(2,3,figsize=(10,8))
for i, ax in enumerate(axes.flat):
    ax.boxplot(datasetU[i], positions=n, vert=False, widths=0.8, showfliers=False)
    ax.set_ylim(0,22)
    ax.set_xlabel('U [m/s]')
    ax.set_ylabel('n [m]')
    if i == 5:
        ax.set_title('All night')
    else:
        day = sun_schedule[i]['date']
        ax.set_title(f'U(n) for {day} night')
plt.tight_layout()
plt.savefig(f"u_n_box.png", bbox_inches='tight', dpi=300)

############################################# box u'w'
datasetUW = [] # [ [0.5 2 5 10 20], [day 2], ...  ] divided by night
for item in sun_schedule:
    list = [] #all levels in one night
    for i in range(5):
        list.append( all[f'wu_cov_sn{i+1}'][ (all.index > item['sunset_utc']) & (all.index < item['sunrise_utc']) ])
    datasetUW.append(list)

all_u_night = [] #[0.5 2 5 10 20] for all night
for i in range(5):
    level_list = [] #all night, one level
    for n_night in range(len(datasetUW)):
        level_list.append(datasetUW[n_night][i])
    all_u_night.append( pd.concat(level_list, axis=0).sort_index() )#df all night, one level
datasetUW.append(all_u_night)

fig, axes = plt.subplots(2,3,figsize=(10,8))
for i, ax in enumerate(axes.flat):
    ax.boxplot(datasetUW[i], positions=n, vert=False, widths=0.8, showfliers=False)
    ax.axvline(x=0, color='gray', linestyle='--')
    ax.set_ylim(0,22)
    ax.set_xlabel(r"$\overline{u'w'} [m^2/s^{-2}]$")
    ax.set_ylabel('n [m]')
    if i == 5:
        ax.set_title('All night')
    else:
        day = sun_schedule[i]['date']
        ax.set_title(f' {day} night')
plt.tight_layout()
plt.savefig(f"uw_box.png", bbox_inches='tight', dpi=300)

############################################# box Ts'w'
datasetWT = [] # [ [0.5 2 5 10 20], [day 2], ...  ] divided by night
for item in sun_schedule:
    list = [] #all levels in one night
    for i in range(5):
        list.append( all[f'wT_cov_sn{i+1}'][ (all.index > item['sunset_utc']) & (all.index < item['sunrise_utc']) ])
    datasetWT.append(list)

all_u_night = [] #[0.5 2 5 10 20] for all night
for i in range(5):
    level_list = [] #all night, one level
    for n_night in range(len(datasetWT)):
        level_list.append(datasetWT[n_night][i])
    all_u_night.append( pd.concat(level_list, axis=0).sort_index() )#df all night, one level
datasetWT.append(all_u_night)

fig, axes = plt.subplots(2,3,figsize=(10,8))
for i, ax in enumerate(axes.flat):
    ax.boxplot(datasetWT[i], positions=n, vert=False, widths=0.8, showfliers=False)
    ax.axvline(x=0, color='gray', linestyle='--')
    ax.set_ylim(0,22)
    ax.set_xlabel(r"$\overline{w'T_s'} [Kms^{-1}]$")
    ax.set_ylabel('n [m]')
    if i == 5:
        ax.set_title('All night')
    else:
        day = sun_schedule[i]['date']
        ax.set_title(f' {day} night')
plt.tight_layout()
plt.savefig(f"theta_w_box.png", bbox_inches='tight', dpi=300)

############################################# box u'Ts'
datasetUT = [] # [ [0.5 2 5 10 20], [day 2], ...  ] divided by night
for item in sun_schedule:
    list = [] #all levels in one night
    for i in range(5):
        list.append( all[f'uT_cov_sn{i+1}'][ (all.index > item['sunset_utc']) & (all.index < item['sunrise_utc']) ])
    datasetUT.append(list)

all_u_night = [] #[0.5 2 5 10 20] for all night
for i in range(5):
    level_list = [] #all night, one level
    for n_night in range(len(datasetUT)):
        level_list.append(datasetUT[n_night][i])
    all_u_night.append( pd.concat(level_list, axis=0).sort_index() )#df all night, one level
datasetUT.append(all_u_night)

fig, axes = plt.subplots(2,3,figsize=(10,8))
for i, ax in enumerate(axes.flat):
    ax.boxplot(datasetUT[i], positions=n, vert=False, widths=0.8, showfliers=False)
    ax.axvline(x=0, color='gray', linestyle='--')
    ax.set_ylim(0,22)
    ax.set_xlabel(r"$\overline{u'T_s'} [Kms^{-1}]$")
    ax.set_ylabel('n [m]')
    if i == 5:
        ax.set_title('All night')
    else:
        day = sun_schedule[i]['date']
        ax.set_title(f' {day} night')
plt.tight_layout()
plt.savefig(f"theta_u_box.png", bbox_inches='tight', dpi=300)

############################################# box TKE
P = [] # [ [0.5 2 5 10 20], [day 2], ...  ] divided by night
for item in sun_schedule:
    list = [] #all levels in one night
    for i in range(5):
        uT = all[f'uT_cov_sn{i+1}'][ (all.index > item['sunset_utc']) & (all.index < item['sunrise_utc']) ]
        wT = all[f'wT_cov_sn{i+1}'][ (all.index > item['sunset_utc']) & (all.index < item['sunrise_utc']) ]
        list.append( wT*0.998 - uT*0.0627)
    P.append(list)

all_P_night = [] #[0.5 2 5 10 20] for all night
for i in range(5):
    level_list = [] #all night, one level
    for n_night in range(len(P)):
        level_list.append(P[n_night][i])
    all_P_night.append( pd.concat(level_list, axis=0).sort_index() )#df all night, one level
P.append(all_P_night)

plt.figure(figsize=(3,4))
ax = plt.gca()
ax.boxplot(P[i], positions=n, vert=False, widths=0.8, showfliers=False)
ax.axvline(x=0, color='gray', linestyle='--')
ax.set_ylim(0,22)
#ax.set_xlim(0,1)
ax.set_xlabel(r"B $[Kms^{-1}]$")
ax.set_ylabel('n [m]')
ax.set_title('All night')
 
plt.tight_layout()
plt.savefig(f"P_box.png", bbox_inches='tight', dpi=300)

############################################# box TKE
TKE = [] # [ [0.5 2 5 10 20], [day 2], ...  ] divided by night
for item in sun_schedule:
    list = [] #all levels in one night
    for i in range(5):
        u2 = all[f'sigu_cov_sn{i+1}'][ (all.index > item['sunset_utc']) & (all.index < item['sunrise_utc']) ] ** 2
        v2 = all[f'sigv_cov_sn{i+1}'][ (all.index > item['sunset_utc']) & (all.index < item['sunrise_utc']) ] ** 2
        w2 = all[f'sigw_cov_sn{i+1}'][ (all.index > item['sunset_utc']) & (all.index < item['sunrise_utc']) ] ** 2
        list.append( 0.5 * (u2 + v2 + w2) )
    TKE.append(list)

all_TKE_night = [] #[0.5 2 5 10 20] for all night
for i in range(5):
    level_list = [] #all night, one level
    for n_night in range(len(TKE)):
        level_list.append(TKE[n_night][i])
    all_TKE_night.append( pd.concat(level_list, axis=0).sort_index() )#df all night, one level
TKE.append(all_TKE_night)

fig, axes = plt.subplots(2,3,figsize=(10,8))
for i, ax in enumerate(axes.flat):
    ax.boxplot(TKE[i], positions=n, vert=False, widths=0.8, showfliers=False)
    ax.set_ylim(0,22)
    #ax.set_xlim(0,1)
    ax.set_xlabel(r"TKE $[m^2s^{-2}]$")
    ax.set_ylabel('n [m]')
    if i == 5:
        ax.set_title('All night')
    else:
        day = sun_schedule[i]['date']
        ax.set_title(f' {day} night')
plt.tight_layout()
plt.savefig(f"tke_box.png", bbox_inches='tight', dpi=300)

#plt.show()








