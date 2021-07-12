import pandas as pd
import math
from classes import *
global combinacoes

combinacoes=[]

def import_data():

    global cos
    global sublancos
    global nos
    global turnos
    global satisfeitos
    global incidencias
    global incidencias_visitadas

    cos=[]
    sublancos=[]
    nos=[]
    satisfeitos=[]
    incidencias_visitadas=[]

    df_nos=pd.read_csv('dados/Nos Feira + Mealhada.csv',sep=',',encoding='iso-8859-1')

    df_sublancos=pd.read_csv('dados/sublanços, nós Feira + Mealhada.csv',sep=',',encoding='iso-8859-1')
    lista_cos=df_nos['CO'].tolist()
    lista_nos=df_nos['Nó'].tolist()
    lista_sublancos=df_nos['Sublanço'].tolist()
    is_co=df_nos['CO?'].tolist()
    is_pausa=df_nos['pausa'].tolist()
    is_almoco=df_nos['almoco'].tolist()
    is_vistoria=df_nos['vistoria'].tolist()

    # ler cos

    unique_co=list(set(lista_cos))

    for index in range(len(unique_co)):
        lista_sublancos_no=df_nos[df_nos['CO']==unique_co[index]].Sublanço.unique().tolist()
        new_co=co(index,unique_co[index])
        new_co.lista_sublancos=lista_sublancos_no
        cos.append(new_co)

    # ler sublanços
    unique_sublancos=list(set(lista_sublancos))

    for index in range(len(unique_sublancos)):
        co_sublanco=df_nos[df_nos['Sublanço']==unique_sublancos[index]].CO.unique().tolist()
        id_co = -1
        for pos_co in range(len(cos)):
            if cos[pos_co].nome==co_sublanco[0]:
                id_co=cos[pos_co].id
                break
        new_sublanco=sublanco(index,unique_sublancos[index],id_co)
        sublancos.append(new_sublanco)

    unique_nos = lista_nos.copy()

    df_nos_sublancos = pd.read_csv('dados/sublanços, nós Feira + Mealhada.csv', sep=',', encoding='iso-8859-1')
    descricao_sublanco=df_nos_sublancos['Sublanço'].tolist()
    descricao_no=df_nos_sublancos['Nó'].tolist()

    for index in range(len(unique_nos)):

        sublanco_no=df_nos_sublancos[df_nos_sublancos['Nó']==unique_nos[index]].Sublanço.unique().tolist()
        co_no = df_nos[df_nos['Nó'] == unique_nos[index]].CO.unique().tolist()
        id_sublancos = []
        id_co=-1

        for novo_sublanco in sublanco_no:
            for pos_sublanco in range(len(sublancos)):
                if sublancos[pos_sublanco].nome==novo_sublanco:
                    id_sublanco=sublancos[pos_sublanco].id
                    id_sublancos.append(id_sublanco)
                    sublancos[pos_sublanco].lista_nos.append(index)

        for new_co in cos:
            if new_co.nome==co_no[0]:
                new_co.id_no=index
                if is_co[index]==1:
                    id_co=new_co.id
                break

        new_no=no(index,unique_nos[index],is_pausa[index],is_almoco[index],is_vistoria[index],id_co)

        new_no.lista_sublancos=id_sublancos
        nos.append(new_no)

    #ler distancias

    df_distancias=pd.read_csv('dados/out_distdur_api.csv',sep=',',encoding='iso-8859-1')

    for index in range(len(nos)):

        nos[index].distancias=[0]*len(nos)
        temp=df_distancias[df_distancias['Stop Start']==nos[index].nome]
        velocidade=80

        out=temp['Stop End'].tolist()
        dist = temp['Duration (min)'].tolist()

        for pos_no_fim in range(len(out)):

            no_final=out[pos_no_fim]

            for j in range(len(nos)):
                if nos[j].nome==no_final:
                    nos[index].distancias[j]=dist[pos_no_fim]*120/velocidade

    # ler turnos

    turnos=[]

    df_turnos=pd.read_csv('dados/03. turnos.csv',sep=",",encoding='iso-8859-1')
    inicio=df_turnos['inicio'].tolist()
    pausa=df_turnos['pausa'].tolist()
    almoco=df_turnos['almoco'].tolist()
    fim=df_turnos['fim'].tolist()

    # ler incidencias

    incidencias=[]

    df_incidencias=pd.read_csv('dados/02. ocorrencias.csv',sep=",",encoding='iso-8859-1')
    df_incidencias['Hora']=df_incidencias['Hora']*60-7*60
    df_incidencias.sort_values(by='Hora',ascending=True)
    minuto_visita=df_incidencias['Hora'].tolist()
    descricao_no = df_incidencias['Sublanço'].tolist()

    for pos_descricao in range(len(descricao_no)):
        descricao=descricao_no[pos_descricao]
        for sublanco_comparacao in sublancos:
            if descricao==sublanco_comparacao.nome:
                new_incidencia=[sublanco_comparacao.lista_nos[0],sublanco_comparacao.lista_nos[1],minuto_visita[pos_descricao]]
                incidencias.append(new_incidencia)
                incidencias_visitadas.append(False)
                break

    for index in range(len(inicio)):

        if index==0:

            new_turno=turno(index,inicio[index],pausa[index],almoco[index],fim[index])
            turnos.append(new_turno)

    global max_visitas
    max_visitas = 180

    satisfeitos=[[False] * len(nos)] * len(turnos)

