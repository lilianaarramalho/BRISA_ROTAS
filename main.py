import pandas as pd
import math
from classes import *

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

    df_nos=pd.read_csv('dados/0. nos.csv',sep=',',encoding='iso-8859-1')

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

    print(x)
    print(y)

    if nos[x].distancias[y]<min_dist:
        min_dist=nos[x].distancias[y]

    if nos[y].distancias[x] < min_dist:
        min_dist = nos[y].distancias[x]

    return int(min_dist)

def get_co_proximo(index, sentido):

    global centros_operacionais

    found = False
    min_co=99
    max_co=-1

    if (sentido == "norte"):
        for no in nos:
            i=no.id
            is_co=no.co
            if (i <= index) and i>max_co and is_co!=-1:
                found = True
                max_co=i
                break


    if (sentido == "sul"):
        for no in nos:
            i = no.id
            is_co = no.co
            if (i >= index) and i<min_co and is_co!=-1:
                found = True
                min_co=i
                break

    if found == False:
        return -1

    elif sentido=='norte':
        return max_co

    elif sentido=='sul':
        return min_co

def verificar_carro_iniciado(id_turno):

    if len(carros[0]) == 0:
        posto_norte = get_co_proximo(int(len(nos)/2), "norte")
        # posto_norte=2
        if posto_norte > -1:
            # Se não existir, abrir
            carro_temp=carros[0].copy()
            for pos_sublanço in range(posto_norte, posto_norte-2,-1):
                atualizar_vetor(0,pos_sublanço,id_turno)


    if len(carros[1]) == 0:
            posto_norte = get_co_proximo(int(len(nos)/2), "norte")

            if posto_norte > -1:
                # Se não existir, abrir
                carro_temp = carros[1].copy()
                for pos_sublanço in range(posto_norte, posto_norte+2):
                    atualizar_vetor(1,pos_sublanço,id_turno)



    if len(carros[2]) == 0:
        posto_sul = get_co_proximo(int(len(nos)/2), "sul")
        # posto_sul=6
        if posto_sul > -1:
            # Se não existir, abrir
            carro_temp = carros[2].copy()
            for pos_sublanço in range(posto_sul,posto_sul-2,-1):
                atualizar_vetor(2,pos_sublanço,id_turno)


    if len(carros[3]) == 0:
        posto_sul = get_co_proximo(int(len(nos)/2), "sul")
        # posto_sul = 6
        if posto_sul > -1:
            # Se não existir, abrir
            carro_temp = carros[3].copy()
            for pos_sublanço in range(posto_sul, posto_sul+2):
                atualizar_vetor(3,pos_sublanço,id_turno)



def get_paragem_mais_proxima(current_index,tipo_paragem):

    min_dif=100
    index_prox=-1

    if tipo_paragem=='pausa':
        for no in nos:
            if no.is_pausa==1:
                diferenca=math.fabs(no.id-current_index)
                if diferenca<min_dif:
                    min_dif=diferenca
                    index_prox=no.id

    if tipo_paragem=='almoco':
        for no in nos:
            if no.is_almoco==1:
                diferenca=math.fabs(no.id-current_index)
                if diferenca<min_dif:
                    min_dif=diferenca
                    index_prox=no.id

    return index_prox

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

