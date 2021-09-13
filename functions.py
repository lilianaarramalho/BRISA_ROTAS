import pandas as pd
import math
import numpy as np
import random
import itertools
from classes import *
import ast

def ler_arguments():

    global velocidade
    global t_medio_incidencia
    global n_simulacoes
    global tipo_corrida
    global slot_tempo
    global tempo_inicio_turno

    file = open("dados/arguments.txt", "r")

    contents = file.read()

    dictionary = ast.literal_eval(contents)

    file.close()

    velocidade = dictionary.get('velocidade')
    t_medio_incidencia = dictionary.get('t_medio_incidencia')
    n_simulacoes = dictionary.get('n_simulacoes')
    tipo_corrida = dictionary.get('tipo_corrida')
    slot_tempo = dictionary.get('slot_tempo')
    tempo_inicio_turno=dictionary.get('tempo_inicio_turno')

    return velocidade,t_medio_incidencia,n_simulacoes,tipo_corrida,slot_tempo


def import_data():

    global cos
    global sublancos
    global nos
    global turnos
    global satisfeitos
    global incidencias
    global incidencias_visitadas
    global tempos_nos_norte_sul
    global tempos_nos_sul_norte
    global tempos_nos
    global id_nos
    global vistorias
    global probabilidades_turno_1
    global probabilidades_turno_2
    global probabilidades_turno_3



    cos=[]
    sublancos=[]
    nos=[]
    satisfeitos=[]
    incidencias_visitadas=[]
    id_nos=[]

    df_nos=pd.read_csv('dados/01. nos.csv',sep=',',encoding='iso-8859-1')

    lista_nos=df_nos['Nó'].tolist()
    is_co=df_nos['CO?'].tolist()
    is_pausa=df_nos['pausa'].tolist()
    is_almoco=df_nos['almoco'].tolist()
    is_espera=df_nos['espera'].tolist()
    tempos_nos_norte_sul=df_nos['norte-sul'].tolist()
    tempos_nos_sul_norte = df_nos['sul-norte'].tolist()
    tempos_nos = tempos_nos_norte_sul.copy()

    unique_nos = lista_nos.copy()

    for index in range(len(unique_nos)):

        new_no=no(index,unique_nos[index],is_pausa[index],is_almoco[index],is_co[index],is_espera[index],"Nó")
        nos.append(new_no)
        id_nos.append(index)

    #ler distancias

    df_distancias=pd.read_csv('dados/02. distancias.csv',sep=',',encoding='iso-8859-1')
    df_distancias['no in']=df_distancias['Sublanço'].str.split('-').str[0]
    df_distancias['no in'] = df_distancias['no in'].str.rstrip()
    no_in=df_distancias['no in'].tolist()
    kms=df_distancias['kms'].tolist()

    for index in range(len(nos)):

        no_atual = nos[index]

        if index==len(nos)-1:

            no.extensao = 0
            no.tempo = 0

        else:

            for posicao_lista in range(len(no_in)):

                if no_in[posicao_lista] in no_atual.nome:

                    no_atual.extensao = round(kms[posicao_lista])
                    no_atual.tempo = round(60 * kms[posicao_lista] / velocidade)

    # ler turnos

    turnos=[]

    df_turnos=pd.read_csv('dados/03. turnos.csv',sep=",",encoding='iso-8859-1')
    inicio=df_turnos['inicio'].tolist()
    pausa=df_turnos['pausa'].tolist()
    almoco=df_turnos['almoco'].tolist()
    fim=df_turnos['fim'].tolist()

    for index in range(len(inicio)):

        new_turno=turno(index,inicio[index],pausa[index],almoco[index],fim[index])
        turnos.append(new_turno)

    # ler incidencias

    incidencias=[]

    #ler pausas
    ler_pausas()

    #ler áreas de serviço e converter em nós
    df_as=pd.read_csv('dados/05. areas de servico.csv',sep=",",encoding='ISO-8859-1')

    lista_as=df_as['Área de Serviço'].tolist()
    lista_no_in=df_as['Nó Início'].tolist()
    lista_no_out=df_as['Nó Fim'].tolist()
    lista_pausa=df_as['pausa'].tolist()
    lista_almoco=df_as['almoco'].tolist()
    lista_norte_sul=df_as['norte-sul'].tolist()
    lista_sul_norte=df_as['sul-norte'].tolist()
    lista_espera=df_as['espera'].tolist()
    lista_tipo=df_as['Tipo'].tolist()

    # adicionar areas de serviço e portagens
    vistorias=[]

    count=0
    encontrou=False

    for posicao in range(len(lista_as)):

        for posicao_no in range(len(nos)-1):
            no_in=nos[posicao_no]
            no_out=nos[posicao_no+1]

            if no_in.nome==lista_no_in[posicao] and no_out.nome==lista_no_out[posicao]:

                if lista_pausa[posicao]==1:

                    no_in.pausa=1
                    no_out.pausa=1

                if lista_almoco[posicao]==1:

                    no_in.almoco=1
                    no_out.almoco=1

                if lista_espera[posicao]==1:

                    no_in.espera=1
                    no_out.espera=1

                if lista_tipo[posicao]=="Área de Serviço":
                    new_as={'Nome':lista_as[posicao],'Nó Início':no_in.id,'Nó Fim':no_out.id,'Tempo Norte Sul':lista_norte_sul[posicao],'Tempo Sul Norte':lista_sul_norte[posicao]}
                    vistorias.append(new_as)

                encontrou=True

                break

        if encontrou==False:

            for posicao_no in range(len(nos) - 1,0,-1):
                no_in = nos[posicao_no]
                no_out = nos[posicao_no - 1]

                if no_in.nome == lista_no_in[posicao] and no_out.nome == lista_no_out[posicao]:

                    if lista_pausa[posicao] == 1:
                        no_in.pausa = 1
                        no_out.pausa = 1

                    if lista_almoco[posicao] == 1:
                        no_in.almoco = 1
                        no_out.almoco = 1

                    if lista_espera[posicao] == 1:
                        no_in.espera = 1
                        no_out.espera = 1

                    if lista_tipo[posicao] == "Área de Serviço":
                        new_as = {'Nome': lista_as[posicao], 'Nó Início': no_out.id,
                                  'Nó Fim': no_in.id, 'Tempo Norte Sul': lista_norte_sul[posicao],
                                  'Tempo Sul Norte': lista_sul_norte[posicao]}
                        vistorias.append(new_as)

        encontrou = False

    count=0

    for new_no in nos:
        new_no.id=count
        count+=1

    for no_atual in nos:

        no_atual.distancias = [0] * len(nos)
        no_atual.kms = [0] * len(nos)

    for index in range(len(nos)):

        no_atual = nos[index]

        if no_atual.tipo=="Nó":

            acumulado_tempo = 0
            acumulado_kms = 0

            for index2 in range(len(nos)):

                no2=nos[index2]

                if no_atual==no2:
                    acumulado_tempo=0
                    acumulado_kms=0
                elif no_atual.id>no2.id:
                    acumulado_tempo=no2.distancias[index]
                    acumulado_kms=no2.kms[index]
                else:
                    acumulado_tempo+=nos[index2-1].tempo
                    acumulado_kms+=nos[index2-1].extensao

                no_atual.kms[index2]=acumulado_kms

                no_atual.distancias[index2] = acumulado_tempo

        else:

            no_atual.distancias=nos[index-1].distancias.copy()
            no_atual.kms=nos[index-1].kms.copy()

    satisfeitos=[[False] * len(nos)] * len(turnos)



    probabilidades_turno_1 = [0] * len(sublancos)
    probabilidades_turno_2 = [0] * len(sublancos)
    probabilidades_turno_3 = [0] * len(sublancos)


    df_probabilidades = pd.read_csv('dados/probabilidades com zeros.csv', sep=",", encoding='iso-8859-1')
    df_probabilidades['Probabilidade incidência'] = df_probabilidades['Probabilidade incidência'].replace("%", "",
                                                                                                          regex=True).astype(
        float) / 100

    lista_probabilidades = df_probabilidades['Probabilidade incidência'].tolist()
    lista_hora = df_probabilidades['Hora'].tolist()
    lista_sublanco = df_probabilidades['Sublanço'].tolist()

    id_turno = 0
    id_sublanco = 0



    #Calcular probabilidade agregada por tuno por cada sublanço
    for i in range(len(lista_probabilidades)):

        #Descobrir a que turno diz respeito
        for j in range(len(turnos)):
            if lista_hora[i]*60-tempo_inicio_turno*60 < turnos[j].fim:
                id_turno = j

        #Descobrir qual o sublanço
        for j in range(len(nos)):
            no_fim = lista_sublanco[i].split('-')[1]
            no_fim = no_fim.strip()
            if(no_fim in nos[j].nome):
                id_sublanco = j

        try:
            if(id_turno == 0):
                probabilidades_turno_1[id_sublanco] += lista_probabilidades[i]
            elif (id_turno == 1):
                probabilidades_turno_2[id_sublanco] += lista_probabilidades[i]
            else:
                probabilidades_turno_3[id_sublanco] += lista_probabilidades[i]
        except:
            print('.') #TODO isto nunca devia vir para o except


    return nos,turnos

def get_distance(x,y):

    min_dist=999999

    if nos[x].distancias[y]<min_dist:
        min_dist=nos[x].distancias[y]

    if nos[y].distancias[x] < min_dist:
        min_dist = nos[y].distancias[x]

    # if min_dist==0:
    #     min_dist=2

    return int(min_dist)