def get_distance(x,y):

    min_dist=999999

    if nos[x].distancias[y]<min_dist:
        min_dist=nos[x].distancias[y]

    if nos[y].distancias[x] < min_dist:
        min_dist = nos[y].distancias[x]

    return int(min_dist)

def gerar_combinacoes(lista_sublancos,min_comb):

    global vetor_solucao

    indices_a_manter = []
    for posicao in range(len(incidencias_visitadas)):
        if incidencias_visitadas[posicao] == False:
            indices_a_manter.append(posicao)

    if min_comb==0:
        temp_incidencias = indices_a_manter.copy()
        min_sublanco = min(lista_sublancos)
        max_sublanco = max(lista_sublancos)
        max_diferenca = 1
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

def get_next_posicao(new_carro,lista_sublancos):

    if len(lista_sublancos)==1 or len(new_carro)==0:
        nova_posicao=lista_sublancos[0]

    else:
        posicao_atual=new_carro[-1]

        if len(new_carro)==1:
            posicao_anterior=min(lista_sublancos)
        else:
            posicao_anterior=new_carro[-2]

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

def atualizar_vetor(id_posicao,id_turno,new_carro,vetor_passos,tempo_adicional,tipo):

    anterior=0

    tipo_anterior="none"

    if len(vetor_passos)>0:

        posicao_anterior=vetor_passos[-1].get('posicao')

        hora_fim_atual=get_distance(posicao_anterior,id_posicao)

        anterior=vetor_passos[-1].get('Hora Fim')

        tipo_anterior = vetor_passos[-1].get('Tipo')

    else:

        hora_fim_atual=turnos[id_turno].inicio

    new_row = { 'posicao': id_posicao, 'Hora Inicio': hora_fim_atual + anterior,
               'Hora Fim': hora_fim_atual + anterior + tempo_adicional, 'Tipo': tipo}

    vetor_passos.append(new_row)

    new_carro.append(id_posicao)

    return new_carro,vetor_passos

def adicionar_posicao(id_posicao,tipo_deslocacao,vetor_carro,vetor_passos,vetor_sublancos,id_turno):

    tempo_adicional=0

    if tipo_deslocacao=='Pausa':
        tempo_adicional=10
    elif tipo_deslocacao=='Almoço':
        tempo_adicional = 40
    elif tipo_deslocacao=='Visitar Nó':
        tempo_adicional = 10
    elif tipo_deslocacao=='Vistoria':
        tempo_adicional = 10

    if id_posicao==-1:

        nova_posicao=get_next_posicao(vetor_carro,vetor_sublancos)

        if nova_posicao not in lista_sublancos:
            if nova_posicao>max(lista_sublancos):
                nova_posicao=max(lista_sublancos)
            else:
                nova_posicao = min(lista_sublancos)
    else:

        nova_posicao=id_posicao

    vetor_carro,vetor_passos=atualizar_vetor(nova_posicao,id_turno,vetor_carro,vetor_passos,tempo_adicional,tipo_deslocacao)

    return vetor_carro,vetor_passos

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

