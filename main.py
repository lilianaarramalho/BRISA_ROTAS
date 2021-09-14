import warnings

import pandas as pd

from functions import *
from classes import *

warnings.filterwarnings('ignore')

global combinacoes
global count_rota
global resposta
global best_lista_sublancos
global solucao_global
global range_combinacoes
global resposta
global flat_list
global pausas_hora_inicio
global pausas_hora_fim
global pausas_id_inicio
global pausas_id_fim
global tipo_corrida
global vetor_solucao

range_combinacoes=999
resposta=3*60
combinacoes=[]
count_rota=0
flat_list=[]

#Ler informações
velocidade,t_medio_incidencia,n_simulacoes,tipo_corrida,slot_tempo=ler_arguments()
nos,turnos=import_data()
listas_nos=inverter_nos()
best_global=[]

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
lista_sublancos=[0]
indice_atual = 0

output = []
output_tempo_passagem = []
output_tempo_resposta = []
vetor_solucao=[]


if(tipo_corrida == 1): #Tipo Corrida = 1 é Micro

    simulacoes=[]
    output_condensado = []
    ultima_passagem = [[]] * len(nos)
    output_tmp = []

    solucao_n_voltas = []

    for i in range(2, 4):

        solucao_volta_atual=[]

        id_co = 0

        for no in nos:
            if no.co == 1:
                id_co = no.id

        sentido_anterior = "nd"

        for id_turno in range(len(turnos)):

            print('NOVA ROTA')
            print(str('número de voltas: ' + str(i) + ' turno: ' + str(id_turno)))
            rota_best, tempo_paragens_best, montecarlo_best, passagem_best, sentido_anterior,simulacoes_to_append = criar_rota_dividida(i,
                                                                                                                   id_co,
                                                                                                                   nos,
                                                                                                                   id_turno,
                                                                                                                   sentido_anterior,vetor_solucao)

            solucao_volta_atual.append(tempo_paragens_best[0].copy())

            vetor_solucao = tempo_paragens_best[0].copy()
            condensar_paragens(vetor_solucao)
            simulacoes.append(simulacoes_to_append)

            new_tempo_resposta={'Número Voltas':i,'Turno':id_turno,'Tempo Médio de Resposta':montecarlo_best}
            output_tempo_resposta.append(new_tempo_resposta)

            #VETOR CONDENSADO PARA CÁLCULOS
            vetor_condensado=condensar_paragens(vetor_solucao)

            if id_turno==0:
                for id_no in range(len(nos)):
                    ultima_passagem[id_no]=turnos[id_turno].inicio

            for dict_posicao in vetor_condensado:
                numero_voltas=i
                turno=id_turno
                sequencia=nos[dict_posicao.get('posicao')].id
                nome_no=nos[dict_posicao.get('posicao')].nome
                hora_inicio=dict_posicao.get('Hora Inicio')
                hora_fim=dict_posicao.get('Hora Fim')
                last_passagem=ultima_passagem[dict_posicao.get('posicao')]

                new_condensado = {'Numero Voltas': numero_voltas, 'Turno': turno,
                           'Sequência': sequencia,
                           'Nó': nome_no,
                           'Hora Inicio': hora_inicio,
                           'Hora Fim':hora_fim,
                           'Última Passagem (Hora Fim)':last_passagem}

                ultima_passagem[dict_posicao.get('posicao')]=hora_fim

                output_condensado.append(new_condensado)


            output = adicionar_deslocacoes(output, vetor_solucao, i, id_turno)

        solucao_n_voltas.append(solucao_volta_atual)


    df_output_tempo_resposta = pd.DataFrame(output_tempo_resposta)
    df_output_tempo_resposta.to_csv('dados/99. dados_solucao_tempo_resposta.csv', encoding='iso-8859-1')

    df_output_tmp=pd.DataFrame(output_tmp)
    df_output_tmp.to_csv('dados/99. dados_solucao_tmp.csv',encoding='ISO-8859-1')

    df_output = pd.DataFrame(output)
    df_output.to_csv('dados/99. dados_solucao_detalhe.csv', encoding='iso-8859-1')

    df_output_condensado=pd.DataFrame(output_condensado)
    df_output_condensado.to_csv('dados/99. dados_solucao_tempo_entre_passagens.csv', encoding='iso-8859-1')

    output_simulacoes=[]
    for corrida in simulacoes:
        for posicao in range(len(corrida)):
            new_row = {'Simulação':corrida[posicao].get('Simulação'),
                       'Número de Voltas':corrida[posicao].get('Número Voltas'),
                       'Turno':corrida[posicao].get('Turno'),
                       'Nó': nos[corrida[posicao].get('Nó')].nome,
                       'Hora Inicio': corrida[posicao].get('Hora Inicio'),
                       'Hora Fim': corrida[posicao].get('Hora Fim'),
                       'Tipo': corrida[posicao].get('Tipo')}
            output_simulacoes.append(new_row)

    df_simulacoes=pd.DataFrame(output_simulacoes)
    df_simulacoes.to_csv('dados/99. output_simulacoes.csv')

    output_condensado_ultima_passagem=[]
    for i in range(2,4):

        for index_turno in range(len(turnos)):

            vetor_condensado_turno = condensar_paragens(solucao_n_voltas[i-2][index_turno])

            ultima_passagem=[0]*len(nos)

            if index_turno == 0:
                vetor_condensado_turno_final=condensar_paragens(solucao_n_voltas[i-2][-1])

                for id_no in range(len(nos)):
                    index_final=len(vetor_condensado_turno_final)-1
                    not_found=True
                    while not_found==True:
                        if index_final>=0 and vetor_condensado_turno_final[index_final].get('posicao')==id_no:
                            ultima_passagem[id_no] = vetor_condensado_turno_final[index_final].get('Hora Fim')
                            not_found=False
                        index_final-=1

                    index_final = len(vetor_condensado_turno_final) - 1

            else:

                vetor_condensado_turno_final = condensar_paragens(solucao_n_voltas[i - 2][index_turno-1])

                for id_no in range(len(nos)):
                    index_final = len(vetor_condensado_turno_final) - 1
                    not_found = True
                    while not_found == True:
                        if index_final >= 0 and vetor_condensado_turno_final[index_final].get('posicao') == id_no:
                            ultima_passagem[id_no] = vetor_condensado_turno_final[index_final].get('Hora Fim')
                            not_found = False
                        index_final -= 1

                    index_final = len(vetor_condensado_turno_final) - 1


            for dict_posicao in vetor_condensado_turno:
                numero_voltas = i
                turno = id_turno
                sequencia = nos[dict_posicao.get('posicao')].id
                nome_no = nos[dict_posicao.get('posicao')].nome
                hora_inicio = dict_posicao.get('Hora Inicio')
                hora_fim = dict_posicao.get('Hora Fim')
                last_passagem = ultima_passagem[dict_posicao.get('posicao')]

                new_condensado = {'Numero Voltas': numero_voltas, 'Turno': turno,
                                  'Sequência': sequencia,
                                  'Nó': nome_no,
                                  'Hora Inicio': hora_inicio,
                                  'Hora Fim': hora_fim,
                                  'Última Passagem (Hora Fim)': last_passagem}

                ultima_passagem[dict_posicao.get('posicao')] = hora_fim

                output_condensado_ultima_passagem.append(new_condensado)

    df_output_condensado_ultima_passagem=pd.DataFrame(output_condensado_ultima_passagem)
    df_output_condensado_ultima_passagem.to_csv('dados/99. dados_solucao_tempo_entre_passagens.csv',encoding='ISO-8859-1')