def gerar_combinacoes(lista_sublancos,min_comb,range_combinacoes):

    global vetor_solucao

    indices_a_manter = []
    for posicao in range(len(incidencias_visitadas)):
        if incidencias_visitadas[posicao] == False:
            indices_a_manter.append(posicao)

    if min_comb==0:
        temp_incidencias = indices_a_manter.copy()
        min_sublanco = min(lista_sublancos)
        max_sublanco = max(lista_sublancos)
        max_diferenca = range_combinacoes
        for posicao_incidencia in indices_a_manter:
            if min_sublanco - max_diferenca > incidencias[posicao_incidencia][0] or max_sublanco + max_diferenca < incidencias[posicao_incidencia][0]:
                temp_incidencias.remove(posicao_incidencia)
        indices_a_manter=temp_incidencias.copy()

    def printCombination(arr, n, r):
        # A temporary array to
        # store all combination
        # one by one
        data = [0] * r;

        vetor_solucao=combinationUtil(arr, data, 0,
                        n - 1, 0, r);

        return vetor_solucao

    def combinationUtil(arr, data, start,
                        end, index, r):
        # Current combination is ready
        # to be printed, print it
        vetor_solucao=[]
        if (index == r):
            for j in range(r):
                vetor_solucao.append(data[j])
            combinacoes.append(vetor_solucao)
            return vetor_solucao,indices_a_manter
        i = start;
        while (i <= end and end - i + 1 >= r - index):
            data[index] = arr[i];
            combinationUtil(arr, data, i + 1,
                            end, index + 1, r);
            i += 1;

        return combinacoes,indices_a_manter

    for i in range(min_comb,len(indices_a_manter)+1):
        printCombination(indices_a_manter, len(indices_a_manter), i)

def get_next_posicao(vetor_posicoes,lista_sublancos):

    if len(lista_sublancos)==1 or len(vetor_posicoes)==0:
        nova_posicao=lista_sublancos[0]

    else:
        posicao_atual=vetor_posicoes[-1].get('posicao')

        if len(vetor_posicoes)==1:
            posicao_anterior=min(lista_sublancos)
        else:
            posicao_anterior=vetor_posicoes[-2].get('posicao')

        if posicao_atual==min(lista_sublancos):
            if posicao_anterior!=min(lista_sublancos):
                nova_posicao=min(lista_sublancos)
            else:
                nova_posicao=min(lista_sublancos)+1

        elif posicao_atual==max(lista_sublancos):
            if posicao_anterior!=max(lista_sublancos):
                nova_posicao=max(lista_sublancos)
            else:
                nova_posicao=max(lista_sublancos)-1

        else:
            if posicao_anterior>posicao_atual:
                nova_posicao=posicao_atual-1
            else:
                nova_posicao=posicao_atual+1

    return nova_posicao

def atualizar_vetor(id_posicao,id_turno,vetor_passos,tempo_adicional,tipo):

    anterior=0

    tipo_anterior="none"

    if len(vetor_passos)>0:

        try:

            posicao_anterior=vetor_passos[-1].get('posicao')

        except:

            print(vetor_passos)

        hora_fim_atual=get_distance(posicao_anterior,id_posicao)

        anterior=vetor_passos[-1].get('Hora Fim')

        tipo_anterior = vetor_passos[-1].get('Tipo')

        deslocacao=nos[id_posicao].kms[posicao_anterior]

    else:

        hora_fim_atual=turnos[id_turno].inicio
        deslocacao=nos[id_posicao].extensao

    new_row = { 'posicao': id_posicao, 'Hora Inicio': hora_fim_atual + anterior,
               'Hora Fim': hora_fim_atual + anterior + tempo_adicional, 'Tipo': tipo,'Deslocação':deslocacao}

    vetor_passos.append(new_row)

    return vetor_passos

def visitar_no(id_no,passos,posicao,tempo_no,tipo,id_ocorrencia):


    new_row={'posicao':id_no,'Hora Inicio':passos[posicao].get('Hora Fim'),'Hora Fim':tempo_no+passos[posicao].get('Hora Fim'),'Tipo':tipo,'id_pausa':id_ocorrencia}
    passos.insert(posicao,new_row)
    if posicao==0:
        dif_inicial = tempo_no
    else:
        dif_inicial= passos[posicao].get('Hora Inicio') - passos[posicao-1].get('Hora Fim')+tempo_no

    index=posicao+1

    while index< len(passos):
        try:
            id_pausa=passos[index].get('id_pausa')
        except:
            id_pausa=-1

        new_row = {'posicao': passos[index].get('posicao'), 'Hora Inicio': passos[index].get('Hora Inicio') + dif_inicial,
               'Hora Fim': passos[index].get('Hora Fim')+dif_inicial, 'Tipo': passos[index].get('Tipo'),'id_pausa':id_pausa}
        passos[index] = new_row
        index+=1

    count=0
    for index in range(len(passos)):
        if passos[index].get('Tipo')=='Visitar Nó':
            count+=1

    return passos,count

def adicionar_posicao(id_posicao,tipo_deslocacao,vetor_passos,vetor_sublancos,id_turno):

    tempo_adicional=0

    if tipo_deslocacao=='Pausa':
        tempo_adicional=10
    elif tipo_deslocacao=='Almoço':
        tempo_adicional = 30
    elif tipo_deslocacao=='Visitar Nó':
        tempo_adicional = 10
    elif tipo_deslocacao=='Vistoria':
        tempo_adicional = 10
    elif tipo_deslocacao == 'Incidência':
        tempo_adicional = 30

    if id_posicao==-1:

        nova_posicao=get_next_posicao(vetor_sublancos)

        if nova_posicao not in vetor_sublancos:
            if nova_posicao>max(vetor_sublancos):
                nova_posicao=max(vetor_sublancos)
            else:
                nova_posicao = min(vetor_sublancos)
    else:

        nova_posicao=id_posicao

    vetor_passos=atualizar_vetor(nova_posicao,id_turno,vetor_passos,tempo_adicional,tipo_deslocacao)

    return vetor_passos

def get_tempo_atualizado(posicao_inicial,posicao_final):

    tempo=0

    if posicao_final!=-1:

        if posicao_inicial<=posicao_final:
            for posicao in range(posicao_inicial,posicao_final):
                tempo+=get_distance(posicao,posicao+1)
        else:
            for posicao in range(posicao_inicial,posicao_final,-1):
                tempo+=get_distance(posicao,posicao-1)

    return int(tempo)

def verificar_npausas(new_tempo_paragens):
    n_pausas = 0
    n_almocos = 0
    n_fim = 0

    for index in range(len(new_tempo_paragens)):
        if new_tempo_paragens[index].get('Tipo') == 'Pausa':
            n_pausas += 1
        if new_tempo_paragens[index].get('Tipo') == 'Almoço':
            n_almocos += 1
        if new_tempo_paragens[index].get('Tipo') == 'Fim':
            n_fim += 1

    return n_pausas,n_almocos,n_fim

def precisa_paragem(lista_sublancos,new_rota,new_tempo_paragens,id_turno):

    pausa = turnos[id_turno].pausa
    almoco = turnos[id_turno].almoco
    fim = turnos[id_turno].fim
    tipo_paragem='Pausa'

    posicao_atual=new_tempo_paragens[-1].get('posicao')
    tempo_fim=get_distance(posicao_atual,new_rota[0])

    tempo=new_tempo_paragens[-1].get('Hora Fim')

    n_pausas = 0
    n_almocos = 0
    n_fim = 0
    tempo_a_verificar=0

    for index in range(len(new_tempo_paragens)):
        if new_tempo_paragens[index].get('Tipo') == 'Pausa':
            n_pausas += 1
        if new_tempo_paragens[index].get('Tipo') == 'Almoço':
            n_almocos += 1
        if new_tempo_paragens[index].get('Tipo') == 'Fim':
            n_fim += 1

    posicao_objetivo = -1

    if len(new_rota) > 0:
        posicao_atual = new_rota[-1]
        posicao_objetivo = -1
        diferenca_min = 999


        if pausa-tempo<= 45 and n_pausas==0 :
            tempo_a_verificar = pausa-tempo
            tipo_paragem='Pausa'
            for id_no in lista_sublancos:
                no=nos[id_no]
                if no.pausa == 1:
                    diferenca = get_distance(id_no, posicao_atual)
                    if diferenca < diferenca_min:
                        posicao_objetivo = id_no
                        diferenca_min = diferenca
            if posicao_objetivo==-1:
                for id_no in id_nos:
                    if nos[id_no].pausa == 1 and id_no not in lista_sublancos:
                        diferenca = get_distance(id_no, posicao_atual)
                        if diferenca < diferenca_min:
                            posicao_objetivo = id_no
                            diferenca_min = diferenca

        elif almoco-tempo<=45 and n_almocos == 0:
            tempo_a_verificar = almoco-tempo
            tipo_paragem = 'Almoço'
            for id_no in lista_sublancos:
                no = nos[id_no]
                if no.almoco == 1:
                    diferenca = get_distance(id_no, posicao_atual)
                    if diferenca < diferenca_min:
                        posicao_objetivo = id_no
                        diferenca_min = diferenca
            if posicao_objetivo == -1:
                for id_no in id_nos:
                    no = nos[id_no]
                    if no.almoco == 1 and id_no not in lista_sublancos:
                        diferenca = get_distance(id_no, posicao_atual)
                        if diferenca < diferenca_min:
                            posicao_objetivo =id_no
                            diferenca_min = diferenca

    return posicao_objetivo,tipo_paragem,new_rota,new_tempo_paragens,tempo_a_verificar

