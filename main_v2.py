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
    global paragens
    global hora_paragens
    global duracao_paragens

    df_sublancos = pd.read_csv('dados/01. sublanços.csv', sep=",", encoding='iso-8859-1')
    df_turnos = pd.read_csv('dados/03. turnos.csv', sep=',', encoding='iso-8859-1')

    df_sublancos = df_sublancos.reset_index()
    df_sublancos['id_sublanco'] = df_sublancos.index
    sublancos = []
    pausas = []
    almocos = []
    centros_operacionais = []
    carro_1_1_tempo_sub = []
    carro_1_2_tempo_sub = []
    carro_2_1_tempo_sub = []
    carro_2_2_tempo_sub = []
    duracoes = []
    satisfeitos = []

    for index, row in df_sublancos.iterrows():
        if row['CO?'] == 1:
            centros_operacionais.append(row['id_sublanco'])
        if row['Pausa?'] == 1:
            pausas.append(row['id_sublanco'])
        if row['Almoço?'] == 1:
            almocos.append(row['id_sublanco'])
        sublancos.append(row['id_sublanco'])
        carro_1_1_tempo_sub.append(3 * 60)
        carro_1_2_tempo_sub.append(3 * 60)
        carro_2_1_tempo_sub.append(3 * 60)
        carro_2_2_tempo_sub.append(3 * 60)
        satisfeitos.append(False)

        duracoes.append(row['Extensão'] / (80 / 60))

    turnos = df_turnos['turno'].tolist()

    df_paragens=pd.read_csv('dados/04. paragens.csv',sep=',',encoding='ISO-8859-1')

    paragens=df_paragens['paragens'].tolist()
    hora_paragens = df_paragens['hora paragem'].tolist()
    duracao_paragens = df_paragens['tempo paragem'].tolist()

    return centros_operacionais, sublancos, duracoes, turnos


def main():
    global max_visitas

    centros_operacionais, sublancos, duracoes, turnos = ler_inputs()
    max_visitas = 180
    criar_rotas()


def get_co_proximo(index, sentido):
    global centros_operacionais

    i = 0
    found = False
    if (sentido == "norte"):
        for i in centros_operacionais:
            if (i < index):
                found = True
                return i
    if (sentido == "sul"):
        for i in centros_operacionais:
            if (i > index):
                found = True
                return i
    if found == False:
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


def check_tempo_sublanco(carro, tempo_sublanco):
    if len(carro) == 0:
        return False

    for paragem in carro:
        for pos_sublanco in set(carro):
            if pos_sublanco != paragem:
                duracao = duracoes[paragem]
                tempo_sublanco[pos_sublanco] = tempo_sublanco[pos_sublanco] - duracao
                if tempo_sublanco[pos_sublanco] < 0:
                    return False
            else:
                tempo_sublanco[pos_sublanco] = 3 * 60

    return True

def atualizar_index(index,index_anterior):

    global sublancos

    if index > 0 and index < (len(sublancos) - 1):
        if index_anterior < index:
            index_anterior = index
            index += 1
        else:
            index_anterior = index
            index -= 1

    elif index == 0:
        index_anterior = index
        index += 1

    elif index == len(sublancos) - 1:
        index_anterior = index
        index -= 1

    return index,index_anterior

def check_proxima_paragem(carro, paragens_possiveis, hora_paragem, hora_atual):
    if len(carro) == 0:
        return False
    ultima_posicao = carro[len(carro) - 1]
    hora_min = 99
    paragem_min = -1
    for paragem in paragens_possiveis:
        hora = hora_atual
        if paragem > ultima_posicao:
            for posicao in range(ultima_posicao, paragem + 1):
                hora += duracoes[posicao]
            if hora <= hora_paragem and hora < hora_min:
                hora_min = hora
                paragem_min = paragem

        elif paragem < ultima_posicao:
            for posicao in range(ultima_posicao, paragem - 1, -1):
                hora += duracoes[posicao]
            if hora > hora_paragem + 60 or hora < hora_paragem - 30:
                return False
            else:
                return True
        elif paragem == ultima_posicao:
            if hora > hora_paragem + 60 or hora < hora_paragem - 60:
                return False
            else:
                return True


def verificar_restricoes(carro_1, carro_1_1_tempo_sub):
    possivel_1 = check_tempo_sublanco(carro_1, carro_1_1_tempo_sub)
    possivel_2 = check_tempo(carro_1, 0)
    if possivel_1 == True and possivel_2 == True:
        return True
    else:
        return False