def precisa_paragem(lista_sublancos,new_rota,new_tempo_paragens,id_turno):

    pausa = turnos[id_turno].pausa
    almoco = turnos[id_turno].almoco
    fim = turnos[id_turno].fim - 50
    tipo_paragem='Pausa'

    tempo=new_tempo_paragens[-1].get('Hora Fim')

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

    posicao_objetivo = -1

    if len(new_rota) > 0:
        posicao_atual = new_rota[-1]
        posicao_objetivo = -1
        diferenca_min = 99

        if math.fabs(tempo- pausa)<= 60 and n_pausas==0 :
            tempo_a_verificar = pausa
            tipo_paragem='Pausa'
            for id_no in lista_sublancos:
                no=nos[id_no]
                if no.pausa == 1:
                    diferenca = get_distance(no.id, posicao_atual)
                    if diferenca < diferenca_min:
                        posicao_objetivo = no.id
                        diferenca_min = diferenca
            if posicao_objetivo==-1:
                for no in nos:
                    if no.pausa == 1 and no not in lista_sublancos:
                        diferenca = get_distance(no.id, posicao_atual)
                        if diferenca < diferenca_min:
                            posicao_objetivo = no.id
                            diferenca_min = diferenca

        elif math.fabs(tempo - almoco)<=60 and n_almocos == 0:
            tempo_a_verificar = almoco
            tipo_paragem = 'Almoço'
            for id_no in lista_sublancos:
                no = nos[id_no]
                if no.almoco == 1:
                    diferenca = get_distance(no.id, posicao_atual)
                    if diferenca < diferenca_min:
                        posicao_objetivo = no.id
                        diferenca_min = diferenca
            if posicao_objetivo == -1:
                for no in nos:
                    if no.almoco == 1 and no not in lista_sublancos:
                        diferenca = get_distance(no.id, posicao_atual)
                        if diferenca < diferenca_min:
                            posicao_objetivo = no.id
                            diferenca_min = diferenca
        elif n_fim == 0 and math.fabs(tempo-fim)<=30:
            tempo_a_verificar = fim
            tipo_paragem = 'Fim'
            posicao_objetivo = new_rota[0]
            diferenca = get_distance(posicao_objetivo, posicao_atual)
            diferenca_min = diferenca

    return posicao_objetivo,tipo_paragem,new_rota,new_tempo_paragens

def threshold(new_tempo_paragens,lista_sublancos):

    tempo_visita=[180]*len(nos)

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
                tempo_visita[index]=180
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

def go_to(id_paragem,lista_sublancos,tipo_paragem,new_rota,new_tempo_paragens,id_turno):

    posicao_inicial=new_tempo_paragens[-1].get('posicao')

    if posicao_inicial <= id_paragem:
        for posicao in range(posicao_inicial, id_paragem+1):
            if posicao==id_paragem:
                new_rota, new_tempo_paragens=adicionar_posicao(posicao,tipo_paragem,new_rota,new_tempo_paragens,lista_sublancos,id_turno)
            else:
                new_rota, new_tempo_paragens = adicionar_posicao(posicao, "Deslocação", new_rota, new_tempo_paragens,
                                                                 lista_sublancos, id_turno)
    else:
        for posicao in range(posicao_inicial, id_paragem-1, -1):
            tempo = get_distance(posicao, posicao - 1)
            if posicao==id_paragem:
                new_rota, new_tempo_paragens=adicionar_posicao(posicao,tipo_paragem,new_rota,new_tempo_paragens,lista_sublancos,id_turno)
            else:
                new_rota, new_tempo_paragens = adicionar_posicao(posicao, "Deslocação", new_rota, new_tempo_paragens,
                                                                 lista_sublancos, id_turno)

    min_dif=999
    id_final=-1
    if id_paragem not in lista_sublancos:
        for posicao in lista_sublancos:
            diferenca=math.fabs(posicao-id_paragem)
            if diferenca<min_dif:
                id_final=posicao
                min_dif=diferenca

    if id_final!=-1:
        if id_paragem <= id_final:
            for posicao in range(id_paragem, id_final + 1):
                new_rota, new_tempo_paragens = adicionar_posicao(posicao, "Deslocação", new_rota,
                                                                     new_tempo_paragens,
                                                                     lista_sublancos, id_turno)
        else:
            for posicao in range(id_paragem, id_final - 1, -1):

                new_rota, new_tempo_paragens = adicionar_posicao(posicao, "Deslocação", new_rota,
                                                                 new_tempo_paragens,
                                                                 lista_sublancos, id_turno)


    return new_rota, new_tempo_paragens

