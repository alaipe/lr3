from pathlib import Path
from parser import parse
from solver import DommelSolver
import numpy

def run(cfg_path:str,n_steps:int):
    A,Y,E,J,components,dt=parse(cfg_path)
    solver=DommelSolver(A,Y,E,J,components,dt)
    print("Матрица A:\n",A.T)
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

def main(n_steps:int):
    tests_dir=Path(__file__).parent / "tests"
    configs=[("r_series.json",n_steps),("r_parallel.json",n_steps),("rc.json",n_steps),("rl.json",n_steps),("rlc_series.json",n_steps)]
    for filename,steps in configs:
        path=str(tests_dir/filename)
        print(f"Тест: {filename}")
        run(path,steps)

'''Задай количество точек!'''
n_steps=100
main(n_steps)