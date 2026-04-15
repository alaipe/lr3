from pathlib import Path
from parser import parse
from solver import DommelSolver
import numpy
import sys
import os
import matplotlib.pyplot as plt

def run(cfg_path:str,n_steps:int):
    A,Y,E,J,components,dt=parse(cfg_path)
    solver=DommelSolver(A,Y,E,J,components,dt)
    print("Матрица A:\n",A.T)
    times = []
    currents = []
    U0s = []
    for k in range(n_steps):
        U0,I=solver.step()
        t=solver.get_time()
        print(f"t = {t*1000000:.0f} мкс")
        numpy.set_printoptions(formatter={'float': '{: 0.2f}'.format})
        print(f"U0 = {U0.flatten()} В") #напряжение в узлах 1,2,...,n (U0 первого узла всегда равен 10 В, т.к. источник ЭДС)
        numpy.set_printoptions(formatter={'float': '{: 0.5f}'.format})
        print(f"I = {I} A") #токи в ветвях
        EDS=[]
        for element in components:
            EDS.append(element.get_E())
        numpy.set_printoptions(legacy='1.25') #версия 1.25 удаляет из вывода np.float64('число')
        print(f"E = {EDS} В") #добавочное ЭДС для L и C, не считая источник ЭДС в первой ветви
        times.append(solver.get_time())
        currents.append(I.copy())
        U0s.append(U0.flatten().copy())
    return numpy.array(times), numpy.array(currents), numpy.array(U0s), dt

def main(n_steps:int):
    tests_dir=Path(__file__).parent / "tests"
    configs=[("r_series.json",n_steps),("r_parallel.json",n_steps)]
    for filename,steps in configs:
        path=str(tests_dir/filename)
        print(f"Тест: {filename}")
        run(path,steps)

'''Задай количество точек!'''
n_steps=5
main(n_steps)

tests_dir = Path(__file__).parent / "tests"
print(f"Тест: rl.json")
t, I, U0, dt = run(str(tests_dir / "rl.json"), n_steps)

R, L, r_int, V = 100, 0.01, 0.001, 10
R_eff    = R + r_int
tau      = L / R_eff
I_ana    = (V / R_eff) * (1 - numpy.exp(-t / tau))
U_R_ana  = I_ana * R
U_L_ana  = V * (R / R_eff) * numpy.exp(-t / tau)   # L * dI/dt = V*R/R_eff * e^{-t/τ}
U_src_ana = V - I_ana * r_int                     # node 1 voltage

U_src_sim = U0[:, 0]              # fi_1   (branch 0 node voltage)
U_R_sim   = U0[:, 0] - U0[:, 1]  # fi_1 − fi_2  (branch 1)
U_L_sim   = U0[:, 1]             # fi_2   (branch 2)
I_sim     = I[:, 0]

fig, axes = plt.subplots(2, 1, figsize=(9, 7))
fig.suptitle("RL_series: R=100 Ω, L=0.01 Гн, V=10 В", fontsize=13)

ax = axes[0]
ax.set_title("Напряжения (ветви 0, 1, 2)")
ax.plot(t * 1e3, U_src_sim,  label="U_node1 branch 0 (Dommel)", color="purple")
ax.plot(t * 1e3, U_src_ana,  "--", label="U_node1 (аналит.)", color="purple", alpha=0.5)
ax.plot(t * 1e3, U_R_sim,    label="U_R branch 1 (Dommel)", color="blue")
ax.plot(t * 1e3, U_R_ana,    "--", label="U_R (аналит.)", color="blue",   alpha=0.5)
ax.plot(t * 1e3, U_L_sim,    label="U_L branch 2 (Dommel)", color="red")
ax.plot(t * 1e3, U_L_ana,    "--", label="U_L (аналит.)", color="red",    alpha=0.5)
ax.set_xlabel("t, мс")
ax.set_ylabel("U, В")
ax.legend()
ax.grid(True)

ax = axes[1]
ax.set_title("Ток (branch 0)")
ax.plot(t * 1e3, I_sim,  label="I branch 0 (Dommel)", color="green")
ax.plot(t * 1e3, I_ana,  "--", label="I (аналит.)", color="green", alpha=0.5)
ax.set_xlabel("t, мс")
ax.set_ylabel("I, А")
ax.legend()
ax.grid(True)

plt.tight_layout()
plt.savefig(Path(__file__).resolve().parent / "rl_series.png", dpi=120)
plt.close()

print(f"Тест: rc.json")
t, I, U0, dt = run(str(tests_dir / "rc.json"), n_steps)

R, C, r_int, V = 1000, 0.00001, 0.001, 10
R_eff    = R + r_int
tau      = R_eff * C
I_ana    = (V / R_eff) * numpy.exp(-t / tau)
U_R_ana  = I_ana * R
U_C_ana  = V * (1 - numpy.exp(-t / tau)) - I_ana * r_int
U_src_ana = V - I_ana * r_int                     # node 1 voltage

U_src_sim = U0[:, 0]              # fi_1   (branch 0 node voltage)
U_R_sim   = U0[:, 0] - U0[:, 1]  # fi_1 − fi_2  (branch 1)
U_C_sim   = U0[:, 1]             # fi_2   (branch 2)
I_sim     = I[:, 0]

fig, axes = plt.subplots(2, 1, figsize=(9, 7))
fig.suptitle("RC_series: R=1000 Ω, C=10 мкФ, V=10 В", fontsize=13)