def verificar_ultima_paragem(lista_sublancos,new_rota,new_tempo_paragens,id_turno):

    id_paragem, tipo_paragem, new_rota, new_tempo_paragens = precisa_paragem(lista_sublancos, new_rota,
                                                                             new_tempo_paragens, id_turno)
    temp_rota=new_rota.copy()
    temp_tempos=new_tempo_paragens.copy()
    temp_rota, temp_paragens = adicionar_posicao(-1, "Deslocação", temp_rota, temp_tempos, lista_sublancos,
                                                 id_turno)
    temp_rota, temp_paragens = adicionar_posicao(-1, "Deslocação", temp_rota, temp_tempos, lista_sublancos,
                                                 id_turno)
    temp_posicao_objetivo, temp_tipo_paragem, temp_new_rota, temp_new_tempo_paragens = precisa_paragem(lista_sublancos,
                                                                                                       temp_rota,
                                                                                                       temp_paragens,
                                                                                                       id_turno)

    if temp_posicao_objetivo != -1 and temp_tipo_paragem == tipo_paragem:
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

    new_visitas=[False]*len(incidencias)

    for index in range(len(incidencias_visitadas)):
        if index in incidencias_a_considerar:
            new_visitas[index]=False
        else:
            new_visitas[index]=True

    new_rota=carro_origem.copy()

    new_tempo_paragens=tempo_paragens.copy()

    posicao_inicial=carro_origem[1]

    if posicao_inicial not in lista_sublancos:
        if posicao_inicial>max(lista_sublancos):
            new_rota, new_tempo_paragens = go_to(max(lista_sublancos), lista_sublancos, "Inicio", new_rota,
                                                 new_tempo_paragens, 0)
        else:
            new_rota, new_tempo_paragens = go_to(min(lista_sublancos), lista_sublancos, "Inicio", new_rota,
                                                 new_tempo_paragens, 0)

    # if carro_origem[1]>carro_origem[0]:
    #     sentido='Sul'
    # else:
    #     sentido='Norte'
    #
    # if sentido=='Norte' and len(lista_sublancos)>0:
    #     if posicao_inicial==0:
    #         new_rota, new_tempo_paragens = adicionar_posicao(0, "Deslocação", new_rota,
    #                                                          new_tempo_paragens,
    #                                                          lista_sublancos, id_turno)
    #     else:
    #         new_rota, new_tempo_paragens = adicionar_posicao(posicao_inicial-1, "Deslocação", new_rota, new_tempo_paragens,
    #                                                      lista_sublancos, id_turno)
    #
    # elif sentido=='Sul' and len(lista_sublancos)>0:
    #     if posicao_inicial==len(nos):
    #         new_rota, new_tempo_paragens = adicionar_posicao(posicao_inicial, "Deslocação", new_rota, new_tempo_paragens,
    #                                                      lista_sublancos, id_turno)
    #     else:
    #         new_rota, new_tempo_paragens = adicionar_posicao(posicao_inicial + 1, "Deslocação", new_rota,
    #                                                          new_tempo_paragens,
    #                                                          lista_sublancos, id_turno)

    while new_tempo_paragens[-1].get('Hora Fim')<8*60:

        id_paragem,tipo_paragem=verificar_ultima_paragem(lista_sublancos, new_rota, new_tempo_paragens, id_turno)

        id_incidencia,posicao_incidencia=verificar_ultima_incidencia(incidencias_a_considerar, new_rota, new_tempo_paragens, new_visitas, id_turno)

        id_threshold=threshold(new_tempo_paragens,lista_sublancos)

        if id_paragem!=-1:

            new_rota, new_tempo_paragens = go_to(id_paragem,lista_sublancos,tipo_paragem,new_rota,new_tempo_paragens,0)  #verificar se ele está a ir a um sublanço dele e se assim for assume o sentido que está a ir. se sai do sublanços sentido oposto que esta a ir

        elif id_incidencia!=-1:

            new_rota, new_tempo_paragens = go_to(id_incidencia,lista_sublancos,"Incidência",new_rota,new_tempo_paragens,0)  #verificar se ele está a ir a um sublanço dele e se assim for assume o sentido que está a ir. se sai do sublanços sentido oposto que esta a ir

            new_visitas[posicao_incidencia]=True

        elif id_threshold!=-1:

            new_rota, new_tempo_paragens = go_to(id_threshold, lista_sublancos, "Tempo Sublanço",new_rota,new_tempo_paragens,0)

        else:

            new_rota, new_tempo_paragens = adicionar_posicao(-1,"Deslocação", new_rota, new_tempo_paragens,lista_sublancos,id_turno)

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
            if (i <= index) and i>max_co and is_co!=-1:
                found = True
                max_co=i
                break


    if (sentido == "Sul"):
        for no in nos:
            i = no.id
            is_co = no.co
            if (i >= index) and i<min_co and is_co!=-1:
                found = True
                min_co=i
                break

    if found == False:
        return -1

    elif sentido=='Norte':
        return max_co

    elif sentido=='Sul':
        return min_co