def threshold(new_tempo_paragens,lista_sublancos):

    tempo_visita=[resposta]*len(nos)

    posicao_atual=new_tempo_paragens[-1].get('posicao')
    tempo_atual=new_tempo_paragens[-1].get('Hora Fim')

    criticos=[]

    for posicao in range(1,len(new_tempo_paragens)):

        id_posicao= new_tempo_paragens[posicao].get('posicao')

        tempo_anterior=new_tempo_paragens[posicao-1].get('Hora Fim')
        tempo_atual = new_tempo_paragens[posicao].get('Hora Fim')

        tempo_retirar=tempo_atual-tempo_anterior

        for index in range(len(tempo_visita)):

            if index==id_posicao:
                tempo_visita[index]=resposta
            elif index in lista_sublancos:
                tempo_visita[index]=tempo_visita[index]-tempo_retirar

    max_dif = -1
    id_max_dif=-1

    for posicao in range(len(tempo_visita)):
        tempo_adicionar=get_tempo_atualizado(posicao_atual,posicao)
        if tempo_visita[posicao]-tempo_adicionar<10:
            criticos.append(posicao)
            if tempo_visita[posicao]-tempo_adicionar>max_dif:
                max_dif = tempo_visita[posicao]-tempo_adicionar
                id_max_dif = posicao

    return id_max_dif

def go_to(id_paragem,lista_sublancos,tipo_paragem,new_tempo_paragens,id_turno):

    posicao_inicial=new_tempo_paragens[-1].get('posicao')

    if posicao_inicial <= id_paragem:
        for posicao in range(posicao_inicial, id_paragem+1):
            if posicao==id_paragem:
                new_tempo_paragens= adicionar_posicao(posicao,tipo_paragem,new_tempo_paragens,lista_sublancos,id_turno)
            else:
                new_tempo_paragens = adicionar_posicao(posicao, "Deslocação", new_tempo_paragens,
                                                                 lista_sublancos, id_turno)
    else:
        for posicao in range(posicao_inicial, id_paragem-1, -1):
            tempo = get_distance(posicao, posicao - 1)
            if posicao==id_paragem:
                new_tempo_paragens=adicionar_posicao(posicao,tipo_paragem,new_tempo_paragens,lista_sublancos,id_turno)
            else:
                new_tempo_paragens = adicionar_posicao(posicao, "Deslocação", new_tempo_paragens,
                                                                 lista_sublancos, id_turno)

    return new_tempo_paragens

def verificar_ultima_paragem(lista_sublancos,new_rota,new_tempo_paragens,id_turno):

    id_paragem, tipo_paragem, new_rota, new_tempo_paragens,tempo_a_verificar_1 = precisa_paragem(lista_sublancos, new_rota,
                                                                             new_tempo_paragens, id_turno)
    temp_rota=new_rota.copy()
    temp_tempos=new_tempo_paragens.copy()
    temp_rota, temp_paragens = adicionar_posicao(-1, "Deslocação", temp_rota, temp_tempos, lista_sublancos,
                                                 id_turno)
    temp_posicao_objetivo, temp_tipo_paragem, temp_new_rota, temp_new_tempo_paragens,tempo_a_verificar_2 = precisa_paragem(lista_sublancos,
                                                                                                       temp_rota,
                                                                                                       temp_paragens,
                                                                                               id_turno)

    if temp_posicao_objetivo != -1 and temp_tipo_paragem == tipo_paragem and tempo_a_verificar_1>0:
        id_paragem = -1

    return id_paragem,tipo_paragem

def verificar_ultima_incidencia(incidencias_a_considerar, new_rota, new_tempo_paragens, new_visitas, id_turno):

    id_incidencia,posicao_incidencia = precisa_incidencia(incidencias_a_considerar, new_rota, new_tempo_paragens, new_visitas, id_turno)

    temp_rota = new_rota.copy()
    temp_tempos = new_tempo_paragens.copy()

    temp_rota, temp_paragens = adicionar_posicao(-1, "Deslocação", temp_rota, temp_tempos, lista_sublancos,
                                                 id_turno)
    temp_rota, temp_paragens = adicionar_posicao(-1, "Deslocação", temp_rota, temp_tempos, lista_sublancos,
                                                 id_turno)
    temp_id_incidencia,temp_posicao_incidencia = precisa_incidencia(incidencias_a_considerar, temp_rota, temp_paragens, new_visitas, id_turno)

    if temp_id_incidencia == id_incidencia:
        id_incidencia = -1

    return id_incidencia,posicao_incidencia

def precisa_incidencia(incidencias_a_considerar,new_rota,new_tempo_paragens,new_visitas,id_turno):

    tempo_atual=new_tempo_paragens[-1].get('Hora Fim')
    tempo_total=tempo_atual
    tempo_resposta=0
    posicao_atual=new_tempo_paragens[-1].get('posicao')

    id_incidencia=-1
    posicao_incidencia=-1

    for posicao_incidencia in incidencias_a_considerar:
        tempo_resposta=incidencias[posicao_incidencia][2]
        max_0=math.fabs(posicao_atual-incidencias[posicao_incidencia][0])
        max_1 = math.fabs(posicao_atual-incidencias[posicao_incidencia][1])
        if max_0>max_1:
            id_incidencia=incidencias[posicao_incidencia][0]
        else:
            id_incidencia = incidencias[posicao_incidencia][1]
        tempo_total+=get_tempo_atualizado(posicao_atual,id_incidencia)
        if new_visitas[posicao_incidencia]==False:
            break

    if math.fabs(tempo_total - tempo_resposta) > 45 and len(incidencias_a_considerar)>0:
        id_incidencia=-1

    return id_incidencia,posicao_incidencia

def criar_rota_particular(lista_sublancos,incidencias_a_considerar,id_turno,carro_origem,tempo_paragens):

    global count_rota
    count_rota+=1

    new_visitas=[False]*len(incidencias)

    for index in range(len(incidencias_visitadas)):
        if index in incidencias_a_considerar:
            new_visitas[index]=False
        else:
            new_visitas[index]=True

    new_rota=carro_origem.copy()

    new_tempo_paragens=tempo_paragens.copy()

    posicao_inicial=carro_origem[-1]

    if posicao_inicial not in lista_sublancos:
        if posicao_inicial>max(lista_sublancos):
            id_posicao=max(lista_sublancos)+1
        else:
            id_posicao=min(lista_sublancos)-1

        if posicao_inicial <= id_posicao:
            for posicao in range(posicao_inicial+1, id_posicao + 1):
                new_rota, new_tempo_paragens = adicionar_posicao(posicao, "Início", new_rota,
                                                                     new_tempo_paragens,
                                                                     lista_sublancos, id_turno)
        else:
            for posicao in range(posicao_inicial-1, id_posicao - 1, -1):
                tempo = get_distance(posicao, posicao - 1)
                new_rota, new_tempo_paragens = adicionar_posicao(posicao, "Início", new_rota,
                                                                     new_tempo_paragens, lista_sublancos, id_turno)

    tempo_atual=new_tempo_paragens[-1].get('Hora Fim')
    tempo_to_fim=0
    tempo_nos_sublanco=tempos_nos[min(lista_sublancos):max(lista_sublancos)+1]
    tempo_nos_sublanco=sum(tempo_nos_sublanco)
    tempo_abertura=8*60
    tempo_abertura=tempo_abertura-tempo_nos_sublanco

    posicao_incidencia_anterior=-1
    n_pausas=0
    n_almocos=0
    n_fim=0

    while tempo_atual+tempo_to_fim<tempo_abertura:

        n_pausas,n_almocos,n_fim=verificar_npausas(new_tempo_paragens)
        id_paragem, tipo_paragem = verificar_ultima_paragem(lista_sublancos, new_rota, new_tempo_paragens, id_turno)

        id_paragem,tipo_paragem=verificar_ultima_paragem(lista_sublancos, new_rota, new_tempo_paragens, id_turno)

        id_incidencia,posicao_incidencia=verificar_ultima_incidencia(incidencias_a_considerar, new_rota, new_tempo_paragens, new_visitas, id_turno)

        if id_paragem!=-1:

            temp_rota=new_rota.copy()
            temp_paragens=new_tempo_paragens.copy()
            temp_rota, temp_paragens = go_to(id_paragem, lista_sublancos, tipo_paragem, temp_rota, temp_paragens, 0)
            temp_final=temp_paragens[-1].get('Hora Fim')
            tempo_to_fim = get_distance(temp_rota[0], temp_paragens[-1].get('posicao'))
            if temp_final+tempo_to_fim<tempo_abertura:
                new_rota, new_tempo_paragens = go_to(id_paragem,lista_sublancos,tipo_paragem,new_rota,new_tempo_paragens,0)  #verificar se ele está a ir a um sublanço dele e se assim for assume o sentido que está a ir. se sai do sublanços sentido oposto que esta a ir
            else:
                tempo_to_fim=10000000

        elif id_incidencia!=-1 and tipo_paragem!='Fim':

            temp_rota = new_rota.copy()
            temp_paragens = new_tempo_paragens.copy()
            temp_rota, temp_paragens = go_to(id_incidencia, lista_sublancos, "Incidência", temp_rota,
                                                 temp_paragens, 0)

            temp_final = temp_paragens[-1].get('Hora Fim')
            tempo_to_fim = get_distance(temp_rota[0], temp_paragens[-1].get('posicao'))
            if temp_final + tempo_to_fim < tempo_abertura and posicao_incidencia_anterior!=posicao_incidencia:
                new_rota, new_tempo_paragens = go_to(id_incidencia,lista_sublancos,"Incidência",new_rota,new_tempo_paragens,0)
                posicao_incidencia_anterior = posicao_incidencia
                new_visitas[posicao_incidencia]=True
            else:
                tempo_to_fim=10000000

        else:
            temp_rota = new_rota.copy()
            temp_paragens = new_tempo_paragens.copy()
            temp_rota, temp_paragens = adicionar_posicao(-1,"Deslocação", temp_rota, temp_paragens,lista_sublancos,id_turno)
            temp_final = temp_paragens[-1].get('Hora Fim')
            tempo_to_fim = get_distance(temp_rota[0], temp_paragens[-1].get('posicao'))

            if temp_final + tempo_to_fim < tempo_abertura:
                new_rota, new_tempo_paragens = adicionar_posicao(-1,"Deslocação", new_rota, new_tempo_paragens,lista_sublancos,id_turno)
            else:
                tempo_to_fim=10000000

        tempo_atual=new_tempo_paragens[-1].get('Hora Fim')

        # tempo_to_fim=get_distance(new_rota[0],new_tempo_paragens[-1].get('posicao'))

    new_rota, new_tempo_paragens = go_to(new_rota[0], lista_sublancos, "Fim", new_rota,
                                             new_tempo_paragens, 0)



    return new_rota,new_tempo_paragens,new_visitas

