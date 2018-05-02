from collections import defaultdict, namedtuple,Counter
from datetime import datetime, timedelta
import numpy as np
import csv

#Importar
#As demandas criadas anteriormente são um exemplo de arquivo de entrada a ser importado
#Agora começa o código que será utilizado em produção
unordered_demanda = []
with open('demanda.csv','r') as csvfile:
    reader = csv.reader(csvfile)
    print('Header: ',next(reader))
    
    for row in reader:
        unordered_demanda.append(row)

unordered_demanda.sort(key=lambda x:x[3])


#Criar dicionário com as demandas ordenadas
demanda = defaultdict(list)
for row in unordered_demanda:
    if row[2] == 'etapa 1':
        #se for etapa 1 guarda o poder como demanda
        demanda[row[1]].append(row[0])
    else:
        demanda[row[2]].append(row[0])


#Criar colaboradores
#Cada grupo tem uma quantidade de pessoas que seguem os mesmos **skills** e **proficiência**.
#A cada momento do planejamento o grupo recebe as demandas pendentes e segue a ordem de proficiência para alocar a quantidade de pessoas disponíveis pelo tempo da tarefa.
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
            for ii, rd in enumerate(demanda[skill]):
                #Verificando se existem colaboradores disponíveis e existem demandas para o skill
                
                if self.disponiveis > 0:
                    
                    #Seguindo o FIFO -- descarto primeiro da lista que foi ordenada previamente
                    #Necessário analisar se é uma etapa de poderes ou conferência para propagar a demanda
                    if skill.startswith('poderes'):
                        aux_demanda = demanda[skill].pop(ii)
                            
                        demanda['etapa 2'].append(aux_demanda)
                        demanda['etapa 3'].append(aux_demanda)
                        demanda['etapa 4'].append(aux_demanda)
                        demanda['etapa 5'].append(aux_demanda)
                        
                    elif skill.startswith('etapa'):
                        demanda[skill].pop(ii)
                        
                    else:
                        print('Cadastro inválido para skill: {}'.format(skill))
                    
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


#Criar grupos de trabalho
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
g.executar_demandas(minutos=2000,demanda=demanda)

#exportar csv
g.exportar_csv(filename='teste.csv',current_time=datetime(2018,4,28,8,0,0))