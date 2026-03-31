import json
import numpy
from components.elements import Resistor, Inductor, Capacitor, VoltageSource, CurrentSource

def make_component(cfg:dict, dt:float):
    t=cfg["type"]
    b=cfg["branch"]
    nb=cfg["node_begin"]
    ne=cfg["node_end"]
    if t=="R":
        return Resistor(b,nb,ne,cfg["R"])
    elif t=="L":
        return Inductor(b,nb,ne,cfg["L"],dt)
    elif t=="C":
        return Capacitor(b,nb,ne,cfg["C"],dt)
    elif t=="V":
        return VoltageSource(b,nb,ne,cfg["voltage"],cfg["frequency"],cfg["phase_deg"],cfg["r_internal"])
    elif t=="J":
        return CurrentSource(b,nb,ne,cfg["current"])

def parse(path:str):
    with open(path, "r", encoding="utf-8") as f:
        data=json.load(f)
    dt=float(data["dt"]) #шаг расчета
    n_nodes=int(data["nodes"]) #количество узлов, !включая землю!
    n_free_nodes=n_nodes-1 #количество узлов, !не включая землю!
    components=[] #список элементов
    for element_json in data["elements"]: #для каждого отдельного элемента в json файле
        components.append(make_component(element_json, dt)) #добавить элемент из json в список
    n_branches = len(components) #количество ветвей
    #Матрица инцидентности A (ветви X (узлы-1) т.к. отсчет от 0 в python) столбцы - номер ветви, строки - номер узла
    A=numpy.zeros((n_branches,n_free_nodes),dtype=int) #создает матрицу, заполненную нулями
    for i, element in enumerate(components): #enumerate создает пару счетчик-значение, идем по ветвям i(по каждому элементу из json)
        nb=element.get_node_begin() #значение начального узла для i-го элемента (ветви)
        ne=element.get_node_end() #значение конечного узла для i-го элемента (ветви)
        if nb!=0: #если начальный узел не земля, т.к. земля не входит в A
            A[i,nb-1]=1 #A[ветвь, узел-1]=1, т.к. ветвь направлена из начального узла
        if ne!=0: #если конечный узел не земля, т.к. земля не входит в A
            A[i,ne-1]=-1 #A[ветвь, узел-1]=-1, т.к. ветвь направлена в конечный узел
    #Диагональная матрица проводимостей ветвей Y[branches,branches]
    Y=numpy.zeros((n_branches, n_branches),dtype=float)
    for i,element in enumerate(components):
        Y[i,i]=1/element.get_R()
    #матрица E (+/- задается в json файле в поле напряжения источника!)
    E=numpy.zeros((n_branches,1),dtype=float)
    for i,element in enumerate(components):
        E[i,0]=element.get_E()
    #матрица J (+/- задается в json файле в поле тока источника!)
    J=numpy.zeros((n_branches,1),dtype=float)
    for i,element in enumerate(components):
        J[i,0]=element.get_J()
    return A,Y,E,J,components,dt