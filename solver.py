import numpy
from components.elements import VoltageSource

class DommelSolver:
    def __init__(self,A_stored,Y,E,J,components,dt: float):
        self.A=A_stored.copy()
        self.Y=Y #Диагональная матрица проводимостей
        self.E=E #матрица источников ЭДС
        self.J=J  #матрица источников тока
        self.components=components
        self.dt=dt
        self.t=0.0
        self.nb=A_stored.shape[0] #number_branches кол-во ветвей (элементов)
        self.nn=A_stored.shape[1] #number_nodes кол-во узлов
        self.G=self.A.T @ self.Y @ self.A #G=A×Y×A^T, .T - транспонирование numpy, @ - умножение матриц numpy

    def step(self): #один шаг
        self.t+=self.dt
        for element in self.components:
            if isinstance(element, VoltageSource): #проверка принадлежности элементов к источнику ЭДС
                element.set_time(self.t) #выставляем новое время для источников ЭДС
        E=self.E.copy()
        J=self.J.copy()
        for i, element in enumerate(self.components):
            E[i,0]=element.get_E()
            J[i,0]=element.get_J()
        right_side_eq = -self.A.T@(J+self.Y@E) #-A*(J+YE)
        #Решаем СЛАУ: G*U0=right_side_eq
        U0=numpy.linalg.solve(self.G,right_side_eq) #решает A*x=B
        #уравнение ветви: E=R_eq*I+U=>I=Y*(E-U)
        U_branch=self.A@U0 #(nb, 1)
        I_branch=self.Y@(E+U_branch)+J #(nb, 1)
        I_branch=I_branch.flatten() #(nb) #столбец -> список
        U0_flat=U0.flatten() #(nn) #столбец -> список
        #Обновляем fi_begin, fi_end, current
        for i, element in enumerate(self.components):
            nb=element.get_node_begin()
            ne=element.get_node_end()
            element.set_fi_begin(U0_flat[nb-1] if nb!=0 else 0.0)
            element.set_fi_end(U0_flat[ne-1] if ne!=0 else 0.0)
            element.set_current(I_branch[i])
        for element in self.components:
            element.update()
        return U0, I_branch

    def get_time(self) -> float:
        return self.t