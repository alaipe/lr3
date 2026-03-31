from components.base import Component
from math import pi, sin

class Resistor(Component):
    def __init__(self,branch,node_begin,node_end,R):
        super().__init__(branch,node_begin,node_end) #вызываем __init__ родительского класса через super()
        self.R=R
    def get_E(self): #Нет ЭДС у резистора
        return 0
    def get_R(self):
        return self.R
    def get_J(self): #Нет источника тока у резистора
        return 0
    def update(self):
        pass #Не нужно, так как резистор
    def __repr__(self):
        return(f"Резистор, ветвь={self.branch}, узлы={self.node_begin}->{self.node_end}, R={self.R} Ом")

class Inductor(Component):
    def __init__(self,branch,node_begin,node_end,L,dt):
        super().__init__(branch,node_begin,node_end) #вызываем __init__ родительского класса через super()
        self.L=L
        self.dt=dt #h=dt!
        self.E_L=0.0
    def get_E(self):
        return self.E_L
    def get_R(self):
        return 2*self.L/self.dt
    def get_J(self):
        return 0
    def update(self):
        G=self.dt/(2*self.L) #G=1/R=dt/(2L)
        U_L=self.fi_begin-self.fi_end #Uln=fi_begin-fi_end
        self.E_L=(2*self.L)/self.dt*self.current+U_L #El=2L/dt*Iln+Uln
    def __repr__(self):
        return (f"Индуктивность, ветвь={self.branch}, узлы={self.node_begin}->{self.node_end}, L={self.L} Гн")

class Capacitor(Component):
    def __init__(self,branch,node_begin,node_end,C,dt):
        super().__init__(branch,node_begin,node_end)
        self.C=C
        self.dt=dt #dt=h
        self.E_C=0.0
    def get_E(self):
        return self.E_C
    def get_R(self):
        return self.dt/(2*self.C)
    def get_J(self):
        return 0
    def update(self):
        G=2*self.C/self.dt #G=1/R=2C/dt
        U_C=self.fi_begin-self.fi_end #UCn=fi_begin-fi_end
        self.E_C=-(self.dt/(2*self.C)*self.current+U_C) #Ec=-(h/(2C)*Icn+Ucn)
    def __repr__(self):
        return (f"Конденсатор, ветвь={self.branch}, узлы={self.node_begin}->{self.node_end}, C={self.C} Ф")

class VoltageSource(Component):
    def __init__(self,branch,node_begin,node_end,voltage,frequency=0,phase_degree=0,r_internal=1e-10):
        super().__init__(branch, node_begin, node_end)
        self.volt=voltage #ЭДС источника
        self.freq=frequency #Частота для переменного источника ЭДС
        self.phase=phase_degree*pi/180 #Фаза в радианах для переменного источника ЭДС
        self.r_int=r_internal #Внутреннее сопротивление источника
        self.time=0 #Время для переменного источника ЭДС
    def get_E(self):
        if self.freq==0:
            v=self.volt
        else:
            v=self.volt*sin(2*pi*self.freq*self.time+self.phase)
        return v
    def get_R(self):
        return self.r_int
    def get_J(self):
        return 0
    def set_time(self,t):
        self.time=t
    def update(self):
        pass
    def __repr__(self):
        return (f"Источник напряжения, ветвь={self.branch}, узлы={self.node_begin}->{self.node_end}, V={self.volt} В")

class CurrentSource(Component):
    def __init__(self,branch,node_begin,node_end,current): #Источник тока не может быть переменным
        super().__init__(branch,node_begin,node_end)
        self.J0=current
    def get_E(self):
        return 0
    def get_R(self):
        return 1e10
    def get_J(self):
        return self.J0
    def update(self):
        pass
    def __repr__(self):
        return (f"Источник тока, ветвь={self.branch}, узлы={self.node_begin}->{self.node_end}, J={self.J0} А")