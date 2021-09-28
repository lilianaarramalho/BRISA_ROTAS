import warnings

import pandas as pd

from functions import *
from classes import *
from joblib import Parallel,delayed
import multiprocessing
global vetor_warnings
vetor_warnings=[]

warnings.filterwarnings('ignore')

# if __name__ == '__main__':
#
#     # Pyinstaller fix

#multiprocessing.freeze_support()
#
#     main()

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
nos,turnos=import_data('Sequência Micro')
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
    numero_incidencias=[]
    output_condensado = []
    ultima_passagem = [[]] * len(nos)
    output_tmp = []

    solucao_n_voltas = []

    for i in range(2, 4):

        solucao_volta_atual=[]

        id_co = 0
        vetor_solucao = []

        for no in nos:
            if no.co == 1:
                id_co = no.id

        sentido_anterior = "nd"
        for id_turno in range(len(turnos)):

            print('NOVA ROTA')
            print(str('número de voltas: ' + str(i) + ' turno: ' + str(id_turno)))
            rota_best, tempo_paragens_best, montecarlo_best, passagem_best, sentido_anterior,simulacoes_to_append,numero_medio_incidencias_to_append = criar_rota_dividida(i,
                                                                                                                   id_co,
                                                                                                                   nos,
                                                                                                                   id_turno,
                                                                                                                   sentido_anterior,vetor_solucao)

            solucao_volta_atual.append(tempo_paragens_best[0].copy())

            vetor_solucao = tempo_paragens_best[0].copy()
            condensar_paragens(vetor_solucao)
            simulacoes.append(simulacoes_to_append)
            new_row={'voltas':i,'turno':id_turno,'n_medio_simulacoes':numero_medio_incidencias_to_append}
            numero_incidencias.append(new_row)

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
                       'Nó inicio': corrida[posicao].get('Nó partida'),
                       'Nó fim':  corrida[posicao].get('Nó chegada'),
                       'Tempo':  corrida[posicao].get('Tempo'),
                       'Posicao real escolhida':corrida[posicao].get('Posicao real escolhida'),
                       'Hora fim vetor':corrida[posicao].get('Hora fim vetor')}
            output_simulacoes.append(new_row)

    df_numero_incidencias=pd.DataFrame(numero_incidencias)
    df_numero_incidencias.to_csv('dados/99. output_numero_incidencias.csv',encoding='ISO-8859-1')

    df_simulacoes=pd.DataFrame(output_simulacoes)
    df_simulacoes.to_csv('dados/99. output_simulacoes.csv',encoding='ISO-8859-1')

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

    sorts=['Sequência AE_1','Sequência AE_2']

    print('Corrida Macro')

    solucao_macro = []

    index = 0
    este_carro = []

    teste_carro = []
    n_voltas = 4
    cos_escolhidos = []
    co_escolhido = 0
    turnos_escolhidos = []

    calcular_matriz_cos()
    output_solucao = []

    carro_count = 0

    output_agregado = []
    indicadores = {
        'Tempo_Resolucao_Incid': 0,
        'Tempo_Desloc_Incid': 0,
        'Tempo_Nos': 0,
        'Tempo_Patrulha': 0,
        'Tempo_Total': 0,
        'Tempo_Abertura':0
    }
    teste_indicadores = []

    indicadores_escolhidos = []

    #for i in range(2,4):

    for sort in sorts:
        nos, turnos = import_data(sort)
        for i in range(n_voltas):
            print ('No Voltas:::' + str(i))
            #Por turno
            carro_count = 0
            for id_turno in range(len(turnos)):
                print('Turno::::' + str(id_turno))
                index = 0
                este_carro = []
                teste_carro = []
                teste_indicadores = {
            'Tempo_Resolucao_Incid': 0,
            'Tempo_Desloc_Incid': 0,
            'Tempo_Nos': 0,
            'Tempo_Patrulha': 0,
            'Tempo_Total': 0}

                while index < len(nos):
                    este_carro = []
                    teste_carro = []
                    criterio_corte = False
                    while criterio_corte == False and index < len(nos):
                        if(index > 0 and len(teste_carro) == 0):
                            index -= 1

                        adicionados=0
                        

                        if nos[index].grupo!="-1" and nos[index-1].grupo!=nos[index].grupo:
                            for no in nos:
                                if no.grupo==nos[index].grupo:
                                    teste_carro.append(no.id)
                                    adicionados+=1

                        else:
                            teste_carro.append(nos[index].id)
                            adicionados+=1

                        co_escolhido, dist_co_rota = escolher_co(teste_carro)
                        teste_indicadores, criterio_corte,vetor_warnings = verificar_corte(teste_carro, id_turno,i +1, dist_co_rota,vetor_warnings,adicionados)

                        if (criterio_corte == False):
                            este_carro = teste_carro.copy()
                            indicadores = teste_indicadores.copy()
                            index += adicionados
                        elif len(este_carro)==1 and adicionados>1:
                            print('Para o número de voltas ' + str(n_voltas) + ' no turno ' + str(id_turno) + ', é impossível alocar grupo ' + str(nos[teste_carro[-1]].grupo) + ' em conjunto.' )
                            vetor_warnings.append('Para o número de voltas ' + str(n_voltas) + ' no turno ' + str(id_turno) + ', é impossível alocar grupo ' + str(nos[teste_carro[-1]].grupo) + ' em conjunto.' )

                    solucao_macro.append(este_carro)
                    cos_escolhidos.append(co_escolhido)
                    turnos_escolhidos.append(id_turno)

                    count_sub=0
                    lista_aes=[]

                    for id_no in este_carro:
                        if nos[id_no].auto_estrada not in lista_aes:
                            lista_aes.append(nos[id_no].auto_estrada)

                    listToStr = ' + '.join([str(elem) for elem in lista_aes])

                    for sub in este_carro:
                        if count_sub>0:
                            sublanco=str(nos[este_carro[count_sub]-1].nome) + " - " + str(nos[este_carro[count_sub]].nome)
                            extensao=indicadores.get('Lista extensoes')[count_sub-1]
                            incidencias=indicadores.get('Incidencias consideradas')[count_sub-1]

                        else:
                            sublanco=str(nos[co_escolhido].nome) + " - " + str(nos[este_carro[0]].nome)
                            extensao=(indicadores.get('Tempo_CO_Rota')/2*60)/velocidade
                            if extensao==0:
                                sublanco=""
                            incidencias=0

                        new_row = {'No.Voltas': i+1,
                                   'Turno': id_turno,
                                   'Carro': carro_count,
                                   'C.O.': nos[co_escolhido],
                                   'Nó': nos[este_carro[count_sub]].nome,
                                   'Sublanço':sublanco,
                                   'Kms':extensao,
                                   'Incidências':incidencias/60,
                                   'Sentido':sort,
                                   'Auto Estradas':listToStr}
                        output_solucao.append(new_row)
                        count_sub+=1

                    lista_nos=[]
                    for id_no in este_carro:
                        lista_nos.append(nos[id_no].nome)

                    new_row = {
                        'No.Voltas': i+1,
                        'Turno': id_turno,
                        'Carro':carro_count,
                        'C.O.': nos[co_escolhido],
                        'Tempo_Resolucao_Incid': indicadores.get('Tempo_Resolucao_Incid')/60,
                        'Tempo_Desloc_Incid': indicadores.get('Tempo_Desloc_Incid')/60,
                        'Tempo_Nos': indicadores.get('Tempo_Nos')/60,
                        'Tempo_Patrulha': indicadores.get('Tempo_Patrulha')/60,
                        'Temp_CO_Rota:' : indicadores.get('Tempo_CO_Rota')/60,
                        'Tempo_Total': indicadores.get('Tempo_Total')/60,
                        'Tempo_Abertura':indicadores.get('Tempo_Abertura')/60,
                        'Nós':lista_nos,
                        'Extensoes_consideradas':indicadores.get('Lista extensoes'),
                        'Nós':indicadores.get('Lista nos'),
                        'Sentido':sort,
                        'Auto Estradas': listToStr

                    }
                    output_agregado.append(new_row)
                    carro_count += 1

    df_solucao = pd.DataFrame(output_solucao)
    df_solucao.to_csv('dados/99. output_macro.csv', encoding='iso-8859-1')

    df_agregado = pd.DataFrame(output_agregado)
    df_agregado.to_csv('dados/99. output_agregado.csv', encoding='iso-8859-1')

    df_warnings=pd.DataFrame(vetor_warnings)
    df_warnings.to_csv('dados/99. output_warnings.csv',encoding='iso-8859-1')

    print('fim')
