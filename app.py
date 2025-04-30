import streamlit as st
import cvmpy
from dateutil.relativedelta import relativedelta
from datetime import date, datetime, timedelta
import pandas as pd
from io import BytesIO
import json

# Funcs
@st.cache_data()
def lista_cvm(m4):
    fi = cvmpy.FI()
    fi.fetch_historical_data(dataset="composicao_diversificacao",start_date=m4,end_date=m4)
    return fi

def main():
    home = st.Page(about_func,title="Home")
    busca = st.Page(busca_func,title="Fundos que detém os ativos")
    st.set_page_config(layout='wide',page_title="Consulta CVM")
    pg = st.navigation([home,busca])
    pg.run()




def busca_func():
    st.title("Consulta Fundos")
    #dm = DateManager()
    with open('nomes_emissores.json', 'r') as f:
        dict_emissores = json.load(f)
    d0 = datetime.today().date()
    mes4 = d0 - relativedelta(months=4)
    mes5 = d0 - relativedelta(months=5)
    mes6 = d0 - relativedelta(months=6)
    mes7 = d0 - relativedelta(months=7)
    mes8 = d0 - relativedelta(months=8)
    mes9 = d0 - relativedelta(months=9)
    mes10 = d0 - relativedelta(months=10)
    mes11 = d0 - relativedelta(months=11)
    mes12 = d0 - relativedelta(months=12)
    m4 = mes4.strftime("%m/%Y")
    m5 = mes5.strftime("%m/%Y")
    m6 = mes6.strftime("%m/%Y")
    m7 = mes7.strftime("%m/%Y")
    m8 = mes8.strftime("%m/%Y")
    m9 = mes9.strftime("%m/%Y")
    m10 = mes10.strftime("%m/%Y")
    m11 = mes11.strftime("%m/%Y")
    m12 = mes12.strftime("%m/%Y")
    lista_fundos = [m4,m5,m6,m7,m8,m9,m10,m11,m12]
    #lista_fundos_form = [data.strftime("%m/%Y") for data in lista_fundos]
    sidebar = st.sidebar.selectbox("Tipo de ativo",['Debêntures','Bancários'])
    sidedate = st.sidebar.selectbox("Data Carteira",options=lista_fundos)
    fi = lista_cvm(sidedate)
    
    if sidebar == 'Bancários':
        df_bancarios = fi.composicao_diversificacao.cda_fi_BLC_5[['CNPJ_FUNDO_CLASSE','DENOM_SOCIAL', 'DT_COMPTC','TP_APLIC', 'TP_ATIVO','CNPJ_EMISSOR', 'EMISSOR','TITULO_POSFX',
       'CD_INDEXADOR_POSFX','VL_MERC_POS_FINAL']]
        
        if 'df_bancarios' not in st.session_state:
            st.session_state['df_bancarios'] = df_bancarios

        if 'counter_replace' not in st.session_state:
            st.session_state['counter_replace'] = 0
    # Lista emissores de Bancários
        df_bancarios = df_bancarios.copy()
        st.session_state['df_bancarios']['EMISSOR'] = st.session_state['df_bancarios']['EMISSOR'].str.upper()
        if st.session_state['counter_replace'] < 1:
            st.session_state['df_bancarios']['EMISSOR'] = st.session_state['df_bancarios']['EMISSOR'].replace(dict_emissores)
            st.session_state['counter_replace'] += 1
        lista_emissores_bancarios = st.session_state['df_bancarios']['EMISSOR'].unique().tolist()
        lista_emissores_bancarios.sort()
        with st.form("form_bancarios"):
            emissores = st.multiselect("Selecione os emissores que deseja ver",lista_emissores_bancarios,placeholder="Selecione os emissores")
            df = st.session_state['df_bancarios'].loc[st.session_state['df_bancarios']['EMISSOR'].isin(emissores)]
            df.columns = ['CNPJ_FUNDO','NOME_FUNDO','DATA_CARTEIRA','TIPO_ATIVO','CLASSIFICAÇÃO_ATIVO','CNPJ_EMISSOR','EMISSOR','TITULO_POS_FIXADO',
                          'INDEXADOR','VALOR_DE_MERCADO']                                 
            df['DATA_CARTEIRA'] = pd.to_datetime(df['DATA_CARTEIRA']).dt.strftime("%m/%Y")
            
            button2 = st.form_submit_button("Exibir")
        if button2:
            df_exibe = df.copy()
            df_exibe["VALOR_DE_MERCADO"] = df_exibe["VALOR_DE_MERCADO"].map("R$ {:,.2f}".format)
            st.dataframe(df_exibe,hide_index=True,use_container_width=True)
            output = BytesIO()
            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                df.to_excel(writer, index=False, sheet_name="Sheet1")
                writer.close()
            excel_data = output.getvalue()
            st.download_button("Baixar base de fundos",data=excel_data,file_name='base_fundos_bancarios.xlsx')
    
    elif sidebar == 'Debêntures':
        df_rv = fi.composicao_diversificacao.cda_fi_BLC_4[['CNPJ_FUNDO_CLASSE','DENOM_SOCIAL','DT_COMPTC','TP_APLIC', 'TP_ATIVO', 'EMISSOR_LIGADO', 'QT_POS_FINAL','CD_ATIVO','VL_MERC_POS_FINAL',
                                                    'DT_INI_VIGENCIA','DT_FIM_VIGENCIA']]
        df_debentures = df_rv.loc[df_rv['TP_APLIC'] == 'Debêntures']
        if 'df_debentures' not in st.session_state:
            st.session_state['df_debentures'] = df_debentures
        lista_ativos = st.session_state['df_debentures']['CD_ATIVO'].unique().tolist()
        lista_ativos.sort()
        with st.form("debform"):
            ativos = st.multiselect("Selecione os ativos",lista_ativos,placeholder="Selecione...")
            button1 = st.form_submit_button("Exibir")
        if button1:
            df = st.session_state['df_debentures'].loc[st.session_state['df_debentures']['CD_ATIVO'].isin(ativos)]
            df.columns = ['CNPJ_FUNDO','NOME_FUNDO','DATA_CARTEIRA','TIPO_ATIVO', 'CLASSE_ATIVO', 'EMISSOR_LIGADO', 'QUANTIDADE','ATIVO','VALOR_DE_MERCADO',
                                                    'DATA_EMISSAO','DATA_VENCIMENTO']
            df['DATA_CARTEIRA'] = pd.to_datetime(df['DATA_CARTEIRA']).dt.strftime("%m/%Y")
            df['DATA_EMISSAO'] = pd.to_datetime(df['DATA_EMISSAO']).dt.date
            df['DATA_VENCIMENTO'] = pd.to_datetime(df['DATA_VENCIMENTO']).dt.date
            df_exibe = df.copy()
            df_exibe["VALOR_DE_MERCADO"] = df_exibe["VALOR_DE_MERCADO"].map("R$ {:,.2f}".format)
            st.dataframe(df_exibe,hide_index=True,use_container_width=True)
            output = BytesIO()
            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                df.to_excel(writer, index=False, sheet_name="Sheet1")
                writer.close()
            excel_data = output.getvalue()
            st.download_button("Baixar base de fundos",data=excel_data,file_name='base_fundos_debentures.xlsx')
            

def about_func():
    st.subheader("Informações")
    st.sidebar.subheader("QUANTITAS | Compliance")
    st.text("-> Nesse site é possível verificar os fundos detentores dos ativos selecionados, de acordo com o Mês/Ano da carteira escolhida.")
    st.text("-> Consultas para títulos bancários: CDB,LFs e DPGE. De acordo com o emissor escolhido")
    st.text("-> Possível consultar os fundos que detem as debêntures selecionadas")
    st.text('-> Ao clicar em "Baixar base de fundos", um Excel com as posições é baixado.')

if __name__ == '__main__':
    main()
