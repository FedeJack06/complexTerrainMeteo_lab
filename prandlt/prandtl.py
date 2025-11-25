import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

df = pd.read_csv("DonwslopeDefant.txt", sep="\t", names=["n","u"])
#df = pd.read_csv("UpslopeDefant.txt", sep="\t", names=["n","u"])

# parametri iniziali
theta_0 = 283
gamma = 0.004
alpha = np.deg2rad(42.5)
pr = 0.72
ni = 1.5e-5 #molecolare, assunto laminare
k = 2.24e-5 #assunto laminare

delta_laminare = ( (4*theta_0*ni**2*pr**(-1)) / (9.81*gamma*(np.sin(alpha))**2) )**0.25
print(f"delta_laminare = {delta_laminare:.3f} m")

# ricavano analiticamente: derivo u(n), impongo u'(n_picco) = 0 ==> trovo delta = 4*n_picco/pi
# impongo u(n_picco) = u_max ==> trovo theta_s
def u_prandtl_teor(x, theta_s, delta):
    u_pr = -theta_s * ( ( pr**(-1) * 9.81 )/(theta_0*gamma) )**0.5 * np.exp(-x/delta) * np.sin(x/delta)
    return u_pr

# modello da fittare
def u_prandtl(x, theta_s, ni):
    delta = ( (4*theta_0*ni**2*pr**(-1)) / (9.81*gamma*(np.sin(alpha))**2) )**0.25
    return -theta_s * ( ( pr**(-1) * 9.81 )/(theta_0*gamma) )**0.5 * np.exp(-x/delta) * np.sin(x/delta)

def delta(ni):
    return ( (4*theta_0*ni**2*pr**(-1)) / (9.81*gamma*(np.sin(alpha))**2) )**0.25

par, cov, infodict, mesg, ier = curve_fit(u_prandtl, df["n"], df["u"], full_output=True, bounds=([-3,-np.inf],[3, np.inf]))
errori = np.sqrt(np.diag(cov))
print("_________FIT__________")
print(f"th_s = {par[0]:.3f} ± {errori[0]:.3f} K")
print(f"ni = {par[1]:.3f} ± {errori[1]:.3f} m^2/s")
delta_model = delta(par[1])
print(f"delta = {delta_model:.3f} m")

n = np.linspace(0,130,260)
u_model = u_prandtl(n, par[0], par[1])

plt.figure(1)
plt.plot(u_model, n, label = "fit")
plt.plot(df["u"], df["n"], label="real")
plt.plot(u_prandtl_teor(n, -2, 4*30/np.pi), n, label="model")
plt.legend()
plt.xlabel('u [m/s]')
plt.ylabel('n [m]')
plt.title('')
plt.savefig("down.png", bbox_inches='tight', dpi=300)

#############################################################################################################
############ sensitivity
def u_sens(x, theta_s, slope, gamma, ni):
    delta = ( (4*theta_0*ni**2*pr**(-1)) / (9.81*gamma*(np.sin(np.deg2rad(slope)))**2) )**0.25
    return -theta_s * ( ( pr**(-1) * 9.81 )/(theta_0*gamma) )**0.5 * np.exp(-x/delta) * np.sin(x/delta)

def delta_sens(slope, gamma, ni):
    return ( (4*theta_0*ni**2*pr**(-1)) / (9.81*gamma*(np.sin(np.deg2rad(slope)))**2) )**0.25

def U(theta_s, gamma):
    return -theta_s * ( ( pr**(-1) * 9.81 )/(theta_0*gamma) )**0.5

#####################################
angles =np.linspace(0.1,90,91)
gammas = np.linspace(0.003, 0.01, 10)
thetas = np.linspace(0, 10, 20)

#####################################
delta_fig, ax1 = plt.subplots()
# Plot 1 sull'asse principale
ax1.plot(angles, delta_sens(angles, gamma, par[1]), 'b-', linewidth=2, label=r'$\delta(\alpha)$')
ax1.set_xlabel(r'$\alpha$ [deg]', color='b')
ax1.set_ylabel('$\delta$ [m]')
ax1.tick_params(axis='x', labelcolor='b')

