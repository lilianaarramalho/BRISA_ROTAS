import pandas as pd

global turnos
global sublancos
global duracoes
global centros_operacionais
global max_visitas



def ler_inputs():

    global turnos
    global sublancos
    global duracoes
    global centros_operacionais
    global max_visitas
    global hora_sublanco
    global carro_1_1_tempo_sub
    global carro_1_2_tempo_sub
    global carro_2_1_tempo_sub
    global carro_2_2_tempo_sub
    global satisfeitos

    df_sublancos = pd.read_csv('dados/01. sublanços.csv', sep=",", encoding='iso-8859-1')
    df_turnos=pd.read_csv('dados/03. turnos.csv',sep=',',encoding='iso-8859-1')

    df_sublancos = df_sublancos.reset_index()
    df_sublancos['id_sublanco'] = df_sublancos.index
    sublancos=[]
    pausas=[]
    almocos=[]
    centros_operacionais=[]
    carro_1_1_tempo_sub=[]
    carro_1_2_tempo_sub = []
    carro_2_1_tempo_sub = []
    carro_2_2_tempo_sub = []
    duracoes=[]
    satisfeitos=[]

    for index,row in df_sublancos.iterrows():
        if row['CO?']==1:
            centros_operacionais.append(row['id_sublanco'])
        if row['Pausa?']==1:
            pausas.append(row['id_sublanco'])
        if row['Almoço?']==1:
            almocos.append(row['id_sublanco'])
        sublancos.append(row['id_sublanco'])
        carro_1_1_tempo_sub.append(3 * 60)
        carro_1_2_tempo_sub.append(3 * 60)
        carro_2_1_tempo_sub.append(3 * 60)
        carro_2_2_tempo_sub.append(3 * 60)
        satisfeitos.append(False)

        duracoes.append(row['Extensão']/(80/60))

    turnos=df_turnos['turno'].tolist()

    return centros_operacionais, sublancos, duracoes,turnos

def main():

    global max_visitas

    centros_operacionais, sublancos, duracoes,turnos = ler_inputs()
    max_visitas = 180
    criar_rotas()

def get_co_proximo(index, sentido):

    global centros_operacionais

    i = 0
    found=False
    if (sentido == "norte"):
        for i in centros_operacionais:
            if (i < index):
                found=True
                return i
    if (sentido == "sul"):
        for i in centros_operacionais:
            if (i > index):
                found = True
                return i
    if found==False:
        return -1


def check_tempo(carro, hora_inicio):

    global max_visitas

    horas_carro = carro.copy()
    for i in range(len(carro)):
        if (horas_carro[i] > max_visitas):
            return False
        duracao = duracoes[carro[i]]
        hora_inicio += duracao
        for j in range(len(carro)):
            horas_carro[j] += duracao
    for i in range(len(carro)):
        if (horas_carro[i] > max_visitas):
            return False
    return True

def check_tempo_sublanco(carro,tempo_sublanco):

    if len(carro)==0:
        return False

    for paragem in carro:
        for pos_sublanco in range(len(tempo_sublanco)):
            if pos_sublanco!=paragem:
                duracao=duracoes[paragem]
                tempo_sublanco[pos_sublanco]=tempo_sublanco[pos_sublanco]-duracao
                if tempo_sublanco[pos_sublanco]<0:
                    return False
            else:
                tempo_sublanco[pos_sublanco]=3*60

    return True

def check_proxima_paragem(carro,paragens_possiveis,hora_paragem,hora_atual):

    if len(carro)==0:
        return False
    ultima_posicao=carro[len(carro)-1]
    hora_min=99
    paragem_min=-1
    for paragem in paragens_possiveis:
        hora=hora_atual
        if paragem>ultima_posicao:
            for posicao in range(ultima_posicao,paragem+1):
                hora+=duracoes[posicao]
            if hora<=hora_paragem and hora<hora_min:
                hora_min=hora
                paragem_min=paragem

        elif paragem<ultima_posicao:
            for posicao in range(ultima_posicao,paragem-1,-1):
                hora+=duracoes[posicao]
            if hora>hora_paragem+60 or hora<hora_paragem-30:
                return False
            else:
                return True
        elif paragem==ultima_posicao:
            if hora>hora_paragem+60 or hora<hora_paragem-60:
                return False
            else:
                return True


