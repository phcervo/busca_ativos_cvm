import streamlit as st
import cvmpy
from dateutil.relativedelta import relativedelta
from datetime import date, datetime, timedelta
import pandas as pd
import numpy as np

def ajustar_numero(s):
    try:
        n = float(s)
        if n.is_integer():
            return str(int(n))
        else:
            return s
    except ValueError:
        return s
    
def percentil_do_valor(lista, valor):
    lista_ordenada = sorted(lista)
    n = len(lista_ordenada)
    menores_ou_iguais = sum(v <= valor for v in lista_ordenada)
    return menores_ou_iguais / n
    
def calcula_rating(controlador_cliente,dl_ebitda_cliente,margem_ebitda_cliente,fco_ebitda_cliente,ebitda_resultado_financeiro_cliente,caixa_divida_cp_cliente,roe_cliente):
    # Parametros
    controlador = {'0':0,'1':-1}
    dl_ebitda = {'0':1,'1':2,'2':3,'3':4,'4':5}
    margem_ebitda = {'0.1':5,'0.295':4,'0.3':3,'0.4':2,'0.5':1}
    fco_ebitda = {'0.05':5,'0.1':4,'0.2':3,'0.4':2,'0.6':1}
    ebitda_resultado_financeiro = {'1':5,'1.5':4,'2.5':3,'3':2,'4':1}
    caixa_divida_cp = {'0':5,'0.5':4,'1':3,'1.5':2,'2':1}
    roe = {'0':5,'0.05':4,'0.1':3,'0.15':2,'0.2':1}

    pesos = {'controlador':0.1,'dl_ebitda':0.2,'margem_ebitda':0.15,'fco_ebitda':0.15,'ebitda_resultado_financeiro':0.1,'caixa_divida_cp':0.15,'roe':0.15}

    # Converter as chaves para float
    controlador_keys = [float(k) for k in controlador.keys()]
    dl_ebitda_keys = [float(k) for k in dl_ebitda.keys()]
    margem_ebitda_keys = [float(k) for k in margem_ebitda.keys()]
    fco_ebitda_keys = [float(k) for k in fco_ebitda.keys()]
    ebitda_resultado_financeiro_keys = [float(k) for k in ebitda_resultado_financeiro.keys()]
    caixa_divida_cp_keys = [float(k) for k in caixa_divida_cp.keys()]
    roe_keys = [float(k) for k in roe.keys()]

    # Encontrar a chave mais próxima
    chave_controlador = min(controlador_keys, key=lambda x: abs(x - controlador_cliente))
    chave_dl_ebitda = min(dl_ebitda_keys, key=lambda x: abs(x - dl_ebitda_cliente))
    chave_margem_ebitda = min(margem_ebitda_keys, key=lambda x: abs(x - margem_ebitda_cliente))
    chave_fco_ebitda = min(fco_ebitda_keys, key=lambda x: abs(x - fco_ebitda_cliente))
    chave_ebitda_resultado_financeiro = min(ebitda_resultado_financeiro_keys, key=lambda x: abs(x - ebitda_resultado_financeiro_cliente))
    chave_caixa_divida_cp = min(caixa_divida_cp_keys, key=lambda x: abs(x - caixa_divida_cp_cliente))
    chave_roe = min(roe_keys, key=lambda x: abs(x - roe_cliente))

    # Retornar o valor correspondente
    resultado_controlador = controlador[str(ajustar_numero(chave_controlador))]
    resultado_dl_ebitda = dl_ebitda[str(ajustar_numero(chave_dl_ebitda))]
    resultado_margem_ebitda = margem_ebitda[str(ajustar_numero(chave_margem_ebitda))]
    resultado_fco_ebitda = fco_ebitda[str(ajustar_numero(chave_fco_ebitda))]
    resultado_ebitda_resultado_financeiro = ebitda_resultado_financeiro[str(ajustar_numero(chave_ebitda_resultado_financeiro))]
    resultado_caixa_divida_cp = caixa_divida_cp[str(ajustar_numero(chave_caixa_divida_cp))]
    resultado_roe = roe[str(ajustar_numero(chave_roe))]

    lista_resultados = []
    lista_resultados.append(resultado_controlador)
    lista_resultados.append(resultado_dl_ebitda)
    lista_resultados.append(resultado_margem_ebitda)
    lista_resultados.append(resultado_fco_ebitda)
    lista_resultados.append(resultado_ebitda_resultado_financeiro)
    lista_resultados.append(resultado_caixa_divida_cp)
    lista_resultados.append(resultado_roe)

    lista_pesos = list(pesos.values())
    resultado = np.dot(lista_resultados, lista_pesos)

    score_final = {'1':'AAA','1.5':'AA+','2':'AA','2.5':'AA-','3':'A+','3.5':'A','4':'A-','4.5':'BBB+','5':'BBB'}
    score_keys = [float(k) for k in score_final.keys()]
    chave_score = min(score_keys, key=lambda x: abs(x - resultado))
    resultado_score = score_final[str(ajustar_numero(chave_score))]

    return lista_resultados,resultado,resultado_score