def get_co_proximo(index, sentido):

    global centros_operacionais

    found = False
    min_co=99
    max_co=-1

    if (sentido == "Norte"):
        for no in nos:
            i=no.id
            is_co=no.co
            if (i <= index) and i>max_co and is_co==1:
                found = True
                max_co=i
                break


    if (sentido == "Sul"):
        for no in nos:
            i = no.id
            is_co = no.co
            if (i >= index) and i<min_co and is_co==1:
                found = True
                min_co=i
                break

    if found == False:
        return -1

    elif sentido=='Norte':
        return max_co

    elif sentido=='Sul':
        return min_co

def verificar_carro_iniciado(id_turno,index,vetor_sublancos,passos,sentido,descer):

    co = get_co_proximo(index, sentido)

    if descer==1:
        incrementar=-1
    else:
        incrementar=1

    id_range=co

    min_dif=99
    dif_incremental=0
    for index in range(len(vetor_sublancos)):
        if math.fabs(vetor_sublancos[index]-co)<min_dif and math.fabs(vetor_sublancos[index]-co)!=0:
            min_dif=math.fabs(vetor_sublancos[index]-co)
            dif_incremental=math.fabs(vetor_sublancos[index]-(co+incrementar))
            id_range=vetor_sublancos[index]


    if len(passos) == 0 and dif_incremental<=min_dif:
        if co > -1:
            passos=adicionar_posicao(co,"Início",passos,vetor_sublancos,id_turno)
            if co!=0:
                passos = adicionar_posicao(co+incrementar, "Início",passos, vetor_sublancos,
                                                         id_turno)
                posicao=co+incrementar

    return passos

def verificar_restricoes(new_tempo_paragens,lista_sublancos,vetor_incidencias,new_visitas):

    valor =True

    soma=0

    tempo_visita=([resposta-90])*len(nos)

    for posicao in range(1,len(new_tempo_paragens)):

        id_posicao= new_tempo_paragens[posicao].get('posicao')

        if posicao==1:
            tempo_anterior=0
        else:
            tempo_anterior=new_tempo_paragens[posicao-1].get('Hora Fim')

        tempo_atual = new_tempo_paragens[posicao].get('Hora Fim')

        tempo_retirar=tempo_atual-tempo_anterior

        for index in lista_sublancos:

            if tempo_visita[index] < 0:
                valor = False
                soma += tempo_visita[index]

            if index==id_posicao:
                tempo_visita[index]=resposta
            else:
                tempo_visita[index]=tempo_visita[index]-tempo_retirar

            if tempo_visita[index] < 0:
                valor = False
                soma += tempo_visita[index]


    for posicao_incidencia in incidencias_a_considerar:
        if new_visitas[posicao_incidencia]==False:
            valor=False

    return valor,soma

def limpar_incidencias(best_incidencias):

    incidencias_a_manter=[]

    for posicao in range(len(incidencias_visitadas)):
        if incidencias_visitadas[posicao] == False:
            incidencias_a_manter.append(posicao)

    for index in range(len(best_incidencias)):
        posicao=best_incidencias[index]
        if posicao in incidencias_a_manter:
            incidencias_a_manter.remove(posicao)
        incidencias_visitadas[posicao]=True

def compara_incidencias(incidencias_a_considerar,best_incidencias):

    resultado=True

    for incidencia in best_incidencias:
        encontrar=False
        for incidencia_nova in incidencias_a_considerar:
            if incidencia==incidencia_nova:
                encontrar=True
        if encontrar==False:
            resultado=False
            return resultado

    return resultado

def verificar_best(temp_rotas,temp_tempos,temp_incidencias,best_rota,best_tempo,best_incidencias,guardar_best,temp_sub,best_sub):

    j=0
    compara_1=0
    compara_2=0

    if len(temp_sub)>len(best_sub) :
        best_rota = temp_rotas.copy()
        best_tempo = temp_tempos.copy()
        best_incidencias = temp_incidencias.copy()
        best_sub=temp_sub.copy()
        guardar_best = True

        return best_rota, best_tempo, best_incidencias, guardar_best,best_sub

    while j<len(incidencias_a_considerar) or j<len(best_incidencias):
        if j>=len(incidencias_a_considerar):
            compara_1=99
        else:
            compara_1=incidencias_a_considerar[j]
        if j>=len(best_incidencias):
            compara_2=99
        else:
            compara_2=best_incidencias[j]

        if compara_1<compara_2:
            best_rota = temp_rotas.copy()
            best_tempo = temp_tempos.copy()
            best_incidencias = temp_incidencias.copy()
            best_sub=temp_sub.copy()
            guardar_best = True

            return best_rota,best_tempo,best_incidencias,guardar_best,best_sub

        j += 1



    return best_rota,best_tempo,best_incidencias,guardar_best,best_sub


def adicionar_vistorias(new_tempo_paragens, lista_sublancos,new_visitas,tempos_nos, id_turno):
    temp_paragens = new_tempo_paragens.copy()
    melhor_paragem = temp_paragens.copy()

    visitado_sul_norte = [False]*len(vistorias)
    visitado_norte_sul = [False]*len(vistorias)

    posicao = 0
    total = len(temp_paragens)
    max_soma = 999999
    index = -1
    for vistoria in vistorias:
        index += 1
        posicao = 1
        max_soma = 999999
        while posicao < total:
            id_posicao = temp_paragens[posicao].get('posicao')
            # Verificar sentido
            if (posicao + 1 < total):
                if (id_posicao < temp_paragens[posicao + 1].get('posicao')):
                    sentido = 'norte'
                else:
                    sentido = 'sul'
            else:
                sentido = 'sul'

            if (id_posicao == vistoria.get('Nó Início') or id_posicao == vistoria.get('Nó Fim')) and visitado_sul_norte[index] == False and sentido == 'norte':

                temp_paragens_2 = melhor_paragem.copy()

                tempo_add = vistoria.get('Tempo Sul Norte')

                # tempo_add=tempos_nos[no]

                temp_paragens_2, count = visitar_no(id_posicao, temp_paragens_2, posicao, tempo_add, "Vistoria", -1)

                visitado_sul_norte[index] = True

                # valor,soma=verificar_restricoes(temp_paragens_2,lista_sublancos,[],new_visitas, id_turno)

                soma = calcular_delta(temp_paragens_2, -1, id_turno)

                if soma < max_soma:
                    max_soma = soma
                    melhor_paragem = temp_paragens_2.copy()

            posicao += 1

        temp_paragens = melhor_paragem.copy()

    melhor_paragem = temp_paragens.copy()

    index = -1
    for vistoria in vistorias:
        index += 1
        posicao = 1
        max_soma = 999999
        while posicao < total:
            id_posicao = temp_paragens[posicao].get('posicao')
            # Verificar sentido
            if (posicao + 1 < total):
                if (id_posicao <= temp_paragens[posicao + 1].get('posicao')):
                    sentido = 'norte'
                else:
                    sentido = 'sul'
            else:
                sentido = 'norte'

            if (id_posicao == vistoria.get('Nó Início') or id_posicao == vistoria.get('Nó Fim')) and visitado_norte_sul[index] == False and sentido == 'sul':

                temp_paragens_2 = melhor_paragem.copy()

                tempo_add = vistoria.get('Tempo Norte Sul')

                # tempo_add=tempos_nos[no]

                temp_paragens_2, count = visitar_no(id_posicao, temp_paragens_2, posicao, tempo_add, "Vistoria", -1)

                visitado_norte_sul[index] = True

                # valor,soma=verificar_restricoes(temp_paragens_2,lista_sublancos,[],new_visitas, id_turno)

                soma = calcular_delta(temp_paragens_2, -1, id_turno)

                if soma < max_soma:
                    max_soma = soma
                    melhor_paragem = temp_paragens_2.copy()

            posicao += 1

        temp_paragens = melhor_paragem.copy()

    melhor_paragem = temp_paragens.copy()

    return melhor_paragem

