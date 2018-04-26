import pandas as pd
from collections import defaultdict

df = pd.read_csv('rds.csv')
df.sort_values('dia_final', ascending=True, inplace=True)

demanda = defaultdict(list)
for line in df.iterrows():
    demanda[line[1][1]].append(line[1][0])

class grupos(object):
    
    def __init__(self, n_funcionais, skills):
        self.disponiveis = n_funcionais
        self.skills = skills
        self.ocupados = {1:0} #período em que fica livre novamente
        self.tratada = defaultdict(list)
    
    def alocar(self,minuto,tma,demanda):
        
        #existem pessoas que ficam disponíveis nesse minuto
        if minuto in self.ocupados.keys():
            self.disponiveis += self.ocupados[minuto]
        
        #seguindo a ordem dos skills
        for skill in self.skills:
            
            #se existem pessoas e demandas disponíveis
            while len(demanda[skill]) > 0 and self.disponiveis > 0:
                
                #atualizar disponibilidade
                self.disponiveis -= 1
                
                #vai dar erro quando não existir o minuto de destino
                try:
                    self.ocupados[minuto + tma] += 1
                except:
                    self.ocupados[minuto + tma] = 1
                    
                #guardar da demanda tratada
                self.tratada[minuto].append(demanda[skill].pop(0))


g1 = grupos(5,['MODULO 1','MODULO 2'])
g1.alocar(1,1,demanda)
g1.ocupados
demanda

print(g1.alocar(2,1,demanda))
print(g1.ocupados)
print(demanda)
print(g1.tratada)

