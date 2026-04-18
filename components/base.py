from abc import ABC, abstractmethod
class Component(ABC):
    def __init__(self,branch:int,node_begin:int,node_end:int):
        self.branch=branch #ветвь
        self.node_begin=node_begin #из какого узла течет ток
        self.node_end=node_end #в какой узел течет ток
        self.fi_begin=0 #потенциал начального узла
        self.fi_end=0 #потенциал конечного узла
        self.current=0 #ток через ветвь
    @abstractmethod #абстрактный метод - классы-наследники сами должны определить, как данная функция реализуется. причем классы-наследники обязаны определить его, иначе будет ошибка
    def get_E(self)->float:
        pass

    @abstractmethod
    def get_R(self)->float:
        pass

    def set_fi_begin(self,value:float):
        self.fi_begin=value
    def set_fi_end(self,value:float):
        self.fi_end=value
    def set_current(self,value:float):
        self.current=value
    def get_node_begin(self)->int:
        return self.node_begin
    def get_node_end(self)->int:
        return self.node_end
    def get_branch(self)->int:
        return self.branch
    def get_current(self)->float:
        return self.current
    def get_fi_begin(self)->float:
        return self.fi_begin
    def get_fi_end(self)->float:
        return self.fi_end