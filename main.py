from pathlib import Path #работа с путями к файлам
from parser import parse #мой парсер json файлов и строитель матриц
from solver import DommelSolver #мой решатель
import numpy #матан
import sys
import os
import matplotlib.pyplot as plt #графики

def run(cfg_path:str,n_steps:int): #
    A,Y,E,J,components,dt=parse(cfg_path) #создаем матрицы с помощью парсера
    solver=DommelSolver(A,Y,E,J,components,dt) #создаем объект класса DommelSolver
    print("Матрица A:\n",A.T) #вывод матрицы А
    times = [] #массив меток времени
    currents = [] #массив выдержек токов
    U0s = [] #массив выдержек потенциалов
    for k in range(n_steps):
        U0,I=solver.step() #для заданного t находим потенциалы и ток
        t=solver.get_time() #получаем заданное t
        print(f"t = {t*1000:.2f} мс") #выводим заданное t в мс
        numpy.set_printoptions(formatter={'float': '{: 0.2f}'.format}) #округление до 2 знаков после запятой для U0
        print(f"U0 = {U0.flatten()} В") #напряжение в узлах 1,2,...,n (U0 первого узла всегда равен 10 В, т.к. источник ЭДС)
        numpy.set_printoptions(formatter={'float': '{: 0.5f}'.format}) #округление до 5 знаков после запятой для I
        print(f"I = {I} A") #токи в ветвях
        EDS=[] #массив с добавочным ЭДС в ветвях (замена L/C на E+R)
        for element in components: #проходим по каждому элементу
            EDS.append(element.get_E()) #для каждого элемента получаем E и добавляем в массив
        numpy.set_printoptions(legacy='1.25') #версия 1.25 удаляет из вывода np.float64('число')
        print(f"E = {EDS} В") #добавочное ЭДС для L и C
        times.append(solver.get_time()) #добавляем метку времени в массив
        currents.append(I.copy()) #добавляем выдержку тока в массив
        U0s.append(U0.flatten().copy()) #добавляем выдержку напряжения в массив
    return numpy.array(times), numpy.array(currents), numpy.array(U0s), dt #превращаем в многомерный массив

def main(n_steps:int):
    tests_dir=Path(__file__).parent / "tests" #в переменную tests_dir закидываем строку с путем к родительской папке проекта + (слэш есть суммирование) папка tests
    configs=[("r_series.json",n_steps),("r_parallel.json",n_steps)] #задаем только r_series и r_parallel, для них не строю графики
    for filename,steps in configs: #цикл по названию файла и количеству шагов
        path=str(tests_dir / filename) #путь к папке "tests" + название файла
        print(f"Тест: {filename}") #выводим название теста
        run(path,steps) #запускаем расчет значений

n_steps=int(input('Задай количество точек: '))
main(n_steps) #запускаем расчет

tests_dir = Path(__file__).parent / "tests"

print(f"Тест: rl.json")
t, I, U0, dt = run(str(tests_dir / "rl.json"), n_steps)
#Расчет аналитический для RL цепи
R, L, V = 100, 0.01, 10
tau=L/R #тау L/R
I_ana=(V/R)*(1-numpy.exp(-t/tau)) #I=U/R*(1-e^(-t/tau))
U_R_ana=I_ana*R #U_R=I*R
U_L_ana=V*numpy.exp(-t/tau) #U_L=U*e^(-t/tau)

U_R_sim=U0[:,0]-U0[:,1] #U0[:,0] - берем все строки (время) для 1 узла, U0[:,1] - все строки (время) для 2 узла. U_R=U0_1-U0_2
U_L_sim=U0[:,1] #U0[:,0] - берем все строки (время) для 2 узла. U_R=U0_2-U0_0=U0_2
I_sim=I[:,0] #I[:,0] - токи для первой ветви (источник ЭДС)