ax = axes[0]
ax.set_title("Напряжения (ветви 0, 1, 2)")
ax.plot(t * 1e3, U_src_sim,  label="U_node1 branch 0 (Dommel)", color="purple")
ax.plot(t * 1e3, U_src_ana,  "--", label="U_node1 (аналит.)", color="purple", alpha=0.5)
ax.plot(t * 1e3, U_R_sim,    label="U_R branch 1 (Dommel)", color="blue")
ax.plot(t * 1e3, U_R_ana,    "--", label="U_R (аналит.)", color="blue",   alpha=0.5)
ax.plot(t * 1e3, U_C_sim,    label="U_C branch 2 (Dommel)", color="red")
ax.plot(t * 1e3, U_C_ana,    "--", label="U_C (аналит.)", color="red",    alpha=0.5)
ax.set_xlabel("t, мс")
ax.set_ylabel("U, В")
ax.legend()
ax.grid(True)

ax = axes[1]
ax.set_title("Ток (branch 0)")
ax.plot(t * 1e3, I_sim,  label="I branch 0 (Dommel)", color="green")
ax.plot(t * 1e3, I_ana,  "--", label="I (аналит.)", color="green", alpha=0.5)
ax.set_xlabel("t, мс")
ax.set_ylabel("I, А")
ax.legend()
ax.grid(True)

plt.tight_layout()
plt.savefig(Path(__file__).resolve().parent / "rc_series.png", dpi=120)
plt.close()

print(f"Тест: rlc_series.json")
t, I, U0, dt = run(str(tests_dir / "rlc_series.json"), n_steps)

R, L, C, r_int, V = 10, 0.01, 0.0001, 0.001, 10
R_eff  = R + r_int
alpha  = R_eff / (2 * L)
omega0 = 1.0 / numpy.sqrt(L * C)
disc   = alpha**2 - omega0**2

if disc < 0:
    # Underdamped
    omega_d = numpy.sqrt(omega0**2 - alpha**2)
    I_ana   = (V / (L * omega_d)) * numpy.exp(-alpha * t) * numpy.sin(omega_d * t)
    U_C_ana = V * (1 - numpy.exp(-alpha * t) * (
        numpy.cos(omega_d * t) + (alpha / omega_d) * numpy.sin(omega_d * t)))
elif disc == 0:
    # Critically damped
    I_ana   = (V / L) * t * numpy.exp(-alpha * t)
    U_C_ana = V * (1 - numpy.exp(-alpha * t) * (1 + alpha * t))
else:
    # Overdamped
    s1 = -alpha + numpy.sqrt(disc)
    s2 = -alpha - numpy.sqrt(disc)
    A1 =  V / (L * (s1 - s2))
    A2 = -A1
    I_ana   = A1 * numpy.exp(s1 * t) + A2 * numpy.exp(s2 * t)
    U_C_ana = V + (A1 / (C * s1)) * numpy.exp(s1 * t) + (A2 / (C * s2)) * numpy.exp(s2 * t)

U_R_ana   = I_ana * R
U_L_ana   = V - I_ana * r_int - U_R_ana - U_C_ana
U_src_ana = V - I_ana * r_int                    # node 1 voltage

U_src_sim = U0[:, 0]                             # fi_1          (branch 0 node voltage)
U_R_sim   = U0[:, 0] - U0[:, 1]                 # fi_1 − fi_2   (branch 1)
U_L_sim   = U0[:, 1] - U0[:, 2]                 # fi_2 − fi_3   (branch 2)
U_C_sim   = U0[:, 2]                             # fi_3           (branch 3)
I_sim     = I[:, 0]

fig, axes = plt.subplots(2, 1, figsize=(9, 7))
fig.suptitle("RLC_series: R=10 Ω, L=0.01 Гн, C=100 мкФ, V=10 В", fontsize=13)

ax = axes[0]
ax.set_title("Напряжения (ветви 0, 1, 2, 3)")
ax.plot(t * 1e3, U_src_sim,  label="U_node1 branch 0 (Dommel)", color="purple")
ax.plot(t * 1e3, U_src_ana,  "--", label="U_node1 (аналит.)", color="purple", alpha=0.5)
ax.plot(t * 1e3, U_R_sim,    label="U_R branch 1 (Dommel)", color="blue")
ax.plot(t * 1e3, U_R_ana,    "--", label="U_R (аналит.)", color="blue",   alpha=0.5)
ax.plot(t * 1e3, U_L_sim,    label="U_L branch 2 (Dommel)", color="red")
ax.plot(t * 1e3, U_L_ana,    "--", label="U_L (аналит.)", color="red",    alpha=0.5)
ax.plot(t * 1e3, U_C_sim,    label="U_C branch 3 (Dommel)", color="orange")
ax.plot(t * 1e3, U_C_ana,    "--", label="U_C (аналит.)", color="orange", alpha=0.5)
ax.set_xlabel("t, мс")
ax.set_ylabel("U, В")
ax.legend()
ax.grid(True)

ax = axes[1]
ax.set_title("Ток (branch 0)")
ax.plot(t * 1e3, I_sim,  label="I branch 0 (Dommel)", color="green")
ax.plot(t * 1e3, I_ana,  "--", label="I (аналит.)", color="green", alpha=0.5)
ax.set_xlabel("t, мс")
ax.set_ylabel("I, А")
ax.legend()
ax.grid(True)

plt.tight_layout()
plt.savefig(Path(__file__).resolve().parent / "rlc_series.png", dpi=120)
plt.close()

print("Все графики сохранены.")