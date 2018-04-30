
# coding: utf-8

# In[1]:


from collections import defaultdict, namedtuple,Counter
from datetime import datetime, timedelta
import numpy as np
import csv


# # Criar demanda
# Para criar a demanda preciso criar 3 variáveis
# 1. data_criacao: dia e hora que a demanda entrou no sistema
# 
# 2. NumeroCaso: número de identificação de uma demanda
# 
# Esses são os campos com que o **salesforce** trabalha no sistema FIFO (first in first out)

# In[2]:


np.random.seed(1023)
dia_atual = 28
sortear = lambda x,y:np.random.randint(x,y)
ntuple = namedtuple('demanda',['numerocaso','poder','etapa','data_entrada','data_final'])
demanda = []
add_minutes = 150

for i in range(3000):
    #sortear o dia
    dia = sortear(dia_atual-2,dia_atual+1)

    #sortear a hora
    hora = sortear(8,20)

    #sortear o minuto 
    minuto = sortear(0,60)

    #criar datetime
    data_entrada = datetime(2018,4,dia,hora,minuto,0)
    data_final = datetime(2018,4,dia,hora,minuto,0) + timedelta(minutes = add_minutes)
    
    #criar número do caso
    numerocaso: str = ''.join([str(i) for i in np.random.randint(0,10,size=9)])
    
    #criar o tipo de poder que será utilizado
    poder = 'poderes ' + str(sortear(1,6))
    
    #criar skill que pode tratar da demanda
    etapa = sortear(0,2)
    
    if etapa == 0:
        #está na etapa inicial
        demanda.append(ntuple(numerocaso=numerocaso, 
                              poder=poder, 
                              etapa='etapa {}'.format(1),
                              data_entrada=data_entrada, 
                              data_final=data_final))
    elif etapa == 1:
        #sortear quantas etapas secundárias existem
        n_etapas = np.random.randint(2,6)
        
        for i in range(2,n_etapas+1):
            demanda.append(ntuple(numerocaso=numerocaso,
                                    data_entrada=data_entrada,
                                    etapa = 'etapa {}'.format(i),
                                    data_final = data_final, 
                                    poder = poder))


# # Ordenar
# É necesssário ordenar por hora de entrada para criar a fila FIFO do salesforce

# In[3]:


demanda.sort(key=lambda x:x.data_entrada)


# In[4]:


demanda[0:5]


# # Exportar

# In[5]:


formato = '%Y-%m-%d %H:%M:%S'

with open('demanda.csv','w') as csvfile:
    writer = csv.writer(csvfile, delimiter=',',lineterminator='\n')
    
    writer.writerow(['numerocaso','poder','etapa','data_entrada','data_final'])
    
    for i in demanda:
        writer.writerow([i.numerocaso,i.poder,i.etapa,i.data_entrada.strftime(formato),i.data_final.strftime(formato)])


# # Importar
# As demandas criadas anteriormente são um exemplo de arquivo de entrada a ser importado
# 
# Agora começa o código que será utilizado em produção

# In[6]:


unordered_demanda = []
with open('demanda.csv','r') as csvfile:
    reader = csv.reader(csvfile)
    print('Header: ',next(reader))
    
    for row in reader:
        unordered_demanda.append(row)

unordered_demanda.sort(key=lambda x:x[3])


# # Criar dicionário com as demandas ordenadas

# In[7]:


demanda = defaultdict(list)
for row in unordered_demanda:
    if row[2] == 'etapa 1':
        #se for etapa 1 guarda o poder como demanda
        demanda[row[1]].append(row[0])
    else:
        demanda[row[2]].append(row[0])


# # Criar colaboradores
# 
# Cada grupo tem uma quantidade de pessoas que seguem os mesmos **skills** e **proficiência**.
# A cada momento do planejamento o grupo recebe as demandas pendentes e segue a ordem de proficiência para alocar a quantidade de pessoas disponíveis pelo tempo da tarefa.

# In[8]:


class grupo_trabalho(object):
    
    def __init__(self, n_colaboradores, skills_tma):
        
        #Quantidade de colaboradores nesse grupo
        self.disponiveis = n_colaboradores
        
        #Skills na ordem de proficiência
        self.skills = list(skills_tma.keys())
        
        #guardar minuto de atendimento e qual RD atendida
        self.atendidas = defaultdict(list)
        
        #não existem pessoas ocupadas inicialmente
        self.ocupados = Counter()
        
        #tma de cada skills -- em minutos
        self.tma = skills_tma.copy()
    
    def atendimento(self, minuto, demanda):
        
        #verificar se existem pessoas a serem liberadas
        if minuto in self.ocupados.keys():
            self.disponiveis += self.ocupados[minuto]
            
        #Verificar cada skill -- seguindo ordem de proeficiência
        for skill in self.skills:
            
            #atribuir a rd
            for rd in demanda[skill]:
                #Verificando se existem colaboradores disponíveis e existem demandas para o skill
                if self.disponiveis > 0:
                    
                    #Seguindo o FIFO -- descarto primeiro da lista que foi ordenada previamente
                    #print(skill, demanda[skill].pop(0))
                    
                    #atribuir demanda -- minuto em que a demanda foi passada
                    self.atendidas[minuto].append([rd,skill]) 
                
                    #alocar um pessoa
                    self.disponiveis -= 1
                    
                    #momento em que a pessoa volta a ser ativa
                    self.ocupados[minuto + self.tma[skill]] += 1
                    
    def status(self):
        print('Disponíveis: {}\nOcupados: {} \n'.format(self.disponiveis, self.ocupados))
        
class grupos(grupo_trabalho):
    
    def __init__(self):
        self.grupo = {}
        
    def start_group(self,name,n_colaboradores, skills_tma):
        self.grupo[name] = grupo_trabalho(n_colaboradores=n_colaboradores, skills_tma=skills_tma)
        
    def executar_demandas(self, minutos, demanda):
        
        for minuto in range(1,minutos+1):            
            for key, grupo in self.grupo.items():
                
                #print('grupo: {} minuto: {}'.format(key, minuto))
                grupo.atendimento(minuto, demanda)
    
    def periodo_atendimento(self, current_time):
        
        formato = '%Y-%m-%d %H:%M:%S'
        
        x = lambda minuto: (current_time + timedelta(minutes=minuto)).strftime(formato)
        consolidar = []
        
        for keys, grupo in self.grupo.items():
            for minuto in grupo.atendidas.keys():
                consolidar += [[x(minuto),rd,x(minuto + grupo.tma[skill]), skill] for rd, skill in grupo.atendidas[minuto]]
        
        return consolidar
    
    def exportar_csv(self, filename, current_time):
        
        dataset = grupos.periodo_atendimento(self,current_time)
        
        with open(file=filename, mode='w') as file:
            
            spamwriter = csv.writer(file, delimiter=',',lineterminator='\n')
            
            spamwriter.writerow(['data_inicio','rd','data_fim','skill'])
            
            for ii in dataset:
                spamwriter.writerow(ii)
        


# # Criar grupos de trabalho

# In[9]:


g = grupos()

skills_tma = {'poderes 1':15,'etapa 2':5, 'etapa 3':2, 'etapa 4':3, 'etapa 5':5}
g.start_group('grupo 1', 10, skills_tma)

skills_tma = {'poderes 2':15,'etapa 2':5, 'etapa 3':2, 'etapa 4':3, 'etapa 5':5}
g.start_group('grupo 2', 10, skills_tma)

skills_tma = {'poderes 3':15,'etapa 2':5, 'etapa 3':2, 'etapa 4':3, 'etapa 5':5}
g.start_group('grupo 3', 10, skills_tma)

skills_tma = {'poderes 4':15,'etapa 2':5, 'etapa 3':2, 'etapa 4':3, 'etapa 5':5}
g.start_group('grupo 4', 10, skills_tma)

skills_tma = {'poderes 5':15,'etapa 2':5, 'etapa 3':2, 'etapa 4':3, 'etapa 5':5}
g.start_group('grupo 5', 10, skills_tma)

skills_tma = {'etapa 2':5, 'etapa 3':2, 'etapa 4':3, 'etapa 5':5}
g.start_group('grupo 6', 10, skills_tma)


# # Executar demanda
# Abaixo o código que executa a demanda

# In[12]:


g.executar_demandas(minutos=180,demanda=demanda)


# In[13]:


g.exportar_csv(filename='teste.csv',current_time=datetime(2018,4,6,0,0,0))


# In[ ]:




