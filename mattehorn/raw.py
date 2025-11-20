import pandas as pd
import matplotlib.pyplot as plt
plt.rcParams['font.size'] = 22              # dimensione testo di default (titoli, etichette, legende)
plt.rcParams['axes.titlesize'] = 22         # dimensione del titolo degli assi
plt.rcParams['axes.labelsize'] = 22         # dimensione delle etichette degli assi
plt.rcParams['xtick.labelsize'] = 22        # dimensione dei tick sull’asse x
plt.rcParams['ytick.labelsize'] = 22        # dimensione dei tick sull’asse y
plt.rcParams['legend.fontsize'] = 22        # dimensione del testo nella legenda
plt.rcParams['figure.titlesize'] = 22       # dimensione del titolo della figura (fig.suptitle)

#df2 = pd.read_csv("E1349535_01.DAT", header=0, skiprows=[1,2], sep="\t", encoding='ISO-8859-1')
#print(df2)
lista = []
#with open("E1349535_01.DAT", encoding='ISO-8859-1') as f:
with open("ASC_n_01_20130521_2326_2344UTC_2.txt", encoding='ISO-8859-1') as f:
    for line in f:
        l = line.split()
        lista.append(l)
#lista[0].insert(0, "Data")

df = pd.DataFrame(lista[1:],columns=lista[0])
print(df)
df['Speed'] = pd.to_numeric(df["Speed"])
df['Press'] = pd.to_numeric(df["Press"])
df['Alt'] = pd.to_numeric(df["Alt"])
df['PTemp'] = pd.to_numeric(df["PTemp"])

plt.plot(df['Speed'], df['Alt'])
plt.figure()
plt.plot(df['PTemp'], df['Alt'])
#plt.invert_yaxis()
plt.show()