def verificar_tempo_pausa(id_turno,id_carro,tempo):

    pausa=turnos[id_turno].pausa
    almoco=turnos[id_turno].almoco
    fim=turnos[id_turno].fim-50

    n_pausas=0
    n_almocos=0
    n_fim=0

    for index in range(len(vetor_passos[id_carro])):
        if vetor_passos[id_carro][index].get('Tipo')=='Pausa':
            n_pausas+=1
        if vetor_passos[id_carro][index].get('Tipo')=='Almoço':
            n_almocos+=1
        if vetor_passos[id_carro][index].get('Tipo')=='Fim':
            n_fim+=1

    posicao_objetivo = -1

    if len(carros[id_carro])>0:
        posicao_atual = carros[id_carro][-1]
        posicao_objetivo=-1
        diferenca_min=99

        if tempo<=pausa+60:
            tempo_a_verificar=pausa
            for no in nos:
                if no.pausa == 1:
                    diferenca = get_distance(no.id, posicao_atual)
                    if diferenca < diferenca_min:
                        posicao_objetivo = no.id
                        diferenca_min = diferenca

        elif tempo<=almoco+60 and tempo>almoco-60:
            tempo_a_verificar = almoco
            for no in nos:
                if no.almoco == 1:
                    diferenca = get_distance(no.id, posicao_atual)
                    if diferenca < diferenca_min:
                        posicao_objetivo = no.id
                        diferenca_min = diferenca
        elif tempo>=fim-30:
            tempo_a_verificar = fim
            posicao_objetivo = carros[id_carro][0]
            diferenca = get_distance(posicao_objetivo, posicao_atual)
            diferenca_min = diferenca

        possivel=True
        print(possivel)
        print(posicao_objetivo)

        if int(tempo + 20) > tempo_a_verificar:
            possivel=False

        if tempo_a_verificar==pausa:
            id_tipo='pausa'
            if n_pausas>0:
                possivel=True
        elif tempo_a_verificar==almoco:
            id_tipo = 'almoco'
            if n_almocos>0:
                possivel=True
        elif tempo_a_verificar==fim:
            id_tipo = 'fim'
            if n_fim>0:
                possivel=False


    return possivel,posicao_objetivo,id_tipo

def get_tempo_atual(id_carro):

    tempo_atual=vetor_passos[id_carro][-1].get('Hora Fim')

    return tempo_atual

def verificar_tempo_incidencia(id_turno,id_carro,tempo_atual):

    posicao_atual = carros[id_carro][- 1]
    max_dif=-1
    proxima_posicao=-1
    hora_comparacao=99999

    if len(carros[id_carro])>0:
        for pos in range(len(incidencias)):
            incidencia=incidencias[pos]
            hora_inicidencia=incidencia[2]
            visitada=incidencias_visitadas[id_carro][pos]
            if hora_inicidencia>tempo_atual-45 and hora_inicidencia-tempo_atual<45 and visitada==False and hora_inicidencia<=turnos[id_turno].fim and hora_inicidencia>=turnos[id_turno].inicio:
                hora_comparacao=hora_inicidencia
                if math.fabs(posicao_atual-incidencia[0])>max_dif:
                    proxima_posicao=incidencia[0]
                    max_dif=math.fabs(posicao_atual-incidencia[0])
                if math.fabs(posicao_atual-incidencia[1])>max_dif:
                    proxima_posicao=incidencia[1]
                    max_dif=math.fabs(posicao_atual-incidencia[1])
                break

    tempo_adicional=get_tempo_atualizado(posicao_atual,proxima_posicao)

    tempo_atual+=tempo_adicional

    possivel,id_posicao,id_tipo=verificar_tempo_pausa(id_turno, id_carro,tempo_atual)

    for index in range(len(vetor_sublancos[id_carro])):

        if vetor_sublancos[id_carro][index] in nos_carro[id_carro]:

            vetor_sublancos[id_carro][index]-=tempo_adicional

            if vetor_sublancos[id_carro][index]<0:
                possivel=False

    if possivel==True and tempo_atual>hora_comparacao:
        return proxima_posicao,pos
    else:
        return -1,-1

def get_next_posicao(id_carro,lista_sublancos):

    posicao_atual=carros[id_carro][-1]
    posicao_anterior=carros[id_carro][-2]

    id_seguinte,vetor=verificar_tempo_sublancos(id_carro)

    if posicao_atual==0:
        if posicao_anterior!=0:
            nova_posicao=0
        else:
            nova_posicao=1

    elif posicao_atual>=len(nos)-1:
        if posicao_anterior!=len(nos)-1:
            nova_posicao=len(nos)-2
        else:
            nova_posicao=len(nos)-1

    else:
        if posicao_anterior>posicao_atual:
            nova_posicao=posicao_atual-1
        else:
            nova_posicao=posicao_atual+1

    return nova_posicao