def verificar_carro_iniciado(id_turno,index,vetor_sublancos,carro,passos,sentido,descer):

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


    if len(carro) == 0 and dif_incremental<=min_dif:
        if co > -1:
            carro,passos=adicionar_posicao(co,"Início",carro,passos,vetor_sublancos,id_turno)
            if co!=0:
                carro,passos = adicionar_posicao(co+incrementar, "Início", carro,passos, vetor_sublancos,
                                                         id_turno)
                posicao=co+incrementar

                if posicao>id_range:

                    for id_pos in range(posicao-1,id_range-1,-1):

                        carro, passos = adicionar_posicao(id_pos, "Início", carro, passos, vetor_sublancos,
                                                          id_turno)

                elif posicao<id_range:

                    for id_pos in range(posicao+1,id_range+1):

                        carro, passos = adicionar_posicao(id_pos, "Início", carro, passos, vetor_sublancos,
                                                          id_turno)



    return carro,passos

def verificar_restricoes(new_tempo_paragens,lista_sublancos,vetor_incidencias,new_visitas):

    valor =True

    tempo_visita=[180]*len(nos)

    for posicao in range(1,len(new_tempo_paragens)):

        id_posicao= new_tempo_paragens[posicao].get('posicao')

        tempo_anterior=new_tempo_paragens[posicao-1].get('Hora Fim')
        tempo_atual = new_tempo_paragens[posicao].get('Hora Fim')

        tempo_retirar=tempo_atual-tempo_anterior

        for index in range(len(tempo_visita)):

            if index==id_posicao:
                tempo_visita[index]=180
            elif index in lista_sublancos:
                tempo_visita[index]=tempo_visita[index]-tempo_retirar
                if tempo_visita[index]<0:
                    valor=False

    for posicao_incidencia in range(len(incidencias_a_considerar)):
        if new_visitas[posicao_incidencia]==False:
            valor=False

    return valor

def limpar_incidencias(best_incidencias):

    incidencias_a_manter=[]

    for posicao in range(len(incidencias_visitadas)):
        if incidencias_visitadas[posicao] == False:
            incidencias_a_manter.append(posicao)

    for index in range(len(best_incidencias)):
        posicao=best_incidencias[index]
        print('posicao ' + str(posicao))
        if posicao in incidencias_a_manter:
            incidencias_a_manter.remove(posicao)
        incidencias_visitadas[posicao]=True

def verificar_best(temp_rotas,temp_tempos,temp_incidencias,best_rota,best_tempo,best_incidencias,guardar_best,temp_sub,best_sub):

    j=0
    compara_1=0
    compara_2=0

    if len(temp_sub)>len(best_sub):
        best_rota = temp_rotas
        best_tempo = temp_tempos
        best_incidencias = temp_incidencias
        best_lista_sublancos=temp_sub
        guardar_best = True

        return best_rota, best_tempo, best_incidencias, guardar_best

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
            best_rota = temp_rotas
            best_tempo = temp_tempos
            best_incidencias = temp_incidencias
            best_lista_sublancos=temp_sub
            guardar_best = True

            return best_rota,best_tempo,best_incidencias,guardar_best

        j += 1

    return best_rota,best_tempo,best_incidencias,guardar_best,best_sub

import_data()

lista_sublancos=[0]
carro_1_1=[]
passos_1_1=[]
carro_1_2=[]
passos_1_2=[]
carro_2_1=[]
passos_2_1=[]
carro_2_2=[]
passos_2_2=[]
carros=[[]]
passos=[[]]
temp_rotas=[]
temp_tempos=[]
temp_incidencias=[]
stop_condition=False
rotas=[]
lista_sublancos_solucao=[]
tempos=[]
incidencias_solucao=[]
best_rota=[]
best_tempo=[]
best_incidencias=[]