def verificar_paragens(carro,tempo_atual):

    global paragens
    global hora_paragens
    global duracao_paragens

    if len(carro)==0:
        return carro

    posicao_atual=carro[len(carro)-1]
    proxima_posicao=-1

    for pos_paragem in range(len(paragens)):

        paragem=paragens[pos_paragem]

        if hora_paragens[pos_paragem]>tempo_atual:

            proxima_posicao=paragem
            hora_paragem=hora_paragens[pos_paragem]
            duracao_paragem=duracao_paragens[pos_paragem]
            break

    if proxima_posicao>=posicao_atual:
        for posicao in range(posicao_atual+1,proxima_posicao+1):
            tempo_atual+=duracoes[posicao]

    else:
        for posicao in range(proxima_posicao+1,posicao_atual):
            tempo_atual+=duracoes[posicao]


    if tempo_atual>hora_paragem+duracao_paragem+45 or proxima_posicao==-1:
        carro=[]

    elif tempo_atual>hora_paragem-30:
        if proxima_posicao >= posicao_atual:
            for posicao in range(posicao_atual + 1, proxima_posicao + 1):
                carro.append(posicao)

        else:
            for posicao in range(proxima_posicao + 1, posicao_atual):
                carro.append(posicao)

    return carro

def criar_rotas():


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
        index_anterior_1 = -1
        index_1 = 0
        index_anterior_2 = -1
        index_2 = 0
        index_anterior_1_sul = -1
        index_1_sul = 0
        index_anterior_2_sul = -1
        index_2_sul = 0
        hora = turnos[id_turno]
        carro_1 = []
        carro_2 = []
        carro_1_sul=[]
        carro_2_sul=[]
        possivel = True
        tempo_atual_1_sul = hora
        tempo_atual_2_sul = hora
        tempo_atual_1_sul = hora
        tempo_atual_2_sul = hora

        while any(satisfeitos) == False:

            # Para cada sublanço
            for pos_satisfeito in range(len(satisfeitos)):
                satisfeito=satisfeitos[pos_satisfeito]
                if satisfeito==False:
                    break
                    index_anterior_1 = -1
                    index_1 = 0
                    index_anterior_2 = -1
                    index_2 = 0

            while possivel == True:

                # Existe carro aberto?
                if len(carro_1) == 0:
                    posto_norte = get_co_proximo(index_1, "norte")
                    if posto_norte > -1:
                        # Se não existir, abrir
                        for pos_sublanço in range(posto_norte, index_1):
                            carro_1.append(pos_sublanço)
                            carro_1_sul.append(pos_sublanço)
                            tempo_atual_1 += duracoes[pos_sublanço]
                            satisfeitos[pos_sublanço] = True

                if len(carro_2) == 0:
                    posto_sul = get_co_proximo(index_2, "sul")

                    for pos_sublanço in range(posto_sul, index_2, -1):
                        carro_2.append(pos_sublanço)
                        carro_2_sul.append(pos_sublanço)
                        tempo_atual_2 += duracoes[pos_sublanço]
                        satisfeitos[pos_sublanço] = True

                # Adicionar sublanço a cada carro
                if (len(carro_1) > 0):
                    carro_1.append(index_1)
                    carro_1_sul.append(index_1)
                    tempo_atual_1 += duracoes[index_1]
                    satisfeitos[index_1] = True

                if (len(carro_2) > 0):
                    carro_2.append(index_2)
                    carro_2_sul.append(index_2)
                    tempo_atual_2 += duracoes[index_2]
                    satisfeitos[index_2] = True

                # Verificar se temos de atender alguma paragem

                carro_1,index_1,index_anterior_1=verificar_paragens(carro_1,tempo_atual_1)
                carro_2,index_2, index_anterior_2=verificar_paragens(carro_2,tempo_atual_2)
                carro_1_sul, index_1_sul, index_anterior_1_sul = verificar_paragens(carro_1_sul, tempo_atual_1_)
                carro_2, index_2, index_anterior_2 = verificar_paragens(carro_2, tempo_atual_2)

                # Verificar se entramos em incumprimento de tempo de passagem

                lista_check = []

                tempo_1 = verificar_restricoes(carro_1, carro_1_1_tempo_sub)
                tempo_2 = verificar_restricoes(carro_2, carro_2_1_tempo_sub)
                lista_check.append(tempo_1)
                lista_check.append(tempo_2)

                if any(lista_check) == True:
                    possivel = True
                else:
                    possivel = False

                index_1,index_anterior_1=atualizar_index(index_1,index_anterior_1)
                index_2, index_anterior_2 = atualizar_index(index_2, index_anterior_2)




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
