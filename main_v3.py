import pandas as pd
import math
from classes import *
global combinacoes
global count_rota
global resposta

resposta=3*60
combinacoes=[]
count_rota=0

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

    df_nos=pd.read_csv('dados/01. nos.csv',sep=',',encoding='iso-8859-1')

    df_sublancos=pd.read_csv('dados/05. sublancos nos.csv',sep=',',encoding='iso-8859-1')
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

    df_nos_sublancos = pd.read_csv('dados/05. sublancos nos.csv', sep=',', encoding='iso-8859-1')
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
        velocidade=60

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
    max_visitas = resposta

    satisfeitos=[[False] * len(nos)] * len(turnos)

def get_distance(x,y):

    min_dist=999999

    if nos[x].distancias[y]<min_dist:
        min_dist=nos[x].distancias[y]

    if nos[y].distancias[x] < min_dist:
        min_dist = nos[y].distancias[x]

    if min_dist==0:
        min_dist=2

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

def visitar_no(id_no,rota,passos,posicao,tempo_no,tipo):

    new_row={'posicao':id_no,'Hora Inicio':passos[posicao].get('Hora Fim'),'Hora Fim':tempo_no+passos[posicao].get('Hora Fim'),'Tipo':tipo}
    passos.insert(posicao,new_row)
    rota.insert(posicao,id_no)

    for index in range(posicao+1,len(passos)):

        new_row= {'posicao':passos[index].get('posicao'),'Hora Inicio':passos[index].get('Hora Inicio')+tempo_no,'Hora Fim':passos[index].get('Hora Fim')+tempo_no,'Tipo':passos[index].get('Tipo')}
        passos[index]=new_row

    count=0
    for index in range(len(passos)):
        if passos[index].get('Tipo')=='Visitar Nó':
            count+=1

    return rota, passos,count

def adicionar_posicao(id_posicao,tipo_deslocacao,vetor_carro,vetor_passos,vetor_sublancos,id_turno):

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

        elif almoco-tempo<=45 and n_almocos == 0:
            tempo_a_verificar = almoco-tempo
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

def go_to(id_paragem,lista_sublancos,tipo_paragem,new_rota,new_tempo_paragens,id_turno):

    posicao_inicial=new_tempo_paragens[-1].get('posicao')

    if posicao_inicial <= id_paragem:
        for posicao in range(posicao_inicial, id_paragem+1):
            if posicao==id_paragem:
                new_rota, new_tempo_paragens= adicionar_posicao(posicao,tipo_paragem,new_rota,new_tempo_paragens,lista_sublancos,id_turno)
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
    if (id_paragem not in lista_sublancos) and (tipo_paragem!='Fim' and tipo_paragem!='Início'):
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
    tempo_no=10
    tempo_necessario_nos=len(lista_sublancos)*tempo_no
    tempo_abertura=8*60
    tempo_abertura=tempo_abertura-tempo_necessario_nos

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

                # if posicao>id_range:
                #
                #     for id_pos in range(posicao-1,id_range-1,-1):
                #
                #         carro, passos = adicionar_posicao(id_pos, "Início", carro, passos, vetor_sublancos,
                #                                           id_turno)
                #
                # elif posicao<id_range:
                #
                #     for id_pos in range(posicao+1,id_range+1):
                #
                #         carro, passos = adicionar_posicao(id_pos, "Início", carro, passos, vetor_sublancos,
                #                                           id_turno)



    return carro,passos

def verificar_restricoes(new_tempo_paragens,lista_sublancos,vetor_incidencias,new_visitas):

    valor =True

    soma=0

    tempo_visita=[resposta]*len(nos)

    # n_almocos=0
    # n_pausas=0
    # n_fim=0
    #
    # for index in range(len(new_tempo_paragens)):
    #     if new_tempo_paragens[index].get('Tipo')=='Pausa':
    #         n_pausas+=1
    #     elif new_tempo_paragens[index].get('Tipo')=='Pausa':
    #         n_almocos+=1
    #     elif new_tempo_paragens[index].get('Tipo')=='Fim':
    #         n_fim+=1
    #
    # if n_pausas==0 or n_almocos==0 or n_fim==0:
    #     valor=False

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
                if tempo_visita[index]<0:
                    valor=False
                    soma+=tempo_visita[index]

    # temp=[180]*len(tempo_visita)
    # for index in range(len(tempo_visita)):
    #     soma += tempo_visita[index]-temp[index]

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
        print('posicao ' + str(posicao))
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