def adicionar_nos_dois_sentidos( new_tempo_paragens, lista_sublancos,new_visitas,tempos_nos, id_turno):

    temp_paragens=new_tempo_paragens.copy()

    melhor_paragem = temp_paragens.copy()

    count=0

    nos_visitados=lista_sublancos.copy()

    sentido = 'norte'

    visitado_sul_norte = [False]*len(nos)
    visitado_norte_sul = [False]*len(nos)

    for index in range(len(new_tempo_paragens)):
        sentido = verificar_sentido(index, new_tempo_paragens)
        if(new_tempo_paragens[index].get('Tipo') == "Visitar Nó"):
           id_posicao = new_tempo_paragens[index].get('posicao')
           if(sentido == "Crescente"):
               visitado_norte_sul[id_posicao] = True
           else:
               visitado_sul_norte[id_posicao] = True

    for no in nos:

        posicao=0
        total=len(temp_paragens)
        max_soma = 99999

        while posicao<total:



            id_posicao=temp_paragens[posicao].get('posicao')

            # Verificar sentido
            if (posicao + 1 < total):
                if (id_posicao < temp_paragens[posicao + 1].get('posicao')):
                    sentido = 'norte'
                else:
                    sentido = 'sul'
            else:
                sentido = 'sul'

            #Ver se já foi visitado


            if id_posicao==no.id and sentido == 'norte' and visitado_sul_norte[id_posicao] == False:

                temp_paragens_2=melhor_paragem.copy()

                tempo_add = tempos_nos_sul_norte[no.id]

                #tempo_add=tempos_nos[no]

                temp_paragens_2,count=visitar_no(id_posicao,temp_paragens_2,posicao,tempo_add,"Visitar Nó",-1)

                visitado_sul_norte[id_posicao] = True

                #valor,soma=verificar_restricoes(temp_paragens_2,lista_sublancos,[],new_visitas, id_turno)

                soma = calcular_delta(temp_paragens_2, -1,id_turno)

                if soma<max_soma:
                    max_soma=soma
                    melhor_paragem=temp_paragens_2.copy()

            posicao += 1

        temp_paragens=melhor_paragem.copy()

    melhor_paragem = temp_paragens.copy()

    for no in nos:

        posicao = 0
        total = len(temp_paragens)
        max_soma = 99999

        while posicao < total:

            id_posicao = temp_paragens[posicao].get('posicao')

            # Verificar sentido
            if (posicao + 1 < total):
                if (id_posicao <= temp_paragens[posicao + 1].get('posicao')):
                    sentido = 'norte'
                else:
                    sentido = 'sul'
            else:
                sentido = 'norte'

            if id_posicao == no.id and sentido == 'sul' and visitado_norte_sul[id_posicao] == False:

                temp_paragens_2 = melhor_paragem.copy()

                tempo_add = tempos_nos_norte_sul[no.id]

                # tempo_add=tempos_nos[no]

                temp_paragens_2, count = visitar_no(id_posicao, temp_paragens_2, posicao, tempo_add, "Visitar Nó",-1)

                soma = calcular_delta(temp_paragens_2, -1,id_turno)

                visitado_norte_sul[id_posicao] = True

                if soma < max_soma:
                    max_soma = soma
                    melhor_paragem = temp_paragens_2.copy()

            posicao += 1

        temp_paragens = melhor_paragem.copy()

    return melhor_paragem

def adicionar_nos( new_tempo_paragens, lista_sublancos,new_visitas,tempos_nos):

    temp_paragens=new_tempo_paragens.copy()

    melhor_paragem = temp_paragens.copy()

    count=0

    nos_visitados=lista_sublancos.copy()

    for no in lista_sublancos:

        posicao=0
        total=len(temp_paragens)
        max_soma = -9999

        while posicao<total:

            id_posicao=temp_paragens[posicao].get('posicao')

            if id_posicao==no:

                temp_paragens_2=melhor_paragem.copy()

                tempo_add=tempos_nos[no]

                temp_paragens_2,count=visitar_no(id_posicao,temp_paragens_2,posicao,tempo_add,"Visitar Nó",-1)

                valor,soma=verificar_restricoes(temp_paragens_2,lista_sublancos,[],new_visitas)

                if soma>max_soma:
                    max_soma=soma
                    melhor_paragem=temp_paragens_2.copy()

            posicao += 1

        temp_paragens=melhor_paragem.copy()

    return melhor_paragem

def n_passagens_id(id_pausa,temp_tempos_passagem,id_atual):

    count=0
    vetor_posicoes=[]

    sentido_atual=verificar_sentido(id_atual,temp_tempos_passagem)

    for index in range(id_atual,len(temp_tempos_passagem)):

        posicao=temp_tempos_passagem[index].get('posicao')
        sentido=verificar_sentido(index,temp_tempos_passagem)

        if posicao==id_pausa and sentido_atual==sentido:
            count+=1
            vetor_posicoes.append(index)

    return count,vetor_posicoes

def nao_cumpre(vetor_inicial,vetor_final,lista):

    Resultado=False
    count_1=0
    count_2=0

    for index in range(len(vetor_inicial)):
        if vetor_inicial[index].get('Tipo')!="Deslocação" and vetor_inicial[index].get('Tipo')!="Início" and vetor_inicial[index].get('Tipo')!="Espera":
            count_1+=1

    for index in range(len(vetor_final)):
        if vetor_final[index].get('Tipo')!="Deslocação" and vetor_final[index].get('Tipo')!="Início" and vetor_final[index].get('Tipo')!="Espera":
            count_2+=1

    if count_1!=count_2:
        Resultado=True
        return True

    valor,soma=verificar_restricoes(vetor_final,lista,[],[True]*len(incidencias))

    if valor==False:
        Resultado=True

    return Resultado

def delete_vaivem(rotas,tempos,lista):

    guardar_rotas=[]
    guardar_passagens=[]

    temp_rotas=rotas.copy()
    temp_tempos=tempos.copy()
    posicao_rota=-1

    for index in range(len(temp_tempos)):

        posicao_rota += 1
        rota = temp_tempos[posicao_rota]
        n_pontos = len(rota)
        best = []
        valor_best = 9999
        valor_bool=True

        for id_pausa in lista:

            vetor_posicoes=[]
            posicao_1=-1
            posicao_2=-1
            i=0

            while i<n_pontos:

                posicao_atual=rota[i].get('posicao')

                if posicao_atual==id_pausa:

                    count_passagens, vetor_passagens = n_passagens_id(id_pausa, rota, i)  # adicionar verificação a partir do i
                                                                                    # verificar se o sentido da posicao da pausa é igual ao sentido da posicao i

                    sentido = verificar_sentido(i, rota)

                    for k in range(count_passagens):

                        stop_condition=False

                        j=0
                        count=0

                        sentido_anterior = verificar_sentido(j, rota)

                        encontrei_vaivem = False

                        while stop_condition==False:

                            if j>=n_pontos:
                                stop_condition=True
                            if count>k:
                                stop_condition=True

                                if j<n_pontos and i<n_pontos: #pq tenho de por isto?
                                    if rota[j].get('posicao')==rota[i].get('posicao') and math.fabs(i-j)>1:

                                        encontrei_vaivem=True
                                        posicao_1=min(j,i)
                                        posicao_2=max(j,i)
                                        vetor_posicoes.append([i,j])

                            if stop_condition!=True and j<n_pontos:
                                if rota[j].get('posicao')==rota[i].get('posicao') and sentido_anterior==sentido:
                                    count+=1

                            j += 1

                        if encontrei_vaivem==True:

                            temp_solucao=rota.copy()
                            new_row={'posicao':id_pausa,'Hora Inicio':temp_solucao[posicao_1].get('Hora Fim'), 'Hora Fim':temp_solucao[posicao_2].get('Hora Inicio'),"Tipo":"Espera"}
                            temp_solucao.insert(posicao_1,new_row)
                            del temp_solucao[posicao_1 + 1:posicao_2 + 1]

                            valor_bool = nao_cumpre(rota,temp_solucao,lista_sublancos_solucao[posicao_rota])

                            if valor_bool==False and len(best)==0:
                                best = temp_solucao.copy()

                            if valor_bool==False and len(temp_solucao)<len(best):
                                best=temp_solucao.copy()


                if len(best)!=0:
                    rota=best.copy()

                i += 1
                n_pontos = len(rota)

        guardar_passagens.append(rota)

    return guardar_passagens

def verificar_sentido(posicao,tempos):

    sentido=""

    if tempos[posicao].get('posicao')>tempos[posicao-1].get('posicao'):
        sentido="Crescente"
    else:
        sentido="Decrescente"

    return sentido

def consideracoes_final(rotas):
    total_sublancos = []
    for index in range(len(nos)):
        total_sublancos.append(index)

    guardar_passagens = delete_vaivem(rotas, tempos, total_sublancos)
    rotas = guardar_passagens.copy()

    guardar_passagens = []

    for index in range(len(rotas)):
        temp_passos = rotas[index].copy()
        new_tempo_paragens = adicionar_nos(temp_passos, lista_sublancos_solucao[index], [True] * len(incidencias),
                                           tempos_nos)
        guardar_passagens.append(new_tempo_paragens)

    output = []

    com_zeros, sem_zeros = calcular_tempo_resposta(guardar_passagens, 7,lista_sublancos_solucao)
    #tempo_medio_passagem=calcular_tempo_medio_passagem(guardar_passagens)

    vetor_solucao = guardar_passagens.copy()

    for index in range(len(vetor_solucao)):

        for posicao in range(len(vetor_solucao[index])):
            new_row = {'Carro': index, 'Nó': nos[vetor_solucao[index][posicao].get('posicao')].nome,
                       'Hora Inicio': vetor_solucao[index][posicao].get('Hora Inicio'),
                       'Hora Fim': vetor_solucao[index][posicao].get('Hora Fim'),
                       'Tipo': vetor_solucao[index][posicao].get('Tipo')}

            output.append(new_row)

    df_output = pd.DataFrame(output)
    df_output.to_csv('dados/99. output.csv', encoding='iso-8859-1')

def inverter_nos():

    versoes=[]
    temp=[]
    for no in nos:

        temp.append(no.id)

    versoes.append(temp)
    temp=[]

    for no in list(reversed(nos)):
        temp.append(no.id)

    versoes.append(temp)

    return versoes

def verificar_best_global(rotas,best):

    best_global=rotas.copy()
    len_rotas=0
    len_best=0

    for rota in rotas:
        len_rotas+=len(rota)

    for rota in best:
        len_best+=len(rota)

    if len_best<len_rotas and len_best>0:
        best_global = best.copy()

    return best_global