def atualizar_vetor(id_carro,id_posicao,id_turno):

    anterior=0

    tipo_anterior="none"

    if len(vetor_passos[id_carro])>0:

        posicao_anterior=vetor_passos[id_carro][-1].get('posicao')

        hora_fim_atual=get_distance(posicao_anterior,id_posicao)

        anterior=vetor_passos[id_carro][-1].get('Hora Fim')

        tipo_anterior = vetor_passos[id_carro][-1].get('Tipo')

    else:

        hora_fim_atual=turnos[id_turno].inicio

    if tipo_anterior!='Fim':

        new_row = {'Carro': id_carro, 'posicao': id_posicao, 'Hora Inicio':hora_fim_atual+anterior, 'Hora Fim':hora_fim_atual+anterior,'Tipo':'Deslocação'}

        temp_passos=vetor_passos[id_carro].copy()
        temp_passos.append(new_row)
        vetor_passos[id_carro]=temp_passos

        carro_temporario=carros[id_carro].copy()
        carro_temporario.append((id_posicao))
        carros[id_carro]=carro_temporario

def adicionar_visita(id_carro,id_posicao,tempo,tipo):

    hora_fim = vetor_passos[id_carro][-1].get('Hora Fim')
    tipo_anterior = vetor_passos[id_carro][-1].get('Tipo')
    if tipo_anterior != 'Fim':
        new_row = {'Carro': id_carro, 'posicao': id_posicao, 'Hora Inicio': hora_fim,
                   'Hora Fim': tempo+hora_fim,'Tipo':tipo}

        temp_passos = vetor_passos[id_carro].copy()
        temp_passos.append(new_row)
        vetor_passos[id_carro] = temp_passos

def get_next_incidencia(id_carro,tempo_atual):

    id_posicao_incidencias=[-1]
    id_nos=[-1]

    for pos in range(len(incidencias)):
        incidencia = incidencias[pos]
        hora_inicidencia = incidencia[2]
        visitada = incidencias_visitadas[id_carro][pos]
        if hora_inicidencia > tempo_atual-20 and hora_inicidencia - tempo_atual < 20 and visitada == False:
            if -1 in id_nos:
                id_nos=[]
                id_posicao_incidencias=[]

            id_nos.append(incidencia[0])
            id_posicao_incidencias.append(pos)

    return id_nos,id_posicao_incidencias


def visitar_incidencia(id_no,id_carro,id_turno,tempo_paragem,tipo_paragem):

    posicao_atual=carros[id_carro][-1]
    posicao_anterior=id_no

    if posicao_atual==0:
        sentido='crescente'
    elif posicao_atual==len(nos):
        sentido='decrescente'
    elif posicao_atual>posicao_anterior:
        sentido='decrescente'
    else:
        sentido='crescente'

    if posicao_atual==id_no:
        adicionar_visita(id_carro, id_no, tempo_paragem, tipo_paragem)
        return id_no

    if (posicao_atual==0 or posicao_atual==len(nos)) and posicao_anterior!=posicao_atual:
        if sentido=='crescente':
            for posicao in range(posicao_atual,id_no+1):
                atualizar_vetor(id_carro,posicao,id_turno)

                if posicao==id_no:
                    adicionar_visita(id_carro,id_no,tempo_paragem,tipo_paragem)
        else:
            for posicao in range(posicao_atual,id_no-1,-1):
                atualizar_vetor(id_carro,posicao,id_turno)

                if posicao==id_no:
                    adicionar_visita(id_carro,id_no,tempo_paragem,tipo_paragem)

    else:
        if sentido=='crescente':
            for posicao in range(posicao_atual+1,id_no+1):
                atualizar_vetor(id_carro,posicao,id_turno)

                if posicao==id_no:
                    adicionar_visita(id_carro,id_no,tempo_paragem,tipo_paragem)
        else:
            for posicao in range(posicao_atual-1,id_no-1,-1):
                atualizar_vetor(id_carro,posicao,id_turno)

                if posicao==id_no:
                    adicionar_visita(id_carro,id_no,tempo_paragem,tipo_paragem)

    posicao_atual = carros[id_carro][-1]
    posicao_anterior = carros[id_carro][-2]

    if tipo_paragem!='Fim':

        if posicao_atual == 0:
            sentido = 'crescente'
        elif posicao_atual == len(nos):
            sentido = 'decrescente'
        elif posicao_atual > posicao_anterior:
            sentido = 'crescente'
        else:
            sentido = 'decrescente'

        if (posicao_atual == 0 or posicao_atual == len(nos)) and posicao_anterior != posicao_atual:
            if sentido == 'crescente':
                for posicao in range(posicao_atual, id_no + 1):
                    atualizar_vetor(id_carro, posicao,id_turno)
            else:
                for posicao in range(posicao_atual, id_no - 1, -1):
                    atualizar_vetor(id_carro, posicao,id_turno)

        else:
            if sentido == 'crescente':
                for posicao in range(posicao_atual + 1, id_no + 1):
                    atualizar_vetor(id_carro, posicao,id_turno)
            else:
                for posicao in range(posicao_atual - 1, id_no - 1, -1):
                    atualizar_vetor(id_carro, posicao,id_turno)

    return id_no