def adicionar_nos(new_rota, new_tempo_paragens, lista_sublancos,new_visitas):

    temp_rota=new_rota.copy()
    temp_paragens=new_tempo_paragens.copy()

    melhor_rota = temp_rota.copy()
    melhor_paragem = temp_paragens.copy()

    count=0

    for no in lista_sublancos:

        posicao=0
        total=len(temp_paragens)
        max_soma = -9999

        while posicao<total:

            id_posicao=temp_paragens[posicao].get('posicao')

            if id_posicao==no:

                temp_rota_2=temp_rota.copy()
                temp_paragens_2=temp_paragens.copy()

                if nos[no].vistoria!=-1:
                    tempo_add=10
                else:
                    tempo_add=20

                temp_rota_2,temp_paragens_2,count=visitar_no(id_posicao,temp_rota_2,temp_paragens_2,posicao,tempo_add,"Visitar Nó")

                melhor_rota = temp_rota_2.copy()
                melhor_paragem = temp_paragens_2.copy()

                valor,soma=verificar_restricoes(temp_paragens_2,lista_sublancos,[],new_visitas)

                if soma>max_soma:
                    max_soma=soma
                    melhor_rota=temp_rota_2.copy()
                    melhor_paragem=temp_paragens_2.copy()

            posicao += 1

        temp_rota=melhor_rota.copy()
        temp_paragens=melhor_paragem.copy()


    return temp_rota,temp_paragens


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

    carro_1_1,passos_1_1=verificar_carro_iniciado(0,indice_atual,lista_sublancos,carro_1_1,passos_1_1,'Norte',0)
    carros.append(carro_1_1)
    passos.append(passos_1_1)
    carro_1_2,passos_1_2=verificar_carro_iniciado(0, indice_atual, lista_sublancos, carro_1_2,passos_1_2, 'Norte', 1)
    carros.append(carro_1_2)
    passos.append(passos_1_2)
    carro_2_1,passos_2_1= verificar_carro_iniciado(0, indice_atual, lista_sublancos,  carro_2_1,passos_2_1, 'Sul', 0)
    carros.append(carro_2_1)
    passos.append(passos_2_1)
    carro_2_2,passos_2_2 = verificar_carro_iniciado(0, indice_atual, lista_sublancos, carro_2_2,passos_2_2, 'Sul', 1)
    carros.append(carro_2_2)
    passos.append(passos_2_2)

    guardar_best = True
    min_comb=0

    while guardar_best:

        if max(lista_sublancos)+1<len(nos):
            lista_sublancos.append(lista_sublancos[-1] + 1)

        indice_atual = max(lista_sublancos)

        guardar_best=False

        combinacoes = []

        gerar_combinacoes(lista_sublancos,min_comb)

        for posicao_carro in range(len(carros)):
            carro=carros[posicao_carro]

            if len(carro)>0:

                for incidencias_a_considerar in combinacoes:

                    if compara_incidencias(incidencias_a_considerar,best_incidencias)==True:

                        new_rota=[]

                        new_rota, new_tempo_paragens,new_visitas=criar_rota_particular(lista_sublancos, incidencias_a_considerar, 0, carro,passos[posicao_carro])


                        verificou_restricoes,soma=verificar_restricoes(new_tempo_paragens,lista_sublancos,incidencias_a_considerar,new_visitas)

                        print('minimo sublanço ' + str(min(lista_sublancos)) + str(' carro ') + str(
                            carro) + ' len sublanços ' + str(len(lista_sublancos)) + ' len incidencias ' + str(
                            incidencias_a_considerar) + ' cumpre ' + str(verificou_restricoes))



                        if best_rota == []:
                            best_rota = new_rota.copy()
                            best_tempo = new_tempo_paragens.copy()
                            guardar_best=True
                            best_lista_sublancos=lista_sublancos.copy()
                            best_incidencias=incidencias_a_considerar.copy()

                        if verificou_restricoes==True:

                            best_rota,best_tempo,best_incidencias,guardar_best,best_lista_sublancos=verificar_best(new_rota,new_tempo_paragens,incidencias_a_considerar,best_rota,best_tempo,best_incidencias,guardar_best,lista_sublancos,best_lista_sublancos) #escolher o melhor (com incidencias com menor indice)

        if guardar_best==True and indice_atual==len(nos)-1:
            min_comb+=1

    rotas.append(best_rota)
    tempos.append(best_tempo)
    incidencias_solucao.append(best_incidencias)
    lista_sublancos_solucao.append(best_lista_sublancos)
    limpar_incidencias(best_incidencias)

    best_rota=[]
    best_tempo=[]
    best_incidencias=[]
    best_lista_sublancos=[]


    print('incidencias visitas' + str(incidencias_visitadas))

    flat_list = [item for sublist in lista_sublancos_solucao for item in sublist]

    stop_condition = True
    if all(incidencias_visitadas) == False:
        stop_condition = False
    if len(flat_list)!=len(nos):
        stop_condition=False

    temp_lista=lista_sublancos.copy()

    for index in lista_sublancos:
        if index!=max(lista_sublancos):
            temp_lista.remove(index)

    lista_sublancos=temp_lista.copy()

    if len(lista_sublancos)==1 and lista_sublancos[-1]==len(nos)-1:
        lista_sublancos.insert(0,len(nos)-2)