fig,axes=plt.subplots(2,1,figsize=(9,7)) #subplots(2 строки (2 графика), 1 колонка, figsize=(размер в дюймах))
#fig - объект фигуры, axes - массив из 2 графиков
fig.suptitle("RL_series: R=100 Ом, L=0.01 Гн, V=10 В",fontsize=13) #suptitle() - заголовок всего объекта

ax=axes[0] #берем первый subplot(график)
ax.set_title("Напряжения (ветви 1 - R, 2 - L)") #заголовок первого графика
ax.plot(t*1e3,U_R_sim,label="U_R(Доммель)",color="blue") #переводим с в мс, выводим напряжение, label - легенда, color - цвет
ax.plot(t*1e3,U_R_ana,"--",label="U_R(аналит)",color="green",alpha=0.5) #"--"-пунктиром, alpha - прозрачность
ax.plot(t*1e3,U_L_sim,label="U_L(Доммель)",color="red")
ax.plot(t*1e3,U_L_ana,"--",label="U_L(аналит)",color="purple",alpha=0.5)
ax.set_xlabel("t, мс") #подпись оси времени
ax.set_ylabel("U, В") #подпись оси напряжений
ax.legend() #выводим легенду
ax.grid(True) #включаем сетку

ax=axes[1] #берем второй subplot(график)
ax.set_title("Ток") #заголовок второго графика
ax.plot(t*1e3,I_sim,label="I(Доммель)",color="green") #переводим с в мс, выводим ток, label - легенда, color - цвет
ax.plot(t*1e3,I_ana,"--",label="I (аналит)",color="purple",alpha=0.5) #"--"-пунктиром, alpha - прозрачность
ax.set_xlabel("t, мс") #подпись оси времени
ax.set_ylabel("I, А") #подпись оси токов
ax.legend() #выводим легенду
ax.grid(True) #включаем сетку

plt.tight_layout() #устраняет наложение элементов
plt.savefig(Path(__file__).resolve().parent/"rl_series.png",dpi=120) #сохраняем в корневой папке проекта, DPI=120 точек на дюйм
plt.close() #закрываем фигуру

print("Тест: rc.json")

t,I,U0,dt=run(str(tests_dir/"rc.json"),n_steps)

R,C,V=1000,0.00001,10
tau=R*C #тау
I_ana=(V/R)*numpy.exp(-t/tau) #I=U/R*exp^(-t/tau)
U_R_ana=I_ana*R #U_R=I*R
U_C_ana=V*(1-numpy.exp(-t/tau)) #U_C=U*(1-exp^(-t/tau))

U_R_sim=U0[:,0]-U0[:,1] #берем все строки для 1 узла, вычитаем все строки для 2 узла
U_C_sim=U0[:,1] #все строки 2го узла
I_sim=I[:,0] #ток в 1 ветви

fig,axes=plt.subplots(2,1,figsize=(9,7)) #создаем объект fig из 2 строк (графиков) и 1 столбца, размер фигуры в дюймах, axes - массив двух графиков
fig.suptitle("RC_series: R=1000 Ом, C=10 мкФ, V=10 В",fontsize=13) #заголовок всего объекта

ax=axes[0] #первый график
ax.set_title("Напряжения (ветви 1 - R, 2 - C)") #заголовок графика
ax.plot(t*1e3,U_R_sim,label="U_R(Доммель)",color="blue") #время в мс, напряжение, label - легенда, color - цвет
ax.plot(t*1e3,U_R_ana,"--",label="U_R (аналит)",color="green",alpha=0.5) #"--" - пунктирная, alpha - прозрачность
ax.plot(t*1e3,U_C_sim,label="U_C(Доммель)",color="red")
ax.plot(t*1e3,U_C_ana,"--",label="U_C (аналит)",color="purple",alpha=0.5)
ax.set_xlabel("t, мс") #подпись оси времени
ax.set_ylabel("U, В") #подпись оси напряжений
ax.legend() #отобразить легенду
ax.grid(True) #отобразить сетку