def adiciona_pausas(paragens,id_turno):

    best_rota=paragens.copy()
    rota=best_rota.copy()

    for id_pausa in range(len(pausas_hora_fim[id_turno])):

        hora_inicio_resposta=pausas_hora_inicio[id_turno][id_pausa]

        hora_fim_resposta=pausas_hora_fim[id_turno][id_pausa]

        duracao=hora_fim_resposta-hora_inicio_resposta

        rotas_alternativas = []
        total=len(best_rota)-1
        id_posicao=0

        while id_posicao<total:

            posicao=best_rota[id_posicao]

            tempo_resolucao=duracao

            if posicao.get('posicao') in pausas_id_inicio[id_turno][id_pausa]:

                rota=best_rota.copy()

                rota,count=visitar_no(posicao.get('posicao'), rota, id_posicao,tempo_resolucao,"Pausa", id_pausa)

                delta = calcular_delta(rota,id_pausa,id_turno)

                new_row={'id_pausa':posicao,'id_no':posicao.get('posicao'),'posicao_vetor':id_posicao,'delta':delta,'rota':rota}

                rotas_alternativas.append(new_row)

            total = len(best_rota)-1
            id_posicao += 1

        min_delta=math.inf

        deltas=[]
        for index in range(len(rotas_alternativas)):
            deltas.append(rotas_alternativas[index].get('delta'))


        if len(rotas_alternativas)>0:

            best_rota=rotas_alternativas[0].get('rota')

        for rota in rotas_alternativas:

            if rota.get('delta')<min_delta:

                best_rota=rota.get('rota').copy()
                min_delta=rota.get('delta')

    return best_rota

def calcular_ponto_minimo(id_pausa,id_posicao_final):
    min_dist = 999
    id_to_go = pausas_id_inicio[id_pausa][0]

    for id_possivel in pausas_id_inicio[id_pausa]:

        if math.fabs(id_posicao_final - id_possivel) < min_dist:
            min_dist = math.fabs(id_posicao_final - id_possivel)
            id_to_go = id_possivel

    return id_to_go

def ler_pausas():

    global pausas_hora_inicio
    global pausas_hora_fim
    global pausas_id_inicio
    global pausas_id_fim

    df_pausas=pd.read_csv('dados/04. pausas obrigatorias.csv',sep=",", encoding='iso-8859-1')

    df_pausas.sort_values(by='Hora Inicio')

    pausas_hora_inicio=[[]]*len(turnos)
    pausas_hora_fim=[[]]*len(turnos)
    pausas_id_inicio=[[]]*len(turnos)
    pausas_id_fim=[[]]*len(turnos)

    count=-1

    for index,row in df_pausas.iterrows():

        count+=1

        lista_in=[]

        lista_out=[]

        if pd.isna(row['Nó Início']):

            for no in nos:

                if row['Tipo']=='Pausa' and no.pausa!=0:

                    lista_in.append(no.id)

                if row['Tipo'] == 'Almoço' and no.almoco !=0:

                    lista_in.append(no.id)

        else:

            for no in nos:

                if row['Nó Início'] in no.nome:

                    lista_in.append(no.id)

                if row['Nó Fim'] in no.nome:

                    lista_out.append(no.id)

        for posicao_turno in range(len(turnos)):

            if row['Hora Inicio']>=turnos[posicao_turno].inicio and row['Hora Inicio']<=turnos[posicao_turno].fim:
                temp_inicio=pausas_hora_inicio[posicao_turno].copy()
                temp_inicio.append(row['Hora Inicio'])
                pausas_hora_inicio[posicao_turno]=temp_inicio.copy()

                temp_fim=pausas_hora_fim[posicao_turno].copy()
                temp_fim.append(row['Hora Fim'])
                pausas_hora_fim[posicao_turno]=temp_fim.copy()

                temp_id_inicio=pausas_id_inicio[posicao_turno].copy()
                temp_id_inicio.append(lista_in)
                pausas_id_inicio[posicao_turno]=temp_id_inicio.copy()

                temp_id_fim=pausas_id_inicio[posicao_turno].copy()
                temp_id_fim.append(lista_in)
                pausas_id_fim[posicao_turno]=temp_id_fim.copy()

                break

        lista_in = []

        lista_out = []

def criar_rota_dividida(n_voltas, co_a_considerar, sublancos_a_considerar, id_turno,sentido_anterior):

    # 2 sentidos, requerem duas rotas
    rota_1 = []
    rota_2 = []
    tempo_paragens_1 = []
    tempo_paragens_2 = []
    # Adicionar_CO
    tempo_paragens_1 = adicionar_posicao(co_a_considerar, "Início",
                                                 tempo_paragens_1, sublancos_a_considerar, id_turno)
    tempo_paragens_2 = adicionar_posicao(co_a_considerar, "Início",
                                                 tempo_paragens_2, sublancos_a_considerar, id_turno)
    for i in range(n_voltas):
        # Sentido norte
        tempo_paragens_1 = go_to(sublancos_a_considerar[0].id, sublancos_a_considerar, "Deslocação",
                                         tempo_paragens_1, id_turno)
        tempo_paragens_1 = go_to(sublancos_a_considerar[-1].id, sublancos_a_considerar, "Deslocação",
                                         tempo_paragens_1, id_turno)
        # Sentido sul
        tempo_paragens_2 = go_to(sublancos_a_considerar[-1].id, sublancos_a_considerar, "Deslocação",
                                         tempo_paragens_2, id_turno)
        tempo_paragens_2 = go_to(sublancos_a_considerar[0].id, sublancos_a_considerar, "Deslocação",
                                         tempo_paragens_2, id_turno)
    # Adicionar_CO
    tempo_paragens_1 = go_to(co_a_considerar, sublancos_a_considerar, "Deslocação",
                                     tempo_paragens_1, id_turno)
    tempo_paragens_2 = go_to(co_a_considerar, sublancos_a_considerar, "Deslocação",
                                     tempo_paragens_1, id_turno)

    # Incluir Vistorias
    print('a incluir vistorias')
    tempo_paragens_1 = adicionar_vistorias(tempo_paragens_1, sublancos_a_considerar, [], tempos_nos, id_turno)
    tempo_paragens_2 = adicionar_vistorias(tempo_paragens_2, sublancos_a_considerar, [], tempos_nos, id_turno)

    # Incluir Nós
    print('a incluir nós')
    tempo_paragens_1 = adicionar_nos_dois_sentidos(tempo_paragens_1, sublancos_a_considerar, [], tempos_nos, id_turno)
    tempo_paragens_2 = adicionar_nos_dois_sentidos(tempo_paragens_2, sublancos_a_considerar, [], tempos_nos, id_turno)

    # Incluir Pausas
    print('a incluir pausas')
    tempo_paragens_1 = adiciona_pausas(tempo_paragens_1, id_turno)
    tempo_paragens_2 = adiciona_pausas(tempo_paragens_2, id_turno)

    # Incluir Espera
    print('a incluir espera')
    tempo_paragens_1=adiciona_esperas(tempo_paragens_1,id_turno)
    tempo_paragens_2 = adiciona_esperas(tempo_paragens_2, id_turno)

    tempo_paragens_1=[tempo_paragens_1]
    tempo_paragens_2 = [tempo_paragens_2]

    montecarlo_1,tempo_medio_passagem_1,output_simulacoes_1 = calcular_tempo_resposta(tempo_paragens_1, tempo_inicio_turno,id_turno,n_voltas)
    montecarlo_2,tempo_medio_passagem_2,output_simulacoes_2 = calcular_tempo_resposta(tempo_paragens_2,tempo_inicio_turno ,id_turno,n_voltas)

    if sentido_anterior=='nd':
        if (montecarlo_1 > montecarlo_2):
            rota_best = rota_2
            tempo_paragens_best = tempo_paragens_2
            montecarlo_best=montecarlo_2
            passagem_best=tempo_medio_passagem_2
            sentido='crescente'
            simulacoes=output_simulacoes_2
        else:
            rota_best = rota_1
            tempo_paragens_best = tempo_paragens_1
            passagem_best=tempo_medio_passagem_1
            montecarlo_best=montecarlo_1
            sentido='decrescente'
            simulacoes=output_simulacoes_1
    elif sentido_anterior=='crescente':
        rota_best = rota_1
        tempo_paragens_best = tempo_paragens_1
        passagem_best = tempo_medio_passagem_1
        montecarlo_best = montecarlo_1
        sentido = 'decrescente'
        simulacoes=output_simulacoes_1
    elif sentido_anterior=="decrescente":
        rota_best = rota_2
        tempo_paragens_best = tempo_paragens_2
        montecarlo_best = montecarlo_2
        passagem_best = tempo_medio_passagem_2
        sentido = 'crescente'
        simulacoes=output_simulacoes_2

    return rota_best, tempo_paragens_best,montecarlo_best,passagem_best,sentido,simulacoes

def calcular_tempo_resposta(rotas,hora_inicio_turno,id_turno,n_voltas):

    hora_inicio_turno=turnos[id_turno].inicio

    global code_paragem
    global no_paragem
    global hora_paragem
    global min_hora
    global max_hora
    global tempo_inicio_turno

    rows=[]
    paragens=[]

    flat_list = [item for sublist in rotas for item in sublist]

    df_probabilidades = pd.read_csv('dados/probabilidades sem zeros.csv', sep=",", encoding='iso-8859-1')

    monte_carlo_com_zeros,output_simulacoes=gerar_montecarlo(df_probabilidades,flat_list,tempo_inicio_turno,id_turno,n_voltas)

    tempo_medio_passagem=calcular_tempo_medio_passagem(rotas)

    return monte_carlo_com_zeros,tempo_medio_passagem,output_simulacoes