def verificar_melhor_solucao(id_turno):

    possivel=[True,True,True,True]
    tempo_sublancos=[180]*len(nos)
    soma_diferencas=[0,0,0,0]
    cumprimento_incidencias=[0,0,0,0]
    maximo=-99999
    maximo_id=-1
    max_cumprimento=0.0
    maximo_id_cumprimento=-1
    ultima_passagem_sublancos=[]

    for id_carro in range(len(temp_solucao)):


        cumprimento_incidencias[id_carro]=sum(i!=False for i in incidencias_visitadas[id_carro])/len(incidencias)

        if len(vetor_passos[id_carro])==0:
            possivel[id_carro] = False
        elif vetor_passos[id_carro][-1].get('Hora Fim')>turnos[id_turno].fim:
            possivel[id_carro]=False

        diferentes=[]

        if len(vetor_solucao)>0:
            for index in range(len(vetor_solucao)):
                diferentes.append(vetor_solucao[index][1].get('posicao'))

        carro=temp_solucao[id_carro]

        ultima_passagem=[180]*len(nos)

        if len(vetor_passos[id_carro]) > 0:

            posicao_atual = vetor_passos[id_carro][-1].get('posicao')

            for i in range(len(nos)):
                for index in range(len(vetor_passos[id_carro])):

                    posicao_passagem = vetor_passos[id_carro][index].get('posicao')
                    hora_passagem = vetor_passos[id_carro][index].get('Hora Fim')

                    if posicao_passagem == i:
                        ultima_passagem[i] = 180

                    else:
                        ultima_passagem[i] = ultima_passagem[i] - hora_passagem

        ultima_passagem_sublancos.append(ultima_passagem)

        for posicao in tempo_sublancos:
            soma_diferencas[id_carro]+=posicao

    #menor incidencia, numero de sublancos, tempo de abertura

    for id_carro in range(len(soma_diferencas)):

        ok=False
        if len(vetor_solucao)>0 and len(temp_solucao[id_carro])>0:
            if temp_solucao[id_carro][1]!=vetor_solucao[0][1]:
                ok=True
        else:
            ok=True

        if cumprimento_incidencias[id_carro]>max_cumprimento and possivel[id_carro]==True and ok:
            max_cumprimento=cumprimento_incidencias[id_carro]
            maximo_id_cumprimento=id_carro

        max=-99999
        for index in range(len(cumprimento_incidencias)):
            if cumprimento_incidencias[index]==max_cumprimento:
                if soma_diferencas[index]>max:
                    max=soma_diferencas[index]
                    maximo_id_cumprimento = index
                    max_len=len(vetor_passos[id_carro])

        if len(vetor_solucao)>0:
            for index in range(len(cumprimento_incidencias)):
                if cumprimento_incidencias[index] == max_cumprimento and vetor_passos[index][1].get('posicao') not in diferentes:
                    if len(vetor_passos[id_carro])>max_len:
                        max = soma_diferencas[index]
                        maximo_id_cumprimento = index

    return maximo_id_cumprimento