def lista_ratings(df_setor,resultado):
    # Parametros
    controlador = {'0':0,'1':-1}
    dl_ebitda = {'0':1,'1':2,'2':3,'3':4,'4':5}
    margem_ebitda = {'0.1':5,'0.295':4,'0.3':3,'0.4':2,'0.5':1}
    fco_ebitda = {'0.05':5,'0.1':4,'0.2':3,'0.4':2,'0.6':1}
    ebitda_resultado_financeiro = {'1':5,'1.5':4,'2.5':3,'3':2,'4':1}
    caixa_divida_cp = {'0':5,'0.5':4,'1':3,'1.5':2,'2':1}
    roe = {'0':5,'0.05':4,'0.1':3,'0.15':2,'0.2':1}
    pesos = {'controlador':0.1,'dl_ebitda':0.2,'margem_ebitda':0.15,'fco_ebitda':0.15,'ebitda_resultado_financeiro':0.1,'caixa_divida_cp':0.15,'roe':0.15}
    # Converter as chaves para float
    controlador_keys = [float(k) for k in controlador.keys()]
    dl_ebitda_keys = [float(k) for k in dl_ebitda.keys()]
    margem_ebitda_keys = [float(k) for k in margem_ebitda.keys()]
    fco_ebitda_keys = [float(k) for k in fco_ebitda.keys()]
    ebitda_resultado_financeiro_keys = [float(k) for k in ebitda_resultado_financeiro.keys()]
    caixa_divida_cp_keys = [float(k) for k in caixa_divida_cp.keys()]
    roe_keys = [float(k) for k in roe.keys()]
    lista_pesos = list(pesos.values())
    lista_valores = []
    print(df_setor)
    for index, value in df_setor.iterrows():
        controlador_cliente = value['controlador']
        dl_ebitda_cliente = value['dl_ebitda']
        margem_ebitda_cliente = value['margem_ebitda']
        fco_ebitda_cliente = value['fco_ebitda']
        ebitda_resultado_financeiro_cliente = value['ebitda_resultado_financeiro']
        caixa_divida_cp_cliente = value['caixa_divida_cp']
        roe_cliente = value['roe']

        chave_controlador = min(controlador_keys, key=lambda x: abs(x - controlador_cliente))
        chave_dl_ebitda = min(dl_ebitda_keys, key=lambda x: abs(x - dl_ebitda_cliente))
        chave_margem_ebitda = min(margem_ebitda_keys, key=lambda x: abs(x - margem_ebitda_cliente))
        chave_fco_ebitda = min(fco_ebitda_keys, key=lambda x: abs(x - fco_ebitda_cliente))
        chave_ebitda_resultado_financeiro = min(ebitda_resultado_financeiro_keys, key=lambda x: abs(x - ebitda_resultado_financeiro_cliente))
        chave_caixa_divida_cp = min(caixa_divida_cp_keys, key=lambda x: abs(x - caixa_divida_cp_cliente))
        chave_roe = min(roe_keys, key=lambda x: abs(x - roe_cliente))

        resultado_controlador = controlador[str(ajustar_numero(chave_controlador))]
        resultado_dl_ebitda = dl_ebitda[str(ajustar_numero(chave_dl_ebitda))]
        resultado_margem_ebitda = margem_ebitda[str(ajustar_numero(chave_margem_ebitda))]
        resultado_fco_ebitda = fco_ebitda[str(ajustar_numero(chave_fco_ebitda))]
        resultado_ebitda_resultado_financeiro = ebitda_resultado_financeiro[str(ajustar_numero(chave_ebitda_resultado_financeiro))]
        resultado_caixa_divida_cp = caixa_divida_cp[str(ajustar_numero(chave_caixa_divida_cp))]
        resultado_roe = roe[str(ajustar_numero(chave_roe))]

        lista_resultados = []
        lista_resultados.append(resultado_controlador)
        lista_resultados.append(resultado_dl_ebitda)
        lista_resultados.append(resultado_margem_ebitda)
        lista_resultados.append(resultado_fco_ebitda)
        lista_resultados.append(resultado_ebitda_resultado_financeiro)
        lista_resultados.append(resultado_caixa_divida_cp)
        lista_resultados.append(resultado_roe)

        resultado_emp = np.dot(lista_resultados, lista_pesos)
        lista_valores.append(resultado_emp)

    from statistics import mean,median
    rating_medio = mean(lista_valores)
    rating_mediano = median(lista_valores)
    print(lista_valores)

    score_final = {'1':'AAA','1.5':'AA+','2':'AA','2.5':'AA-','3':'A+','3.5':'A','4':'A-','4.5':'BBB+','5':'BBB'}
    score_keys = [float(k) for k in score_final.keys()]
    chave_score = min(score_keys, key=lambda x: abs(x - resultado))
    resultado_score = score_final[str(ajustar_numero(chave_score))]

    chave_setorial_medio = min(score_keys, key=lambda x: abs(x - rating_medio))
    resultado_setorial_medio = score_final[str(ajustar_numero(chave_setorial_medio))]
    chave_setorial_mediano = min(score_keys, key=lambda x: abs(x - rating_mediano))
    resultado_setorial_mediano = score_final[str(ajustar_numero(chave_setorial_mediano))]
    percentil = percentil_do_valor(lista_valores, resultado)

    return rating_medio,rating_mediano,resultado_setorial_medio,resultado_setorial_mediano,percentil