print('finish')

def delete_vaivem(rotas,tempos):

    guardar_rotas=[]
    guardar_passagens=[]

    temp_rotas=rotas.copy()
    temp_tempos=tempos.copy()

    for index in range(len(temp_rotas)):

        new_rota=temp_rotas[index].copy()
        new_tempo=temp_tempos[index].copy()

        vaivem=0
        posicao=len(new_tempo)-1
        posicao_inicial=-1
        posicao_final=[]

        while posicao>=2:

            if new_tempo[posicao-1].get('posicao')==new_tempo[posicao].get('posicao'):
                if posicao_inicial==-1:
                    posicao_inicial=posicao
                else:
                    posicao_final.append(posicao)

            if new_tempo[posicao].get('Tipo')=='Incidência' :
                posicao=-1

            posicao-=1

        print('posicao inicial ' + str(posicao_inicial))

        print('posicao final ' + str(posicao_final))

        valor_max=999
        valores=[]
        for posicao_fim in posicao_final:

            temp_2=new_tempo.copy()

            del temp_2[posicao_inicial:posicao_fim]

            valor,soma=verificar_restricoes(temp_2,lista_sublancos_solucao[index],[],new_visitas)
            valores.append(valor)
            if posicao_fim<valor_max and valor==True:
                valor_max=posicao_fim

            print(valor)

        if any(valores)==True:

            print(len(new_tempo))

            del new_tempo[valor_max:posicao_inicial]
            del new_rota[valor_max:posicao_inicial]
            guardar_rotas.append(new_rota)
            guardar_passagens.append(new_tempo)
            print(len(new_tempo))

        print('finiso')

    return guardar_rotas,guardar_passagens

guardar_rotas,guardar_passagens=delete_vaivem(rotas,tempos)

for index in range(len(rotas)):
    temp_rota=rotas[index].copy()
    temp_passos=tempos[index].copy()
    new_rota, new_tempo_paragens=adicionar_nos(temp_rota, temp_passos, lista_sublancos,[True]*len(incidencias))

output=[]

vetor_solucao=tempos.copy()

for index in range(len(vetor_solucao)):

    for posicao in range(len(vetor_solucao[index])):

        new_row={'Carro':index,'Nó':nos[vetor_solucao[index][posicao].get('posicao')].nome,'Hora Inicio':vetor_solucao[index][posicao].get('Hora Inicio'),'Hora Fim':vetor_solucao[index][posicao].get('Hora Fim'),'Tipo':vetor_solucao[index][posicao].get('Tipo')}

        output.append(new_row)

df_output=pd.DataFrame(output)
df_output.to_csv('dados/99. output.csv',encoding='iso-8859-1')