def adicionar_nos(id_carro,id_turno,vetor_passos,nos_visitados):

    print(id_carro)
    if len(vetor_passos[id_carro])>0:

        tempo_final=vetor_passos[id_carro][-1].get('Hora Fim')

    else:
        tempo_final=0

    count_visitas=0
    posicao_atualizar=-1
    count=len(vetor_passos[id_carro])-1

    while tempo_final<turnos[id_turno].fim and count>0:

        posicao = count

        id_no=vetor_passos[id_carro][posicao].get('posicao')
        anterior = vetor_passos[id_carro][posicao].get('Hora Fim')

        if nos_visitados[id_carro][id_no]!=True :

            tempo_adicionar=10

            if nos[id_no].vistoria==1:

                new_row = {'Carro': id_carro, 'posicao': id_no, 'Hora Inicio': anterior, 'Hora Fim': 10 + anterior,
               'Tipo': 'Vistoria'}

                count_visitas += 1

                vetor_passos[id_carro].insert(posicao, new_row)

            new_row = {'Carro': id_carro, 'posicao': id_no, 'Hora Inicio':anterior, 'Hora Fim':10+anterior,'Tipo':'Visitar Nó'}

            vetor_passos[id_carro].insert(posicao,new_row)

            nos_visitados[id_carro][id_no]=True

            count_visitas+=1

            posicao_atualizar=posicao

            tempo_final = vetor_passos[id_carro][-1].get('Hora Fim')+count_visitas*10

        count-=1

def verificar_tempo_sublancos(id_carro):

    ultima_passagem=[180]*len(nos)

    posicoes_problematicas=[]

    max_dif = 99

    id_visitar=-1

    if len(carros[id_carro])>0:

        posicao_atual=vetor_passos[id_carro][-1].get('posicao')

        for i in range(len(nos)):
            for index in range(len(vetor_passos[id_carro])):

                posicao_passagem=vetor_passos[id_carro][index].get('posicao')
                hora_passagem=vetor_passos[id_carro][index].get('Hora Fim')

                if posicao_passagem==i:
                    ultima_passagem[i]=180

                else:
                    ultima_passagem[i]=ultima_passagem[i]-hora_passagem

                    if ultima_passagem[i]<0 and i in nao_visitados[id_carro]:
                        posicoes_problematicas.append(i)

        for posicao in posicoes_problematicas:

            if math.fabs(posicao_atual-posicao)<max_dif:

                max_dif=math.fabs(posicao_atual-posicao)

                id_visitar=posicao

    return id_visitar,ultima_passagem


def go_to_no(id_no,id_carro,id_turno):

    posicao_atual=vetor_passos[id_carro][-1].get('posicao')

    if posicao_atual>=id_no:
        for index in range(posicao_atual-1,id_no-1,-1):
            atualizar_vetor(id_carro,index,id_turno)
    else:
        for index in range(posicao_atual+1,id_no+1):
            atualizar_vetor(id_carro,index,id_turno)