# Crea il secondo asse x (in alto)
ax2 = ax1.twiny()
ax2.plot(gammas, delta_sens(alpha, gammas, par[1]), 'r-', linewidth=2, label=r'$\delta(\gamma)$')
ax2.set_xlabel(r'$\gamma$ [K/m]', color='r')
ax2.tick_params(axis='x', labelcolor='r')

# Crea il terzo asse x (spostato più in alto)
ax3 = ax1.twiny()
ax3.spines['top'].set_position(('outward', 40))
ax3.plot(thetas, [delta_sens(alpha, gamma, par[1])]*20, 'g-', linewidth=2, label=r'$\delta(\theta_s)$')
ax3.set_xlabel(r'$\theta_s$ [K]', color='g')
ax3.tick_params(axis='x', labelcolor='g')

# Aggiungi la legenda
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
lines3, labels3 = ax3.get_legend_handles_labels()
ax1.legend(lines1 + lines2 + lines3, labels1 + labels2 + labels3, loc='best')

ax1.grid(True, alpha=0.3)
#plt.subplots_adjust(top=0.80)

delta_fig.savefig("sens_delta.png", bbox_inches='tight', dpi=300)

#####################################
U_fig, ax1 = plt.subplots()
# Plot 1 sull'asse principale
ax1.plot(angles, [U(par[0], gamma)]*91, 'b-', linewidth=2, label=r'$U(\alpha)$')
ax1.set_xlabel(r'$\alpha$ [deg]', color='b')
ax1.set_ylabel('U [m/s]')
ax1.tick_params(axis='x', labelcolor='b')

# Crea il secondo asse x (in alto)
ax2 = ax1.twiny()
ax2.plot(gammas, U(par[0],gammas), 'r-', linewidth=2, label=r'$U(\gamma)$')
ax2.set_xlabel(r'$\gamma$ [K/m]', color='r')
ax2.tick_params(axis='x', labelcolor='r')

# Crea il terzo asse x (spostato più in alto)
ax3 = ax1.twiny()
ax3.spines['top'].set_position(('outward', 40))
ax3.plot(thetas, U(thetas, gamma), 'g-', linewidth=2, label=r'$U(\theta_s)$')
ax3.set_xlabel(r'$\theta_s$ [K]', color='g')
ax3.tick_params(axis='x', labelcolor='g')

# Aggiungi la legenda
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
lines3, labels3 = ax3.get_legend_handles_labels()
ax1.legend(lines1 + lines2 + lines3, labels1 + labels2 + labels3, loc='best')

ax1.grid(True, alpha=0.3)
#plt.subplots_adjust(top=0.80)

U_fig.savefig("sens_U.png", bbox_inches='tight', dpi=300)

#####################################
plt.figure(4)
alphas = [0.1, 10, 30, 45, 60, 75, 90]
for i, angle in enumerate(alphas):
    plt.plot(u_sens(n, par[0], angle, gamma, par[1]), n, label=str(angle)+" deg")

plt.legend()
plt.xlabel('u [m/s]')
plt.ylabel('n [m]')
plt.title('')
plt.savefig("sens_U_slope.png", bbox_inches='tight', dpi=300)

#####################################
plt.figure(5)
gammas = np.linspace(0.003, 0.01, 7)
for i, gamma in enumerate(gammas):
    plt.plot(u_sens(n, par[0], angle, gamma, par[1]), n, label=str(gamma)+" K/m")

plt.legend()
plt.xlabel('u [m/s]')
plt.ylabel('n [m]')
plt.title('')
plt.savefig("sens_U_gamma.png", bbox_inches='tight', dpi=300)

#####################################
plt.figure(6)
thetas = np.linspace(0, 10, 7)
for i, theta in enumerate(thetas):
    plt.plot(u_sens(n, par[0], angle, gamma, theta), n, label=str(theta)+" K")

plt.legend()
plt.xlabel('u [m/s]')
plt.ylabel('n [m]')
plt.title('')
plt.savefig("sens_U_theta.png", bbox_inches='tight', dpi=300)

plt.tight_layout()
plt.show()

