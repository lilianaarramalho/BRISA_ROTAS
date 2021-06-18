

import pandas as pd
global turnos
global sublancos
global duracoes
global centros_operacionais

def ler_inputs():

    df_sublancos=pd.read_csv('dados/01. sublanços.csv',sep=",",encoding='iso-8859-1')

    df_cos=df_sublancos[df_sublancos['CO?']==1]
    df_cos=df_cos.reset_index()
    df_cos['id_co'] = df_cos.index

    df_sublancos=df_sublancos[df_sublancos['CO?']==0]
    df_sublancos=df_sublancos.reset_index()
    df_sublancos['id_sublanco']=df_sublancos.index

    centros_operacionais=df_cos['id_co'].tolist()
    sublancos=df_sublancos['id_sublanco'].tolist()
    duracoes = df_sublancos['Extensão']/(80/60)
    duracoes=duracoes.tolist()
    
    return centros_operacionais,sublancos,duracoes

centros_operacionais,sublancos,duracoes=ler_inputs()

def main():

    ler_inputs()
    criar_rotas()


#vetor com as incidencias em cada hora [SUBLANÇO|HORA INICIO]

#vetor com id turno, hora de inicio, hora fim

#Solução: vetor de vetores de sequencia de pontos para cada carro (em que o ponto inicio e fim é o CO)

#vetor com id sublanços e a ultima hora em que lá se passou

def get_co_proximo(index, sentido):
    i = 0
    if(sentido == "norte"):
        for i in centros_operacionais:
            if(i < index): return i
    if(sentido == "sul"):
        for i in centros_operacionais:
            if(i > index): return i

def check_tempo(carro, hora_inicio):

    possivel = False
    for i in range(len(carro)):
        duracao = duracoes[carro[i]]
        hora_inicio += duracao

    return possivel

def criar_rotas():

    id_turno = 0

    #Para cada turno
    for id_turno in range(len(turnos)):
        index = 0
        hora = turnos[id_turno]
        carro_1 = []
        carro_2 = []

        #Para cada sublanço
        while index < len(sublancos):

            #Existe carro aberto?
            if(len(carro_1) == 0 and len(carro_2) == 0):
                #Se não existir, abrir
                posto_norte = get_co_proximo(index, "norte")
                posto_sul = get_co_proximo(index, "sul")
                if(posto_norte > -1): carro_1.append(posto_norte)
                if(posto_sul > -1): carro_2.append(posto_sul)

            #Adicionar sublanço a cada carro
            if(len(carro_1) > 0): carro_1.append(index)
            if(len(carro_2) > 0): carro_2.append(index)

            #Verificar se entramos em incumprimento de tempo de passagem
            possivel_1 = check_tempo(carro_1, hora)
            possivel_2 = check_tempo(carro_2, hora)



    #for id_turno in range(len(turno)):
        #while index < len(sublanços):
            #se não existirem carros, abrir 2 carros (c01 e c02) que não são do vetor solução, são apenas opções.
                #get_co_norte
                #get_co_sul
                #adicionar ponto inicial ao carro (co)

            #controi rota de intermedio - do sublanço até ao primeiro da sequencia
            #adicionar sublanço ao carro 1 e ao carro 2
            #verifica a que horas passa em cada um dos lanços entre o co e o ponto dos sublanços e atualiza os tempos da ultima hora em que passou no lanço
            #verifica a que horas passa em cada um dos lanços entre o co e o ponto dos sublanços e atualiza os tempos da ultima hora em que passou no lanço