indice_atual = 0

while stop_condition==False:

    carros=[]
    passos=[]

    carro_temp=[]
    passos_temp=[]
    carro_temp,passos_temp=atualizar_vetor(2,0,carro_temp,passos_temp,0,"inicio")
    carro_temp,passos_temp=atualizar_vetor(1, 0, carro_temp, passos_temp, 0, "inicio")

    carros.append(carro_temp)
    passos.append(passos_temp)
    # carro_1_1,passos_1_1=verificar_carro_iniciado(0,indice_atual,lista_sublancos,carro_1_1,passos_1_1,'Norte',0)
    # carros.append(carro_1_1)
    # passos.append(passos_1_1)
    # carro_1_2,passos_1_2=verificar_carro_iniciado(0, indice_atual, lista_sublancos, carro_1_2,passos_1_2, 'Norte', 1)
    # carros.append(carro_1_2)
    # passos.append(passos_1_2)
    # carro_2_1,passos_2_1= verificar_carro_iniciado(0, indice_atual, lista_sublancos,  carro_2_1,passos_2_1, 'Sul', 0)
    # carros.append(carro_2_1)
    # passos.append(passos_2_1)
    # carro_2_2,passos_2_2 = verificar_carro_iniciado(0, indice_atual, lista_sublancos, carro_2_2,passos_2_2, 'Sul', 1)
    # carros.append(carro_2_2)
    # passos.append(passos_2_2)

    guardar_best = True
    min_comb=0

    while guardar_best:

        if max(lista_sublancos)+1<len(nos):
            lista_sublancos.append(lista_sublancos[-1] + 1)

        indice_atual = max(lista_sublancos)

        guardar_best=False

        combinacoes = []

        gerar_combinacoes(lista_sublancos,min_comb)

        print('combinações para os sublancos ' + str(len(lista_sublancos)) + ' = ' + str(len(combinacoes)))

        for posicao_carro in range(len(carros)):
            carro=carros[posicao_carro]

            if len(carro)>0:

                for incidencias_a_considerar in combinacoes:

                    new_rota=[]

                    new_rota, new_tempo_paragens,new_visitas=criar_rota_particular(lista_sublancos, incidencias_a_considerar, 0, carro,passos[posicao_carro])

                    print('Incidencias ' + str(incidencias_a_considerar))
                    print('Incidencias ' + str(new_visitas))
                    print('sublancos '+ str(lista_sublancos))
                    print('rota '+str(new_rota))

                    verificou_restricoes=verificar_restricoes(new_tempo_paragens,lista_sublancos,incidencias_a_considerar,new_visitas)

                    print('cumpre? ' + str(verificou_restricoes))

                    if best_rota == []:
                        best_rota = new_rota
                        best_tempo = new_tempo_paragens
                        guardar_best=True
                        best_lista_sublancos=lista_sublancos
                        best_incidencias=incidencias_a_considerar

                    if verificou_restricoes==True:
                        best_rota,best_tempo,best_incidencias,guardar_best,best_lista_sublancos=verificar_best(new_rota,new_tempo_paragens,incidencias_a_considerar,best_rota,best_tempo,best_incidencias,guardar_best,lista_sublancos,best_lista_sublancos) #escolher o melhor (com incidencias com menor indice)

                    print('alterado? ' +str(guardar_best))

        if guardar_best==True and indice_atual==len(nos)-1:
            min_comb+=1

    rotas.append(best_rota)
    tempos.append(best_tempo)
    incidencias_solucao.append(best_incidencias)
    lista_sublancos_solucao.append(best_lista_sublancos)
    best_rota=[]
    best_tempo=[]

    limpar_incidencias(best_incidencias)
    print('incidencias visitas' + str(incidencias_visitadas))

    stop_condition = True
    if all(incidencias_visitadas) == False:
        stop_condition = False
    if indice_atual < len(nos):
        stop_condition = False

    temp_lista=lista_sublancos.copy()

    for index in lista_sublancos:
        if index!=max(lista_sublancos):
            temp_lista.remove(index)

    lista_sublancos=temp_lista.copy()

    if len(lista_sublancos)==1 and lista_sublancos[-1]==len(nos)-1:
        lista_sublancos.insert(0,len(nos)-2)

print('finish')







