import pandas as pd

df = pd.read_csv('rds.csv')

#ordenando pelo menor sla
df.sort_values('dia_final',ascending=True, inplace=True)

class grupo_trabalho(object):

    def __init__(self,n_colaboradores,skills):
        self.skills = skills
        self.disponiveis = n_colaboradores
        self.ocupados = {1:0}

    def update(self, minuto, demanda):
        for skill in self.skills:                    
            pass