def main():
    st.title("Rating Crédito Privado")
    df_ratings = pd.read_excel('rating_credito/plan_ratings.xlsx')
    df_ratings_mod = df_ratings.copy()
    df_ratings_mod.columns = ['Data','Emissor','Setor','Controlador','DL/EBITDA','Margem EBITDA','FCO/EBITDA','EBITDA/Resultado Financeiro','Caixa/Divida CP','ROE','Rating','Válido']
    with st.expander('Tabela Rating'):
        st.dataframe(
            df_ratings_mod.style.format({"Data":lambda x: x.strftime("%d/%m/%Y"),"Margem EBITDA":"{:.2%}","FCO/EBITDA":"{:.2%}","ROE":"{:.2%}","DL/EBITDA": lambda x: f"{x:.1f}x",
                                         "EBITDA/Resultado Financeiro": lambda x: f"{x:.1f}x","Caixa/Divida CP": lambda x: f"{x:.1f}x"})
            ,hide_index=True)

    with st.expander('Nova Análise'):
        with st.form('form-analise'):
            emissor = st.text_input("Emissor")
            setor = st.text_input("Setor")
            dl_ebitda = st.text_input("DL/EBITDA")
            fco_ebitda = st.text_input("FCO_EBITDA")
            margem_ebitda = st.text_input("Margem EBITDA")
            ebitda_rf = st.text_input("EBITDA/Resultado Financeiro")
            caixa_divida_cp = st.text_input("Caixa/Dívida CP")
            controlador = st.text_input("Controlador (1=sim,0=não)")
            roe = st.text_input("ROE")
            button2 = st.form_submit_button("Calcular")
        
        if button2:
            dl_ebitda = float(dl_ebitda)
            fco_ebitda = float(fco_ebitda)
            margem_ebitda = float(margem_ebitda)
            ebitda_rf = float(ebitda_rf)
            caixa_divida_cp = float(caixa_divida_cp)
            controlador = float(controlador)
            roe = float(roe)
            lista_resultados, resultado,resultado_score = calcula_rating(controlador,dl_ebitda,margem_ebitda,fco_ebitda,ebitda_rf,caixa_divida_cp,roe)
            st.markdown("#### Conversão para Score")
            df_score = pd.DataFrame({
            'Métrica':['Controlador','DL/EBITDA','Margem EBITDA','FCO/EBITDA','EBITDA/Resultado Financeiro','Caixa/Dívida CP','ROE'],
            'Pontos': lista_resultados
                })
            #df_score = df_score.set_index('Métrica')
            html_table = df_score.to_html(index=False,border=0,justify="left",classes="excel-table")
            css = """
<style>
.excel-table {
    width: 100%;
    border-collapse: collapse;
    font-family: Arial, sans-serif;
    font-size: 14px;
}

.excel-table th {
    background-color: #f2f2f2;
    font-weight: bold;
    padding: 6px;
    border-bottom: 1px solid #d9d9d9;
    text-align: left;
}

.excel-table td {
    padding: 6px;
    border-bottom: 1px solid #e6e6e6;
}

.excel-table tr:last-child td {
    border-bottom: none;
}

.excel-table td:nth-child(2) {
    text-align: right;
    font-weight: bold;
}
</style>
"""

            st.markdown(css + html_table, unsafe_allow_html=True)
            st.markdown(f"##### Score Final: {resultado}")
            st.markdown(f"#### Rating Final: {resultado_score}")

            df_setor = df_ratings.loc[df_ratings['setor']==setor]
            rating_medio,rating_mediano,resultado_setorial_medio,resultado_setorial_mediano,percentil = lista_ratings(df_setor,resultado)
            st.divider()
            st.markdown("#### Score Setorial (Benchmark)")
            df_score = pd.DataFrame({
            'Métrica':['SETOR','MÉDIA DO SETOR','MEDIANA DO SETOR','RATING MÉDIO','RATING MEDIANO','PERCENTIL NO SETOR'],
            'Valor': [setor,round(rating_medio,2),round(rating_mediano,2),resultado_setorial_medio,resultado_setorial_mediano,f"{round(percentil*100,2)}%"]
                })
            #df_score = df_score.set_index('Métrica')
            html_table2 = df_score.to_html(index=False,border=0,justify="left",classes="excel-table")
            st.markdown(css + html_table2, unsafe_allow_html=True)

    with st.expander('Pesos'):
        pesos = {'controlador':0.1,'dl_ebitda':0.2,'margem_ebitda':0.15,'fco_ebitda':0.15,'ebitda_resultado_financeiro':0.1,'caixa_divida_cp':0.15,'roe':0.15}
        df_pesos = pd.DataFrame({
            'Métrica':list(pesos.keys()),
            'Peso': list(pesos.values())
                })
        st.dataframe(
            df_pesos.style.format({"Peso":"{:.2%}"}),hide_index=True)

if __name__ == '__main__':
    main()