def verificar_restricoes(carro_1,carro_1_1_tempo_sub):

    possivel_1=check_tempo_sublanco(carro_1,carro_1_1_tempo_sub)
    possivel_2=check_tempo(carro_1,0)
    if possivel_1==True and possivel_2==True:
        return True
    else:
        return False


def criar_rotas():

    #todo adicionar dar a volta

    global turnos
    global sublancos
    global centros_operacionais
    global max_visitas
    global carro_1_1_tempo_sub
    global carro_1_2_tempo_sub
    global carro_2_1_tempo_sub
    global carro_2_2_tempo_sub
    global satisfeitos

    id_turno = 0
    # Para cada turno

    for id_turno in range(len(turnos)):
        index_anterior_1_norte=-1
        index_1_norte = 0
        index_anterior_2_norte=-1
        index_2_norte=0
        index_anterior_1_sul = -1
        index_1_sul = 0
        index_anterior_2_sul = -1
        index_2_sul = 0
        hora = turnos[id_turno]
        carro_1_norte = []
        carro_2_norte = []
        carro_1_sul = []
        carro_2_sul = []
        possivel=True
        tempo_atual_1=hora
        tempo_atual_2=hora

        while any(satisfeitos)==False:

        # Para cada sublanço

            while possivel==True:

                posto_sul = get_co_proximo(index_1_sul, "sul")
                # Existe carro aberto?
                if len(carro_1_norte) == 0:
                    posto_norte = get_co_proximo(index_1_norte, "norte")
                    if posto_norte>-1:
                        # Se não existir, abrir
                        for pos_sublanço in range(posto_norte,index_1_norte):
                            carro_1_norte.append(pos_sublanço)
                            tempo_atual_1+=duracoes[pos_sublanço]
                            satisfeitos[pos_sublanço]=True

                if len(carro_2)==0 and posto_sul>-1:
                    for pos_sublanço in range(posto_sul, index_, -1):
                        carro_2_1.append(pos_sublanço)
                        tempo_atual_2+=duracoes[pos_sublanço]
                        carro_2_2.append(pos_sublanço)
                        satisfeitos[pos_sublanço] = True

                # Adicionar sublanço a cada carro
                if (len(carro_1_1) > 0):
                    carro_1_1.append(index_1_1)
                    tempo_atual_1+=duracoes[index_1_1]
                    satisfeitos[index_1_1] = True

                if (len(carro_1_2) > 0):
                    carro_1_2.append(index_1_2)
                    satisfeitos[index_1_2] = True

                if (len(carro_2_1) > 0):
                    carro_2_1.append(index_2_1)
                    tempo_atual_2 += duracoes[index_2_1]
                    satisfeitos[index_2_1] = True

                if (len(carro_2_2) > 0):
                    carro_2_2.append(index_2_2)
                    satisfeitos[index_2_2]=True

                # Verificar se entramos em incumprimento de tempo de passagem

                lista_check=[]

                tempo_1 = verificar_restricoes(carro_1_1,carro_1_1_tempo_sub)
                tempo_2 = verificar_restricoes(carro_2_1, carro_2_1_tempo_sub)
                lista_check.append(tempo_1)
                lista_check.append(tempo_2)

                if any(lista_check)==True:
                    possivel=True
                else:
                    possivel=False

                if index>0 and index<(len(sublancos)-1):
                    if index_anterior<index:
                        index_anterior=index
                        index+=1
                    else:
                        index_anterior=index
                        index-=1

                elif index==0:
                    index_anterior=index
                    index+=1

                elif index==len(sublancos)-1:
                    index_anterior=index
                    index-=1

main()

    # for id_turno in range(len(turno)):
    # while index < len(sublanços):
    # se não existirem carros, abrir 2 carros (c01 e c02) que não são do vetor solução, são apenas opções.
    # get_co_norte
    # get_co_sul
    # adicionar ponto inicial ao carro (co)
    # controi rota de intermedio - do sublanço até ao primeiro da sequencia
    # adicionar sublanço ao carro 1 e ao carro 2
    # verifica a que horas passa em cada um dos lanços entre o co e o ponto dos sublanços e atualiza os tempos da ultima hora em que passou no lanço
    # verifica a que horas passa em cada um dos lanços entre o co e o ponto dos sublanços e atualiza os tempos da ultima hora em que passou no lanço