def gerar_montecarlo(df_probabilidades,paragens,tempo_inicio_turno,id_turno,n_voltas):

    #tempo_inicio_turno=turnos[tempo_inicio_turno].inicio
    #method=0 - probabilidades maiores

    global t_medio_incidencia

    output_inicial=paragens.copy()

    output_inicial=condensar_paragens(paragens)

    duracao_paragens = []

    #FILTRAR AS OCORRENCIAS POR HORA (TEM DE SE ESTAR DENTRO DO TURNO)

    min_hora=9999
    for posicao_rota in paragens:
        if posicao_rota.get('Hora Inicio')+tempo_inicio_turno<min_hora:
            min_hora=int(posicao_rota.get('Hora Inicio')/60)+tempo_inicio_turno

    max_hora = -1
    for posicao_rota in paragens:
        if posicao_rota.get('Hora Fim')+tempo_inicio_turno > max_hora:
            max_hora = int(posicao_rota.get('Hora Fim')/60)+tempo_inicio_turno

    df_probabilidades = df_probabilidades[
        (df_probabilidades['Hora'] >= min_hora) & (df_probabilidades['Hora'] < max_hora)]

    df_probabilidades['Probabilidade incidência'] = df_probabilidades['Probabilidade incidência'].replace("%", "",
                                                                                                          regex=True).astype(
        float) / 100

    output=[]

    lista_probabilidades=df_probabilidades['Probabilidade incidência'].tolist()
    lista_hora=df_probabilidades['Hora'].tolist()
    lista_sublanco=df_probabilidades['Sublanço'].tolist()

    for index in range(n_simulacoes):

        hora_incidencia = []
        sublanco_incidencia = []

        for posicao in range(len(lista_probabilidades)):

            probabilidade = lista_probabilidades[posicao]

            if probabilidade > random.random():
                hora_incidencia.append(lista_hora[posicao])
                sublanco_incidencia.append(lista_sublanco[posicao])

        #VERIFICAR SE A INCIDENCIA ACONTECE DENTRO DOS NÓS QUE ESTÃO A SER CONSIDERADOS

        nos_incidencias=filtrar_incidencias(hora_incidencia,sublanco_incidencia)

        for incidencia in nos_incidencias:

            hora_incidencia=incidencia.get('hora')

            pontos_hora=[]
            posicao_real=[]
            id_real=-1

            for paragem in paragens:

                id_real+=1

                if round(paragem.get('Hora Inicio')/60+tempo_inicio_turno)==hora_incidencia:

                    pontos_hora.append(paragem)
                    posicao_real.append(id_real)

            if len(pontos_hora)>0:

                #ESCOLHER UM PONTO ALEATÓRIO A PARTIR DO QUAL SE VAI RESPONDER À INCIDENCIA

                posicao_escolhida=random.randint(0,len(pontos_hora)-1)#escolha do ponto a partir do qual se vai calcular o tempo de resposta
                posicao_real_escolhida=posicao_real[posicao_escolhida]

                ponto_partida=pontos_hora[posicao_escolhida]

                id_no_partida=ponto_partida.get('posicao')

                id_no_in=incidencia.get('no_in')
                id_no_out=incidencia.get('no_out')

                min_acontecimento=ponto_partida.get('Hora Fim')

                if math.fabs(id_no_out-id_no_partida)>math.fabs(id_no_out-id_no_partida) or id_no_in==-1:

                    id_no_chegada=id_no_out

                else:

                    id_no_chegada=id_no_in

                #ADICIONA TODAS AS POSICOES INTERMEDIAS ENTRE O PONTO INICIAL E O FINAL
                print('posicao atual: ' + str(id_no_partida) + ' posicao incidencia: ' + str(id_no_chegada))
                paragens,tempo_total, add,last_hora_fim,first_hora_inicio = go_to_incidencia(paragens,posicao_real_escolhida,id_no_chegada,id_no_partida,id_turno)

                #TEMPO PARA RESPONDER À INCIDENCIA

                tempo_de_resposta=get_distance(id_no_chegada,id_no_partida)
                print('simulacao: ' + str(index) +'/' + str(n_simulacoes) + ' tempo de resposta: ' + str(tempo_de_resposta))
                duracao_paragens.append(tempo_de_resposta)

                #ATUALIZAR VETOR POSICOES
                paragens=update_posicoes(paragens,min_acontecimento,tempo_total, posicao_real_escolhida + add,last_hora_fim,first_hora_inicio)

                for posicao in range(len(paragens)):
                    new_row = {'Simulação': index, 'Número Voltas':n_voltas,'Turno':id_turno,'Nó': paragens[posicao].get('posicao'),
                               'Hora Inicio': paragens[posicao].get('Hora Inicio'),'Hora Fim':paragens[posicao].get('Hora Fim'),'Tipo':paragens[posicao].get('Tipo')}

                    output.append(new_row)

        #RESET NO VETOR DAS PARAGENS
        paragens=output_inicial.copy()

    if len(duracao_paragens)>0:

        simulcao_montecarlo=sum(duracao_paragens)/len(duracao_paragens)

    else:

        simulcao_montecarlo=0

    return simulcao_montecarlo,output

def update_posicoes(paragens,min_acontecimento,tempo_total, posicao_incidencia,last_hora_fim,first_hora_inicio):

    tempo_total=last_hora_fim-first_hora_inicio


    counter=-1

    for posicao in paragens[posicao_incidencia + 2:]:

        counter+=1

        tempo_atual=posicao.get('Hora Inicio')
        tempo_atual2=posicao.get('Hora Fim')

        tempo_atualizado=tempo_atual+tempo_total
        tempo_atualizado2=tempo_atual2+tempo_total

        posicao.update({'Hora Inicio': tempo_atualizado})
        posicao.update({'Hora Fim': tempo_atualizado2})

    return paragens

def calcular_delta(rota,id_pausa,id_turno):

    delta = 0
    dif_inicio = 0
    dif_fim = 0
    id_posicao=-1

    if id_pausa == -1:
        for i in range(len(rota)):
            if(rota[i].get('Tipo') == 'Pausa'):

                dif_inicio = pausas_hora_inicio[id_turno][rota[i].get('id_pausa')] - rota[i].get('Hora Fim')

                dif_fim = rota[i].get('Hora Inicio') - pausas_hora_fim[id_turno][rota[i].get('id_pausa')]

                if (dif_inicio > 0):
                    try:
                        delta = delta + dif_inicio
                        id_posicao = i
                    except OverflowError:
                        delta = float('inf')
                if (dif_fim > 0):
                    try:
                        delta = delta + dif_fim
                        id_posicao = i
                    except OverflowError:
                        delta = float('inf')
    else:
        for i in range(len(rota)):
            if (rota[i].get('Tipo') == 'Pausa'):
                if rota[i].get('id_pausa')==id_pausa:

                    dif_inicio =pausas_hora_inicio[id_turno][rota[i].get('id_pausa')] - rota[i].get('Hora Fim')

                    dif_fim = rota[i].get('Hora Inicio')-pausas_hora_fim[id_turno][rota[i].get('id_pausa')]

                    if (dif_inicio > 0):
                        try:
                            delta = delta + dif_inicio
                            id_posicao=i
                        except OverflowError:
                            delta = float('inf')
                    if (dif_fim > 0):
                        try:
                            delta = delta + dif_fim
                            id_posicao=i
                        except OverflowError:
                            delta = float('inf')

                    break


    return delta

def calcular_tempo_medio_passagem(rotas):

    tempo_medio_passagem=[]
    max_diferenca=[]
    posicoes_por_no=[]

    flat_list = [item for sublist in rotas for item in sublist]

    for no in nos:

        tempos_nos = []
        count=0
        total=0
        max=-1

        for paragem in flat_list:

            if paragem.get('posicao')==no.id:

                tempos_nos.append(paragem)

        tempos_nos = sorted(tempos_nos, key=lambda k: k['Hora Fim'])

        posicoes_por_no.append(tempos_nos)

        for posicao in range(len(tempos_nos)-1):

            if tempos_nos[posicao+1].get('Hora Inicio')-tempos_nos[posicao].get('Hora Fim')<0:
                diferenca=0
            else:
                diferenca=tempos_nos[posicao+1].get('Hora Fim')-tempos_nos[posicao].get('Hora Fim')

            count+=1
            total+=diferenca

            if diferenca>max:
                max=diferenca

        if count>0:
            tempo=total/count
            tempo_medio_passagem.append(tempo)

        max_diferenca.append(max)

    # df_posicoes=pd.DataFrame(posicoes_por_no)
    # df_posicoes.to_csv('posicoes_por_no.csv')

    return tempo_medio_passagem