else: #Tipo Corrida = 0 é Macro
    print('Corrida Macro')

    solucao_macro = []

    index = 0
    este_carro = []

    teste_carro = []
    n_voltas = 2

    #Por turno
    for id_turno in range(len(turnos)):
        index = 0
        este_carro = []
        teste_carro = []
        while index < len(nos)-1:
            este_carro = []
            teste_carro = []
            criterio_corte = False
            while criterio_corte == False:
                teste_carro.append(nos[index].id)
                if (verificar_corte(teste_carro, id_turno, n_voltas)):
                    criterio_corte = True
                else:
                    este_carro = teste_carro.copy()
                    index += 1

            index -= 1
            solucao_macro.append(este_carro)


    output_solucao = []

    for carro in range(len(solucao_macro)):
        for sub in solucao_macro[carro]:
            new_row = {'Carro': carro,
                       'Sublanço': sub}
            output_solucao.append(new_row)

    df_solucao = pd.DataFrame(output_solucao)
    df_solucao.to_csv('dados/99. output_macro.csv')

    print('fim')

# while stop_condition==False:
#
#     passos=[]
#
#     passos_temp=[]
#
#     passos_1_1=verificar_carro_iniciado(0,indice_atual,lista_sublancos,passos_1_1,'Norte',0)
#     passos.append(passos_1_1)
#     passos_1_2=verificar_carro_iniciado(0, indice_atual, lista_sublancos,passos_1_2, 'Norte', 1)
#     passos.append(passos_1_2)
#     passos_2_1= verificar_carro_iniciado(0, indice_atual, lista_sublancos,passos_2_1, 'Sul', 0)
#     passos.append(passos_2_1)
#     passos_2_2 = verificar_carro_iniciado(0, indice_atual, lista_sublancos,passos_2_2, 'Sul', 1)
#     passos.append(passos_2_2)
#
#     guardar_best = True
#     min_comb=0
#
#     while guardar_best:
#
#         if max(lista_sublancos)+1<len(nos):
#             lista_sublancos.append(lista_sublancos[-1] + 1)
#
#         if lista_sublancos in flat_list:
#             for posicao_incidencia in range(len(incidencias_visitadas)):
#                 if incidencias_visitadas[posicao_incidencia] == False:
#                     lista_sublancos = incidencias[posicao_incidencia][0]
#
#         indice_atual = max(lista_sublancos)
#
#         guardar_best=False
#
#         combinacoes = []
#
#         gerar_combinacoes(lista_sublancos,min_comb,range_combinacoes)
#
#         for posicao_carro in range(len(passos)):
#             carro=passos[posicao_carro]
#
#             if len(carro)>0:
#
#                 for incidencias_a_considerar in combinacoes:
#
#                     if compara_incidencias(incidencias_a_considerar,best_incidencias)==True:
#
#                         new_rota=[]
#
#                         new_rota, new_tempo_paragens,new_visitas=criar_rota_particular(lista_sublancos, incidencias_a_considerar, 0, carro,passos[posicao_carro])
#
#                         verificou_restricoes,soma=verificar_restricoes(new_tempo_paragens,lista_sublancos,incidencias_a_considerar,new_visitas)
#
#                         print('minimo sublanço ' + str(min(lista_sublancos)) + str(' carro ') + str(
#                             carro) + ' len sublanços ' + str(len(lista_sublancos)) + ' len incidencias ' + str(
#                             incidencias_a_considerar) + ' cumpre ' + str(verificou_restricoes))
#
#                         if best_rota == []:
#                             best_rota = new_rota.copy()
#                             best_tempo = new_tempo_paragens.copy()
#                             guardar_best=True
#                             best_lista_sublancos=lista_sublancos.copy()
#                             best_incidencias=incidencias_a_considerar.copy()
#
#                         if verificou_restricoes==True:
#
#                             best_rota,best_tempo,best_incidencias,guardar_best,best_lista_sublancos=verificar_best(new_rota,new_tempo_paragens,incidencias_a_considerar,best_rota,best_tempo,best_incidencias,guardar_best,lista_sublancos,best_lista_sublancos) #escolher o melhor (com incidencias com menor indice)
#
#         if guardar_best==True and indice_atual==len(nos)-1:
#             min_comb+=1
#
#     rotas.append(best_rota)
#     tempos.append(best_tempo)
#     incidencias_solucao.append(best_incidencias)
#     lista_sublancos_solucao.append(best_lista_sublancos)
#     limpar_incidencias(best_incidencias)
#
#     best_rota=[]
#     best_tempo=[]
#     best_incidencias=[]
#     best_lista_sublancos=[]
#
#
#     print('incidencias visitas' + str(incidencias_visitadas))
#
#     flat_list = [item for sublist in lista_sublancos_solucao for item in sublist]
#
#     stop_condition = True
#     if all(incidencias_visitadas) == False:
#         stop_condition = False
#     if len(flat_list)!=len(nos):
#         stop_condition=False
#
#     temp_lista=lista_sublancos.copy()
#
#     for index in lista_sublancos:
#         if index!=max(lista_sublancos):
#             temp_lista.remove(index)
#
#     lista_sublancos=temp_lista.copy()
#
#     if len(lista_sublancos)==1 and lista_sublancos[-1]==len(nos)-1:
#         lista_sublancos.insert(0,len(nos)-2)
#
# consideracoes_final(rotas)