ax=axes[1]
ax.set_title("Ток")
ax.plot(t*1e3,I_sim,label="I(Доммель)",color="green")
ax.plot(t*1e3,I_ana,"--",label="I(аналит)",color="red",alpha=0.5)
ax.set_xlabel("t, мс")
ax.set_ylabel("I, А")
ax.legend()
ax.grid(True)

plt.tight_layout() #устраняет наложение друг на друга
plt.savefig(Path(__file__).resolve().parent/"rc_series.png",dpi=120) #сохраняем
plt.close() #закрыть обьект

print("Тест: rlc_series.json")

t,I,U0,dt=run(str(tests_dir/"rlc_series.json"),n_steps)

R,L,C,V=10,0.01,0.0001,10
#L*x^2+R*x+(1/C)=0
alpha=R/(2*L) #коэффициент затухания A=R/(2L)
omega0=1/numpy.sqrt(L*C) #собственная частота колебаний без затухания w=1/(LC)**0,5
disc=alpha**2-omega0**2 #alpha**2-omega0**2 -> x1,x2 = -alpha +- (disc)**0,5

if disc<0: #колебательный (затухает слабо)
    omega_d=numpy.sqrt(omega0**2-alpha**2) #корень из -disc
    I_ana=(V/(L*omega_d))*numpy.exp(-alpha*t)*numpy.sin(omega_d*t)
    U_C_ana=V*(1-numpy.exp(-alpha*t)*(numpy.cos(omega_d*t)+(alpha/omega_d)*numpy.sin(omega_d*t)))
elif disc==0: #критический
    I_ana=(V/L)*t*numpy.exp(-alpha*t)
    U_C_ana=V*(1-numpy.exp(-alpha*t)*(1+alpha*t))
else: #апериодический (затухает быстро)
    s1=-alpha+numpy.sqrt(disc)
    s2=-alpha-numpy.sqrt(disc)
    A1=V/(L*(s1-s2))
    A2=-A1
    I_ana=A1*numpy.exp(s1*t)+A2*numpy.exp(s2*t)
    U_C_ana=V+(A1/(C*s1))*numpy.exp(s1*t)+(A2/(C*s2))*numpy.exp(s2*t)

U_R_ana=I_ana*R
U_L_ana=V-U_R_ana-U_C_ana

U_R_sim=U0[:,0]-U0[:,1]
U_L_sim=U0[:,1]-U0[:,2]
U_C_sim=U0[:,2]
I_sim=I[:,0]

fig,axes=plt.subplots(2,1,figsize=(9,7))
fig.suptitle("RLC_series: R=10 Ом, L=0.01 Гн, C=100 мкФ, V=10 В",fontsize=13)

ax=axes[0]
ax.set_title("Напряжения (ветви 1 - R, 2 - L, 3 - C)")
ax.plot(t*1e3,U_R_sim,label="U_R (Доммель)",color="blue")
ax.plot(t*1e3,U_R_ana,"--",label="U_R (аналит)",color="blue",alpha=0.5)
ax.plot(t*1e3,U_L_sim,label="U_L (Доммель)",color="red")
ax.plot(t*1e3,U_L_ana,"--",label="U_L (аналит)",color="red",alpha=0.5)
ax.plot(t*1e3,U_C_sim,label="U_C (Доммель)",color="orange")
ax.plot(t*1e3,U_C_ana,"--",label="U_C (аналит)",color="orange",alpha=0.5)
ax.set_xlabel("t, мс")
ax.set_ylabel("U, В")
ax.legend()
ax.grid(True)

ax=axes[1]
ax.set_title("Ток")
ax.plot(t*1e3,I_sim,label="I (Доммель)",color="green")
ax.plot(t*1e3,I_ana,"--",label="I (аналит.)",color="green",alpha=0.5)
ax.set_xlabel("t, мс")
ax.set_ylabel("I, А")
ax.legend()
ax.grid(True)

plt.tight_layout()
plt.savefig(Path(__file__).resolve().parent/"rlc_series.png",dpi=120)
plt.close()

print("Все графики сохранены.")