def adiciona_esperas(paragens,id_turno):

    global slot_tempo

    tempo_espera=(turnos[id_turno].fim-turnos[id_turno].inicio)-(paragens[-1].get('Hora Fim')-paragens[0].get('Hora Inicio'))

    #criar slots de tempo para várias pausas

    rotas_alternativas=[]

    rota=paragens.copy()

    numero_esperas=round(tempo_espera/slot_tempo)

    if numero_esperas>0:

        slot_tempo=tempo_espera/numero_esperas

    id_posicoes=[]
    id_testes=[]
    deltas=[]

    diferente = True
    for i in range(len(rota)):
        id_posicao=rota[i].get('posicao')
        if nos[id_posicao].espera==1 and diferente == True:
            id_posicoes.append(i)

        if(i+1<len(rota)):
            if(id_posicao != rota[i + 1].get('posicao')):
                diferente = True
            else:
                diferente = False
        else:
            diferente = True


    if (numero_esperas < 0) :
        numero_esperas = 0

    if numero_esperas>len(id_posicoes):

        try:

            slot_tempo=tempo_espera/len(id_posicoes)
            numero_esperas = round(tempo_espera / slot_tempo)
            for x in itertools.combinations(id_posicoes, numero_esperas):
                id_testes.append(x)


        except:

            slot_tempo=0

    else:

        for x in itertools.combinations(id_posicoes, numero_esperas):
            id_testes.append(x)

    count_combinacao=0
    for combinacao in id_testes:

        rota=paragens.copy()

        combinacao_final=[]

        for i in range(len(combinacao)):
            combinacao_final.append(combinacao[i]+i)

        for id_posicao_espera in combinacao_final:

            id_posicao=rota[id_posicao_espera].get('posicao')

            rota, count = visitar_no(id_posicao, rota, id_posicao_espera, slot_tempo, "Espera", -1)

        delta = calcular_delta(rota,-1,id_turno)

        print('combinação: ' + str(count_combinacao) + '/' + str(len(id_testes)) + ': ' + str(combinacao) + ' delta: ' + str(delta))
        count_combinacao+=1

        deltas.append(delta)

        new_row = {'delta': delta,'rota': rota}

        rotas_alternativas.append(new_row)

    min_delta = math.inf
    best_rota=paragens.copy()

    if len(rotas_alternativas) > 0:
        best_rota = rotas_alternativas[0].get('rota')

    for rota in rotas_alternativas:

        if rota.get('delta') < min_delta:
            best_rota = rota.get('rota')

    paragens = best_rota.copy()

    return paragens

def adicionar_deslocacoes(output, vetor_solucao, i, id_turno):

    deslocacao = 0

    for posicao in range(len(vetor_solucao)):

        deslocacao = 0
        if(vetor_solucao[posicao].get('Tipo') == "Deslocação"):
            #De onde veio?
            pos = posicao -1
            while pos >= 0 and nos[vetor_solucao[pos].get('posicao')].id == nos[vetor_solucao[posicao].get('posicao')].id:
                pos -= 1

            deslocacao = nos[vetor_solucao[pos].get('posicao')].kms[vetor_solucao[posicao].get('posicao')]
            #get_distance(nos[vetor_solucao[pos].get('posicao')].id, nos[vetor_solucao[posicao].get('posicao')].id)

        new_row = {'Numero Voltas': i, 'Turno': id_turno,
                   'Sequência': nos[vetor_solucao[posicao].get('posicao')].id,
                   'Nó': nos[vetor_solucao[posicao].get('posicao')].nome,
                   'Hora Inicio': vetor_solucao[posicao].get('Hora Inicio'),
                   'Hora Fim': vetor_solucao[posicao].get('Hora Fim'),
                   'Tipo': vetor_solucao[posicao].get('Tipo'),
                   'kms': deslocacao}

        output.append(new_row)

    return output

def condensar_paragens(vetor_paragens):

    new_vetor=[]
    index=0

    while index<len(vetor_paragens)-1:
        last_posicao=index
        nova_posicao=index+1

        hora_inicio=vetor_paragens[last_posicao].get('Hora Inicio')
        hora_fim=vetor_paragens[last_posicao].get('Hora Fim')

        while vetor_paragens[nova_posicao].get('posicao') == vetor_paragens[last_posicao].get('posicao'):
            hora_fim=vetor_paragens[nova_posicao].get('Hora Fim')
            if nova_posicao<len(vetor_paragens)-1:
                nova_posicao+=1
            else:
                break

        new={'posicao':vetor_paragens[last_posicao].get('posicao'),'Hora Inicio':hora_inicio,'Hora Fim':hora_fim}
        new_vetor.append(new)
        index = nova_posicao

    return new_vetor

def go_to_incidencia(paragens,posicao_real_escolhida,id_no_chegada,id_no_partida,id_turno):

    count = id_no_partida
    add = 0
    tempo_total = 0
    last_hora_fim=-1
    first_hora_inicio=-1

    while math.fabs(count - id_no_chegada) > 0:
        hora_inicio = paragens[posicao_real_escolhida + add].get('Hora Fim')
        if count < id_no_chegada:
            posicao_anterior = count-1
        else:
            posicao_anterior = count + 1
        if posicao_anterior < len(nos) and posicao_anterior >= 0:
            if first_hora_inicio==-1:
                first_hora_inicio=hora_inicio
            new_row = {'posicao': count, 'Hora Inicio': hora_inicio,
                       'Hora Fim': hora_inicio + get_distance(count, posicao_anterior), 'Tipo': "Deslocação Incidência"}
            add += 1
            tempo_total += get_distance(count, posicao_anterior)
            paragens.insert(posicao_real_escolhida + add, new_row)
        if count < id_no_chegada:
            count += 1
        else:
            count -= 1

    print('deslocação completa')

    print('a resolver incidencia')

    hora_inicio = paragens[posicao_real_escolhida + add].get('Hora Fim')

    if first_hora_inicio==-1:
        first_hora_inicio = paragens[posicao_real_escolhida + add].get('Hora Fim')


    last_hora_fim = hora_inicio + t_medio_incidencia
    new_row = {'posicao': id_no_chegada, 'Hora Inicio': paragens[posicao_real_escolhida + add].get('Hora Fim'),
                   'Hora Fim': hora_inicio + t_medio_incidencia, 'Tipo': "Incidência"}

    tempo_total += t_medio_incidencia

    paragens.insert(posicao_real_escolhida+1+add, new_row)

    count = id_no_chegada
    #add=0

    while math.fabs(count - id_no_partida) > 0:
        hora_inicio = paragens[posicao_real_escolhida + add+1].get('Hora Fim')
        if count < id_no_partida:
            posicao_anterior = count - 1
        else:
            posicao_anterior = count + 1
        if posicao_anterior < len(nos) and posicao_anterior >= 0:
            last_hora_fim=hora_inicio + get_distance(count, posicao_anterior)
            new_row = {'posicao': count, 'Hora Inicio': hora_inicio,
                       'Hora Fim': hora_inicio + get_distance(count, posicao_anterior), 'Tipo': "Deslocação Incidência"}
            add += 1
            tempo_total += get_distance(count, posicao_anterior)
            paragens.insert(posicao_real_escolhida + add+1, new_row)
        if count < id_no_partida:
            count += 1
        else:
            count -= 1

    return paragens,tempo_total, add,last_hora_fim,first_hora_inicio

def filtrar_incidencias(hora_incidencia,sublanco_incidencia):
    nos_incidencias=[]
    for posicao in range(len(hora_incidencia)):
        sublanco = sublanco_incidencia[posicao]
        no_inicio = sublanco.split('-')[0]
        no_inicio = no_inicio.strip()
        id_inicio = -1
        no_fim = sublanco.split('-')[1]
        no_fim = no_fim.strip()
        id_fim = -1
        for no_real in nos:
            if no_inicio in no_real.nome:
                id_inicio = no_real.id
            if no_fim in no_real.nome:
                id_fim = no_real.id

        if id_inicio != -1 and id_fim != -1:
            new_row = {'no_in': id_inicio, 'no_out': id_fim, 'hora': hora_incidencia[posicao]}
            nos_incidencias.append(new_row)
    return nos_incidencias

def limpar_resultado(paragens):

    new_vetor=[]

    count=0

    # while count<len(paragens)-1:

    #   posicao_atual=paragens[count]
        #posicao_seguinte=paragens[count+1]

        #no_atual=posicao_atual.get('posicao')
        #no_seguinte=posicao_seguinte.get('posicao')

        #tipo_atual=posicao_atual.get('Tipo')
        #tipo_seguinte=posicao_seguinte.get('Tipo')

        #hora_inicio=posicao_atual.get('Hora Inicio')
        #hora_fim=posicao_atual.get('Hora Fim')

        #turno_atual=posicao_atual.get('Turno')
        #turno_seguinte=posicao_seguinte.get('Turno')

        #if tipo_atual=='Espera' and no_atual==no_seguinte and turno_atual==turno_seguinte:
            #while no_atual==no_seguinte and (tipo_seguinte=='Espera' or tipo_seguinte=='Deslocação'):
                #hora_fim=posicao_seguinte.get('Hora Fim')
                #count+=1
                #posicao_seguinte=paragens[count+1]
        #new={'Numero Voltas':posicao_atual.get('Numero Voltas'),'Turno':turno_atual,'Sequência':posicao_atual.get('Sequência'),'Nó':posical_atual.get('posicao'),'Hora Inicio':hora_inicio,'Hora Fim':hora_fim,'Tipo':"Espera"}

        #new_vetor.append(new)

    return new_vetor


def verificar_corte(carro, id_turno, n_voltas):
    
    probabilidades_turno = []
    if(id_turno == 0):
        probabilidades_turno = probabilidades_turno_1.copy()
    elif(id_turno == 1):
        probabilidades_turno = probabilidades_turno_2.copy()
    else:
        probabilidades_turno = probabilidades_turno_3.copy()

    #Tempos em minutos
    tempo_patrulha = 0
    tempo_nos = 0
    tempo_incidencias = 0

    #Calcular tempos_nos e tempos patrulhas
    for index in range(len(carro)-1):
        tempo_patrulha += get_distance(carro[index], carro[index+1]) * n_voltas
        tempo_nos += tempos_nos_norte_sul[carro[index]]
        tempo_nos += tempos_nos_sul_norte[carro[index]]
        tempo_incidencias += probabilidades_turno[carro[index]+1] * t_medio_incidencia

    tempo_nos += (tempos_nos_norte_sul[carro[-1]] + tempos_nos_sul_norte[carro[-1]]) / 2

    #Tempo turno sem pausas
    tempo_turno = turnos[id_turno].fim - turnos[id_turno].inicio - 60 - 30

    tempo_total = tempo_patrulha + tempo_nos + tempo_incidencias

    if(tempo_total > tempo_turno):
        return False
    else:
        return True




    #Falta tempo incidências