def criar_rotas():

    global carros
    global indexes
    global tempos_totais
    global carro_2_2
    global vetor_solucao
    global temp_solucao
    global hora_passagem
    global incidencias_visitadas
    global vetor_passos
    global nao_visitados

    global vetor_tempos_solucao
    global tempo_total_solucao
    global vetor_turnos
    global vetor_sublancos

    global pausas
    global almocos
    global visitar_nos
    global visitar_incidencias
    global vetor_solucao_incidencias
    global vetor_solucao_pausas
    global vetor_solucao_almocos
    global vetor_solucao_sublancos
    global nos_carro

    global nos_visitados
    global vistorias_visitadas

    nos_visitados=[False]*len(nos)

    vetor_solucao_sublancos=[]
    vetor_tempos_solucao=[]
    tempo_total_solucao=[]
    vetor_turnos=[]
    nao_visitados=[[]]*4
    nos_carro=[[]]*4


    for index in range(len(nos)):
        nao_visitados[0].append(index)
        nao_visitados[1].append(index)
        nao_visitados[2].append(index)
        nao_visitados[3].append(index)

    vetor_solucao_incidencias=[]
    vetor_solucao_pausas=[]
    vetor_solucao_almocos=[]
    vetor_solucao_visitar_nos=[]

    vetor_solucao=[]

    for turno in turnos:

        possivel=[True,True,True,True]
        carros=[[]]*4
        indexes=[0]*4
        tempos_totais=[0]*4
        temp_solucao = [[]]*4
        hora_passagem= dict.fromkeys([0, 1, 2,3])
        incidencias_visitadas = [[False] * len(incidencias)] * 4
        nos_visitados=[[False]*len(nos)]*4
        stop_condition=False

        while stop_condition==False:

            print(nao_visitados)

            possivel = [True, True, True, True]
            carros = [[]] * 4
            indexes = [0] * 4
            tempos_totais = [0] * 4
            temp_solucao = [[]] * 4
            hora_passagem = {}
            vetor_passos = [[]] * 4
            vetor_sublancos=[0*len(nos)]*4

            for i in range(4):
                hora_passagem[i] = []

            pausas=[[0]*200]*4
            almocos=[[0]*200]*4
            visitar_nos=[[0]*200]*4
            visitar_incidencias=[[0]*200]*4
            visitar_vistorias = [[0] * 200] * 4

            while any(possivel)==True:

                verificar_carro_iniciado(turno.id)

                for id_carro in range(len(carros)):

                    if len(carros[id_carro])>0 and possivel[id_carro]==True:

                        tempo_atual=get_tempo_atual(id_carro)

                        print(turno.id)
                        print(id_carro)
                        print(tempos_totais[id_carro])

                        id_possivel,id_posicao_pausa,id_tipo=verificar_tempo_pausa(turno.id, id_carro, tempo_atual)

                        id_visitar,ultima_passagem_sublancos=verificar_tempo_sublancos(id_carro)

                        vetor_sublancos[id_carro]=ultima_passagem_sublancos

                        if id_visitar!=-1 and id_possivel==True:

                            go_to_no(id_visitar,id_carro,turno.id)

                            nao_visitados[id_carro].remove(id_visitar)

                        elif id_possivel==True and possivel[id_carro]==True and id_visitar==-1:

                            id_no,id_posicao=verificar_tempo_incidencia(turno.id,id_carro,tempo_atual)

                            if id_no!=-1:

                                temp=incidencias_visitadas[id_carro].copy()
                                temp[id_posicao]=True
                                incidencias_visitadas[id_carro]=temp
                                tempo=30
                                tipo='Incidência'
                                visitar_incidencia(id_no,id_carro,turno.id,tempo,tipo)

                            else:

                                nova_posicao=adicionar_posicao(id_carro)
                                atualizar_vetor(id_carro,nova_posicao,turno.id)
                                satisfeitos[turno.id][nova_posicao]=True
                                nos_carro[id_carro].append(nova_posicao)


                        else:

                            if id_tipo=='pausa':
                                tempo=10
                                tipo='Pausa'
                                visitar_incidencia(id_posicao_pausa, id_carro, turno,tempo,tipo)

                            elif id_tipo=='almoco':
                                tempo = 40
                                tipo = 'Almoço'
                                visitar_incidencia(id_posicao_pausa, id_carro, turno, tempo, tipo)

                            elif id_tipo=='fim':
                                tempo = 0
                                tipo = 'Fim'
                                visitar_incidencia(vetor_passos[id_carro][0].get('posicao'), id_carro, turno, tempo, tipo)

                                possivel[id_carro]=False
                                temp_solucao[id_carro]=carros[id_carro]
                                carros[id_carro]=[]

                    else:
                        possivel[id_carro]=False

                if any(possivel)==False:

                    id_carro_add=verificar_melhor_solucao(turno.id)

                    adicionar_nos(id_carro_add,turno.id,vetor_passos,nos_visitados)

                    vetor_solucao.append(vetor_passos[id_carro_add])

                    for posicao_visitada in carros[id_carro_add]:
                        satisfeitos[turno.id][posicao_visitada]=True

                    temp=incidencias_visitadas[id_carro_add].copy()

                    for i in range(0,4):
                        incidencias_visitadas[i]=temp

                    temp=nao_visitados[id_carro_add].copy()
                    for i in range(0,4):
                        nao_visitados[i]=temp

            stop_condition=True
            for index in range(len(incidencias_visitadas[0])):
                if incidencias_visitadas[0][index]==False:
                    stop_condition=False
            if len(nao_visitados[0])>0:
                stop_condition=False

import_data()
criar_rotas()

output=[]

for index in range(len(vetor_solucao)):

    for posicao in range(len(vetor_solucao[index])):

        new_row={'Carro':index,'Nó':nos[vetor_solucao[index][posicao].get('posicao')].nome,'Hora Inicio':vetor_solucao[index][posicao].get('Hora Inicio'),'Hora Fim':vetor_solucao[index][posicao].get('Hora Fim'),'Tipo':vetor_solucao[index][posicao].get('Tipo')}

        output.append(new_row)

df_output=pd.DataFrame(output)
df_output.to_csv('dados/99. output.csv',encoding='iso-8859-1')

print('finish')