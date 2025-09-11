import streamlit as st
import cvmpy
from dateutil.relativedelta import relativedelta
from datetime import date, datetime, timedelta
import pandas as pd
from io import BytesIO
import json
import time

# Funcs
@st.cache_data()
def lista_cvm(m4):
    fi = cvmpy.FI()
    fi.fetch_historical_data(dataset="composicao_diversificacao",start_date=m4,end_date=m4)
    return fi

@st.cache_data()
def cadastros_cvm():
    fi = cvmpy.FI()
    fi.fetch_static_data(dataset='extrato_novo')
    df_gestor = fi.cad_fi_hist_gestor
    df_gestor['DT_FIM_GESTOR'] = df_gestor['DT_FIM_GESTOR'].fillna(0)
    df_gestor = df_gestor.loc[df_gestor['DT_FIM_GESTOR'] == 0]
    df = df_gestor[['CNPJ_FUNDO','GESTOR']]
    df['GESTOR'] = df['GESTOR'].fillna("")
    df.columns = ['CNPJ_FUNDO_CLASSE','GESTOR']
    df = df.sort_values(by="GESTOR", ascending=False)
    df = df.drop_duplicates(subset="CNPJ_FUNDO_CLASSE", keep="first")
    return df

@st.cache_data()
def cadastros_cvm2():
    fi = cvmpy.FI()
    fi.fetch_static_data(dataset="cadastro")
    df = fi.cadastro
    return df

@st.cache_data()
def cadastros_cvm3():
    fi = cvmpy.FI()
    fi.fetch_static_data(dataset='extrato_novo')
    df_nome = fi.cad_fi_hist_denom_social
    df_nome['DT_FIM_DENOM_SOCIAL'] = df_nome['DT_FIM_DENOM_SOCIAL'].fillna(0)
    df_nome = df_nome.loc[df_nome['DT_FIM_DENOM_SOCIAL'] == 0]
    df_nome = df_nome[['CNPJ_FUNDO','DENOM_SOCIAL']]
    df_nome['DENOM_SOCIAL'] = df_nome['DENOM_SOCIAL'].fillna("")
    df_nome.columns = ['CNPJ_FUNDO_CLASSE','NOME_FUNDO']
    df_nome = df_nome.sort_values(by="NOME_FUNDO", ascending=False)
    df_nome = df_nome.drop_duplicates(subset="CNPJ_FUNDO_CLASSE", keep="first")
    return df_nome

@st.cache_data()
def informes_cvm(m4,m1):
    # Carrega informe diario do mês
    fundos = cvmpy.FI()
    fundos.fetch_historical_data(dataset="informe_diario", start_date=m4, end_date=m1)
    return fundos

@st.cache_data()
def get_cdi(d1_form,d2_form):
    df = pd.read_csv(f'https://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados?formato=csv&dataInicial={d1_form}&dataFinal={d2_form}',encoding='UTF-8',sep=';')
    return df

def main():
    home = st.Page(about_func,title="Home")
    busca = st.Page(busca_func,title="Fundos que detém os ativos")
    rentabilidade = st.Page(rentabilidade_func,title="Rentabilidade fundos")
    rentabilidade_incentivados = st.Page(rentabilidade_inc,title="Rentabilidade fundos (incentivados)")
    st.set_page_config(layout='wide',page_title="Consulta CVM")
    pg = st.navigation([home,busca,rentabilidade,rentabilidade_incentivados])
    pg.run()


def busca_func():
    st.title("Consulta Fundos")
    #dm = DateManager()
    with open('nomes_emissores.json', 'r') as f:
        dict_emissores = json.load(f)
    d0 = datetime.today().date()
    mes1 = d0 - relativedelta(months=1)
    mes2 = d0 - relativedelta(months=2)
    mes3 = d0 - relativedelta(months=3)
    mes4 = d0 - relativedelta(months=4)
    mes5 = d0 - relativedelta(months=5)
    mes6 = d0 - relativedelta(months=6)
    mes7 = d0 - relativedelta(months=7)
    mes8 = d0 - relativedelta(months=8)
    mes9 = d0 - relativedelta(months=9)
    mes10 = d0 - relativedelta(months=10)
    mes11 = d0 - relativedelta(months=11)
    mes12 = d0 - relativedelta(months=12)
    m1 = mes1.strftime("%m/%Y")
    m2 = mes2.strftime("%m/%Y")
    m3 = mes3.strftime("%m/%Y")
    m4 = mes4.strftime("%m/%Y")
    m5 = mes5.strftime("%m/%Y")
    m6 = mes6.strftime("%m/%Y")
    m7 = mes7.strftime("%m/%Y")
    m8 = mes8.strftime("%m/%Y")
    m9 = mes9.strftime("%m/%Y")
    m10 = mes10.strftime("%m/%Y")
    m11 = mes11.strftime("%m/%Y")
    m12 = mes12.strftime("%m/%Y")
    lista_fundos = [m1,m2,m3,m4,m5,m6,m7,m8,m9,m10,m11,m12]
    #lista_fundos_form = [data.strftime("%m/%Y") for data in lista_fundos]
    if 'data_counter' not in st.session_state:
        st.session_state['data_counter'] = 0

    if 'datepre' not in st.session_state:
        st.session_state['datepre'] = None

    sidebar = st.sidebar.selectbox("Tipo de ativo",['Debêntures','Bancários','FIDC'])
    sidedate = st.sidebar.selectbox("Data Carteira",options=lista_fundos)
    fi = lista_cvm(sidedate)
    cad_cvm = cadastros_cvm()
    
    if sidebar == 'Bancários':
        df_bancarios = fi.composicao_diversificacao.cda_fi_BLC_5[['CNPJ_FUNDO_CLASSE','DENOM_SOCIAL', 'DT_COMPTC','TP_APLIC', 'TP_ATIVO','CNPJ_EMISSOR', 'EMISSOR','TITULO_POSFX',
       'CD_INDEXADOR_POSFX','VL_MERC_POS_FINAL']]
        df_bancarios = df_bancarios.merge(cad_cvm,on='CNPJ_FUNDO_CLASSE',how='left')
        
        if 'df_bancarios' not in st.session_state:
            st.session_state['df_bancarios'] = df_bancarios
        
        if sidedate != st.session_state['datepre']:
            st.session_state['df_bancarios'] = df_bancarios
            st.session_state['datepre'] = sidedate
            st.session_state['df_bancarios']['EMISSOR'] = st.session_state['df_bancarios']['EMISSOR'].replace(dict_emissores)

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
            df = df[['CNPJ_FUNDO_CLASSE','DENOM_SOCIAL', 'DT_COMPTC','GESTOR','TP_APLIC', 'TP_ATIVO','CNPJ_EMISSOR', 'EMISSOR','TITULO_POSFX','CD_INDEXADOR_POSFX','VL_MERC_POS_FINAL']]
            df.columns = ['CNPJ_FUNDO','NOME_FUNDO','DATA_CARTEIRA','GESTOR','TIPO_ATIVO','CLASSIFICAÇÃO_ATIVO','CNPJ_EMISSOR','EMISSOR','TITULO_POS_FIXADO',
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
        df_debentures = df_debentures.merge(cad_cvm,on='CNPJ_FUNDO_CLASSE',how='left')
        df_debentures['GESTOR'] = df_debentures['GESTOR'].fillna("") 
        if 'df_debentures' not in st.session_state:
            st.session_state['df_debentures'] = df_debentures
        
        if sidedate != st.session_state['datepre']:
            st.session_state['df_debentures'] = df_debentures
            st.session_state['datepre'] = sidedate

        lista_ativos = st.session_state['df_debentures']['CD_ATIVO'].unique().tolist()
        lista_ativos.sort()
        with st.form("debform"):
            ativos = st.multiselect("Selecione os ativos",lista_ativos,placeholder="Selecione...")
            button1 = st.form_submit_button("Exibir")
        if button1:
            df = st.session_state['df_debentures'].loc[st.session_state['df_debentures']['CD_ATIVO'].isin(ativos)]
            df = df[['CNPJ_FUNDO_CLASSE','DENOM_SOCIAL','DT_COMPTC','GESTOR','TP_APLIC', 'TP_ATIVO', 'EMISSOR_LIGADO', 'QT_POS_FINAL','CD_ATIVO','VL_MERC_POS_FINAL',
                                                    'DT_INI_VIGENCIA','DT_FIM_VIGENCIA']]
            df.columns = ['CNPJ_FUNDO','NOME_FUNDO','DATA_CARTEIRA','GESTOR','TIPO_ATIVO', 'CLASSE_ATIVO', 'EMISSOR_LIGADO', 'QUANTIDADE','ATIVO','VALOR_DE_MERCADO',
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
    
    elif sidebar == 'FIDC':
        df_fundos = fi.composicao_diversificacao.cda_fi_BLC_2[['CNPJ_FUNDO_CLASSE','DENOM_SOCIAL','DT_COMPTC','TP_APLIC', 'TP_ATIVO', 'QT_POS_FINAL','VL_MERC_POS_FINAL',
                                                    'CNPJ_FUNDO_CLASSE_COTA','NM_FUNDO_CLASSE_SUBCLASSE_COTA']]
        df_fidc = df_fundos.loc[df_fundos['TP_ATIVO'] == 'FIDC']
        df_fidc = df_fidc.merge(cad_cvm,on='CNPJ_FUNDO_CLASSE',how='left')
        df_fidc['GESTOR'] = df_fidc['GESTOR'].fillna("")
        if 'df_fidc' not in st.session_state:
            st.session_state['df_fidc'] = df_fidc
        
        if sidedate != st.session_state['datepre']:
            st.session_state['df_fidc'] = df_fidc
            st.session_state['datepre'] = sidedate

        lista_ativos = st.session_state['df_fidc']['NM_FUNDO_CLASSE_SUBCLASSE_COTA'].unique().tolist()
        lista_ativos.sort()
        with st.form("fidcform"):
            ativos = st.multiselect("Selecione os ativos",lista_ativos,placeholder="Selecione...")
            button1 = st.form_submit_button("Exibir")
        if button1:
            df = st.session_state['df_fidc'].loc[st.session_state['df_fidc']['NM_FUNDO_CLASSE_SUBCLASSE_COTA'].isin(ativos)]
            df = df[['CNPJ_FUNDO_CLASSE','DENOM_SOCIAL','DT_COMPTC','GESTOR','TP_APLIC', 'TP_ATIVO', 'QT_POS_FINAL','VL_MERC_POS_FINAL',
                                                    'CNPJ_FUNDO_CLASSE_COTA','NM_FUNDO_CLASSE_SUBCLASSE_COTA']]
            df.columns = ['CNPJ_FUNDO','NOME_FUNDO','DATA_CARTEIRA','GESTOR','TIPO_ATIVO', 'CLASSE_ATIVO', 'QUANTIDADE','VALOR_DE_MERCADO',
                                                    'CNPJ_FIDC','NOME_FIDC']
            df['DATA_CARTEIRA'] = pd.to_datetime(df['DATA_CARTEIRA']).dt.strftime("%m/%Y")
            df_exibe = df.copy()
            df_exibe["VALOR_DE_MERCADO"] = df_exibe["VALOR_DE_MERCADO"].map("R$ {:,.2f}".format)
            st.dataframe(df_exibe,hide_index=True,use_container_width=True)
            output = BytesIO()
            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                df.to_excel(writer, index=False, sheet_name="Sheet1")
                writer.close()
            excel_data = output.getvalue()
            st.download_button("Baixar base de fundos",data=excel_data,file_name='base_fundos_fidc.xlsx')
            

def about_func():
    st.subheader("Informações")
    st.sidebar.subheader("QUANTITAS | Compliance")
    st.text("-> Nesse site é possível verificar os fundos detentores dos ativos selecionados, de acordo com o Mês/Ano da carteira escolhida.")
    st.text("-> Consultas para títulos bancários: CDB,LFs e DPGE. De acordo com o emissor escolhido")
    st.text("-> Possível consultar os fundos que detem as debêntures (ativo)")
    st.text("-> Consultas para FIDC (por nome do fundo)")
    st.text('-> Ao clicar em "Baixar base de fundos", um Excel com as posições é baixado.')
    st.text('-> Consultar rentabilidade média de fundos de Crédito Privado.')
    st.text(r'-> Metodologia: Fundos com pelo menos 30% do PL em debêntures na última carteira aberta, mais de 10 cotistas, com Taxa de Adm maior que 0. Após isso, filtra-se os 20 fundos de maior PL.')


def rentabilidade_func():
    st.title("Rentabilidade Fundos Crédito Privado")
    st.sidebar.subheader("QUANTITAS | Compliance")
    d0 = datetime.today().date()
    mes4 = d0 - relativedelta(months=4)
    mes5 = d0 - relativedelta(months=5)
    mes0 = d0
    mes1 = d0 - relativedelta(months=1)
    mes2 = d0 - relativedelta(months=2)
    mes3 = d0 - relativedelta(months=3)
    m4 = mes4.strftime("%Y-%m-%d")
    m5 = mes5.strftime("%Y-%m-%d")
    m0 = mes0.strftime("%Y-%m-%d")
    m1 = mes1.strftime("%Y-%m-%d")
    m2 = mes2.strftime("%Y-%m-%d")
    m3 = mes3.strftime("%Y-%m-%d")
    format_m1 = mes1.strftime("%m/%Y")
    format_m2 = mes2.strftime("%m/%Y")
    format_m3 = mes3.strftime("%m/%Y")
    format_m0 = mes0.strftime("%m/%Y")
    mes_rentabilidade = st.selectbox('Selecione a data',[format_m0,format_m1,format_m2,format_m3])
    fi = lista_cvm(m4)
    df_cadastro = cadastros_cvm3()
    fundos = informes_cvm(m4,m0)

    lista_negativa_cnpj = ['12.845.801/0001-37','29.283.779/0001-81','46.975.474/0001-50']
    df_cadastro = df_cadastro[['CNPJ_FUNDO_CLASSE','NOME_FUNDO']]
    #df_cadastro = df_cadastro.dropna()
    # Composição da carteira (ultima carteira aberta)
    df_bancarios = fi.composicao_diversificacao.cda_fi_BLC_5[['CNPJ_FUNDO_CLASSE','DENOM_SOCIAL', 'DT_COMPTC','TP_APLIC', 'TP_ATIVO','CNPJ_EMISSOR', 'EMISSOR','TITULO_POSFX',
        'CD_INDEXADOR_POSFX','VL_MERC_POS_FINAL']]

    df_rv = fi.composicao_diversificacao.cda_fi_BLC_4[['CNPJ_FUNDO_CLASSE','DENOM_SOCIAL','DT_COMPTC','TP_APLIC', 'TP_ATIVO', 'EMISSOR_LIGADO', 'QT_POS_FINAL','CD_ATIVO','VL_MERC_POS_FINAL',
                                                    'DT_INI_VIGENCIA','DT_FIM_VIGENCIA']]
    df_debentures = df_rv.loc[df_rv['TP_APLIC'] == 'Debêntures']
    # Juntar os fundos que tem um ou outro df, logo esses serão fundos que possuem aplicação em crédito privado.
    df_debentures_cod = df_debentures[['CNPJ_FUNDO_CLASSE','DENOM_SOCIAL']]
    # Pegar os CNPJS desses fundos, para depois linkar com as cotas e cadastro. Filtrando TX_ADM, PL,...
    lista_cnpjs_fundos = df_debentures_cod['CNPJ_FUNDO_CLASSE'].unique().tolist()
    df_taxas = df_cadastro[df_cadastro['CNPJ_FUNDO_CLASSE'].isin(lista_cnpjs_fundos)]
    #print(df_taxas.loc[df_taxas['DENOM_SOCIAL'].str.contains('QUANTITAS')])
    dftx2 = df_taxas
    cnpj_com_taxa = dftx2['CNPJ_FUNDO_CLASSE'].unique().tolist()
    # Filtra apenas os fundos que contem as caracteristicas desejadas (informe diario)
    df_fundos = fundos.informe_diario.inf_diario_fi[['CNPJ_FUNDO_CLASSE', 'DT_COMPTC', 'VL_QUOTA', 'VL_PATRIM_LIQ', 'NR_COTST']][fundos.informe_diario.inf_diario_fi.CNPJ_FUNDO_CLASSE.isin(cnpj_com_taxa)]
    df_fundos = df_fundos.rename(columns={'CNPJ_FUNDO_CLASSE':'cnpj', 'DT_COMPTC':'data', 'VL_QUOTA':'cota', 'VL_PATRIM_LIQ':'pl', 'NR_COTST':'cotistas' })
    df_fundos['pl'] = df_fundos['pl'].astype(float)
    df_fundos['cota'] = df_fundos['cota'].astype(float)
    df_fundos = df_fundos.sort_values('data', ascending=True)
    df_fundos['data'] = pd.to_datetime(df_fundos['data'])

    # Pega os fundos e PL da ultima carteira aberta
    data_maxima = df_debentures['DT_COMPTC'].max()
    df_d2 = df_fundos.loc[df_fundos['data'] == pd.to_datetime(data_maxima)]
    if len(df_d2) <=1:
        data_maxima = data_maxima - relativedelta(days=1)
        df_d2 = df_fundos.loc[df_fundos['data'] == data_maxima]

    pl_dos_fundos = df_d2[['cnpj','pl']]
    pl_dos_fundos.columns = ['CNPJ_FUNDO_CLASSE','PL']
    # Minimo 40% do PL em debentures
    df_debentures = df_debentures.groupby(['CNPJ_FUNDO_CLASSE','DENOM_SOCIAL'])['VL_MERC_POS_FINAL'].sum().reset_index()
    df_debentures = df_debentures.merge(pl_dos_fundos,how='left')
    df_debentures = df_debentures.dropna()
    df_debentures = df_debentures.copy()
    df_debentures['deb/pl'] = df_debentures['VL_MERC_POS_FINAL'] / df_debentures['PL']
    
    df_debentures = df_debentures.loc[df_debentures['deb/pl'] > 0.4]
    df_debentures = df_debentures.loc[~df_debentures['DENOM_SOCIAL'].str.contains("INCENTIVADO")]
    df_debentures = df_debentures.loc[~df_debentures['DENOM_SOCIAL'].str.contains("INFRA")]
    df_debentures = df_debentures.loc[~df_debentures['CNPJ_FUNDO_CLASSE'].isin(lista_negativa_cnpj)]

    lista_cnpj_credito = df_debentures['CNPJ_FUNDO_CLASSE'].unique().tolist()
    df_final = fundos.informe_diario.inf_diario_fi[['CNPJ_FUNDO_CLASSE', 'DT_COMPTC', 'VL_QUOTA', 'VL_PATRIM_LIQ', 'NR_COTST']][fundos.informe_diario.inf_diario_fi.CNPJ_FUNDO_CLASSE.isin(lista_cnpj_credito)]
    df_final = df_final.rename(columns={'CNPJ_FUNDO_CLASSE':'cnpj', 'DT_COMPTC':'data', 'VL_QUOTA':'cota', 'VL_PATRIM_LIQ':'pl', 'NR_COTST':'cotistas' })

    df_final['pl'] = df_final['pl'].astype(float)
    df_final['cota'] = df_final['cota'].astype(float)
    df_final = df_final.sort_values('data', ascending=True)
    df_final = df_final.loc[df_final['data'] == data_maxima]
    df_final = df_final.loc[df_final['cotistas'] > 10]
 
    df_ordenada = df_final.sort_values("pl",ascending=False)
    df_20_maiores = df_ordenada.head(20)
    lista_20 = df_20_maiores['cnpj'].unique().tolist()
    df_filtrada = fundos.informe_diario.inf_diario_fi[['CNPJ_FUNDO_CLASSE', 'DT_COMPTC', 'VL_QUOTA', 'VL_PATRIM_LIQ', 'NR_COTST']][fundos.informe_diario.inf_diario_fi.CNPJ_FUNDO_CLASSE.isin(lista_20)]
    df_filtrada = df_filtrada.rename(columns={'CNPJ_FUNDO_CLASSE':'cnpj', 'DT_COMPTC':'data', 'VL_QUOTA':'cota', 'VL_PATRIM_LIQ':'pl', 'NR_COTST':'cotistas' })

    df_filtrada['pl'] = df_filtrada['pl'].astype(float)
    df_filtrada['cota'] = df_filtrada['cota'].astype(float)
    df_filtrada = df_filtrada.sort_values('data', ascending=True)
   
    # Calculo rentabilidade
    df_filtrada['mes'] = df_filtrada['data'].dt.month
    if mes_rentabilidade == format_m1:
        mes_calculo = mes1
    elif mes_rentabilidade == format_m2:
        mes_calculo = mes2
    elif mes_rentabilidade == format_m0:
        mes_calculo = mes0
    else:
        mes_calculo = mes3

    m1_calculo = mes_calculo.month
    m2_data = mes_calculo - relativedelta(months=1)
    m1_calculo = mes_calculo.month
    m2_calculo = m2_data.month
    data_final = df_filtrada.loc[df_filtrada['mes'] == m1_calculo]['data'].max()
    data_inicial = df_filtrada.loc[df_filtrada['mes'] == m2_calculo]['data'].max()
    dict_rentabilidade = {}
    lista_cnpj = []
    lista_rentabilidade = []
    lista_pl = []
    

    d1_form = data_inicial.strftime('%d/%m/%Y')
    d2_form = data_final.strftime('%d/%m/%Y')
    ### PEGA CDI ###
    df = get_cdi(d1_form,d2_form)
    df['valor'] = df['valor'].str.replace(",",".")
    ### CALCULA CDI ###
    df['valor'] = (df['valor'].apply(float) /100 )+ 1
    df = df.iloc[1:]
    di_acumulado = df['valor'].prod()
    di_acumulado = (di_acumulado - 1) * 100
    df['valor'] = df['valor']- 1
    df['data'] = pd.to_datetime(df['data'],format= "%d/%m/%Y")

    # RENTABILIDADE POR MÊS
    for cnpj in lista_20:
        df1 = df_filtrada.loc[(df_filtrada['cnpj'] == cnpj)]
        df2 = df1.loc[df1['data'] == data_final]
        if len(df2) <1:
            df2 = df1.loc[df1['data'] == data_final - relativedelta(days=1)]

        cota_last = df2['cota'].values[0]
        df3 = df1.loc[df1['data'] == data_inicial]
        pl = df1['pl'].values[0]
        if len(df3) <1:
            pass
        else:
            cota_first = df3['cota'].values[0]
            lista_cnpj.append(cnpj)
            lista_pl.append(pl)
            lista_rentabilidade.append((cota_last/cota_first - 1 )*100)
    dict_rentabilidade['cnpj'] = lista_cnpj
    dict_rentabilidade['rentabilidade'] = lista_rentabilidade
    dict_rentabilidade['pl'] = lista_pl
    df_agrupada_mes = pd.DataFrame(dict_rentabilidade)
    df_cadastro.columns = ['cnpj','nome']
    df_agrupada_mes = df_agrupada_mes.merge(df_cadastro,on='cnpj',how='left').drop_duplicates()
    # DF RENTABILIDADE POR DIA
    df_filtrada = df_filtrada.sort_values(['cnpj', 'data'])
    df_filtrada['retorno'] = df_filtrada.groupby('cnpj')['cota'].pct_change()
    df_diaria = df_filtrada.copy()
    df_diaria = df_diaria.merge(df_cadastro,on='cnpj',how='left')
    df_diaria = df_diaria.loc[df_diaria['mes'] == m1_calculo]
    df_diaria = df_diaria.merge(df,on='data',how='left')
    df_diaria['retorno/cdi'] = df_diaria['retorno'] / df_diaria['valor']
    df_diaria = df_diaria[['data','retorno','retorno/cdi','cnpj','nome','pl']]
    media_diaria = df_diaria.groupby('data')['retorno'].mean().reset_index()
    media_cdi_diaria = df_diaria.groupby('data')['retorno/cdi'].mean().reset_index()
    media_diaria = media_diaria.merge(media_cdi_diaria,how='left')
    # COLOCA NA TELA A RENTABILIDADE
    m1_calculo = mes_calculo.month
    ano_calculo = mes_calculo.year
    data = f"Rentabilidade {m1_calculo}/{ano_calculo}"
    st.subheader(data)
    with st.expander("Rentabilidade diária"):
        st.markdown("#### Rentabilidade diária:")
        # TRANSFORMA EM EXCEL A TABELA DIÁRIA
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            media_diaria.to_excel(writer, index=False, sheet_name="diaria")
        excel_diaria = output.getvalue()
        st.dataframe(media_diaria,hide_index= True)
        st.download_button("Baixar rentabilidade diária",data=excel_diaria,file_name='rent_diaria.xlsx')
        st.markdown("#### Abertura rentabilidade por fundo:")
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df_diaria.to_excel(writer, index=False, sheet_name="diaria")
            writer.close()
        excel_aberto_diaria = output.getvalue()
        st.dataframe(df_diaria,hide_index= True)
        st.download_button("Baixar abertura diária",data=excel_aberto_diaria,file_name='rent_aberta_diaria.xlsx')
   
    
    # CALCULA RENTABILIDADE SOBRE CDI
    rentabilidade_media = df_agrupada_mes['rentabilidade'].mean()
    cdi_acumulado = di_acumulado
    rentabilidade_cdi = rentabilidade_media / cdi_acumulado * 100
    # TRANSFORMA EM EXCEL A TABELA
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df_agrupada_mes.to_excel(writer, index=False, sheet_name="Sheet1")
        writer.close()
    excel_data = output.getvalue()
    
    with st.expander("Fundos considerados"):
        st.dataframe(df_agrupada_mes,hide_index=True)
        st.download_button("Baixar Tabela",excel_data,file_name='rentabilidade_fundos.xlsx')
    
    with st.expander("Informações mensais"):
        st.markdown("#### Rentabilidade média dos fundos:")
        rent_formatada = round(rentabilidade_media,2)
        st.text(f"{rent_formatada} %")
        st.markdown("#### Rentabilidade CDI:")
        cdi_formatado = round(cdi_acumulado,2)
        st.text(f"{cdi_formatado} %")
        st.markdown("#### Rentabilidade sobre o CDI:")
        total_formatado = round(rentabilidade_cdi,2)
        st.success(f"{total_formatado} %")

def rentabilidade_inc():
    st.title("Rentabilidade Fundos Incentivados Crédito Privado")
    st.sidebar.subheader("QUANTITAS | Compliance")
    d0 = datetime.today().date()
    mes4 = d0 - relativedelta(months=4)
    mes5 = d0 - relativedelta(months=5)
    mes0 = d0
    mes1 = d0 - relativedelta(months=1)
    mes2 = d0 - relativedelta(months=2)
    mes3 = d0 - relativedelta(months=3)
    m4 = mes4.strftime("%Y-%m-%d")
    m5 = mes5.strftime("%Y-%m-%d")
    m0 = mes0.strftime("%Y-%m-%d")
    m1 = mes1.strftime("%Y-%m-%d")
    m2 = mes2.strftime("%Y-%m-%d")
    m3 = mes3.strftime("%Y-%m-%d")
    format_m1 = mes1.strftime("%m/%Y")
    format_m2 = mes2.strftime("%m/%Y")
    format_m3 = mes3.strftime("%m/%Y")
    format_m0 = mes0.strftime("%m/%Y")
    mes_rentabilidade = st.selectbox('Selecione a data',[format_m0,format_m1,format_m2,format_m3])
    fi = lista_cvm(m4)
    df_cadastro = cadastros_cvm3()
    fundos = informes_cvm(m4,m0)

    lista_negativa_cnpj = ['12.845.801/0001-37','29.283.779/0001-81','46.975.474/0001-50']
    df_cadastro = df_cadastro[['CNPJ_FUNDO_CLASSE','NOME_FUNDO']]
    #df_cadastro = df_cadastro.dropna()
    # Composição da carteira (ultima carteira aberta)
    df_bancarios = fi.composicao_diversificacao.cda_fi_BLC_5[['CNPJ_FUNDO_CLASSE','DENOM_SOCIAL', 'DT_COMPTC','TP_APLIC', 'TP_ATIVO','CNPJ_EMISSOR', 'EMISSOR','TITULO_POSFX',
        'CD_INDEXADOR_POSFX','VL_MERC_POS_FINAL']]

    df_rv = fi.composicao_diversificacao.cda_fi_BLC_4[['CNPJ_FUNDO_CLASSE','DENOM_SOCIAL','DT_COMPTC','TP_APLIC', 'TP_ATIVO', 'EMISSOR_LIGADO', 'QT_POS_FINAL','CD_ATIVO','VL_MERC_POS_FINAL',
                                                    'DT_INI_VIGENCIA','DT_FIM_VIGENCIA']]
    df_debentures = df_rv.loc[df_rv['TP_APLIC'] == 'Debêntures']
    # Juntar os fundos que tem um ou outro df, logo esses serão fundos que possuem aplicação em crédito privado.
    df_debentures_cod = df_debentures[['CNPJ_FUNDO_CLASSE','DENOM_SOCIAL']]
    # Pegar os CNPJS desses fundos, para depois linkar com as cotas e cadastro. Filtrando TX_ADM, PL,...
    lista_cnpjs_fundos = df_debentures_cod['CNPJ_FUNDO_CLASSE'].unique().tolist()
    df_taxas = df_cadastro[df_cadastro['CNPJ_FUNDO_CLASSE'].isin(lista_cnpjs_fundos)]
    #print(df_taxas.loc[df_taxas['DENOM_SOCIAL'].str.contains('QUANTITAS')])
    dftx2 = df_taxas
    cnpj_com_taxa = dftx2['CNPJ_FUNDO_CLASSE'].unique().tolist()
    # Filtra apenas os fundos que contem as caracteristicas desejadas (informe diario)
    df_fundos = fundos.informe_diario.inf_diario_fi[['CNPJ_FUNDO_CLASSE', 'DT_COMPTC', 'VL_QUOTA', 'VL_PATRIM_LIQ', 'NR_COTST']][fundos.informe_diario.inf_diario_fi.CNPJ_FUNDO_CLASSE.isin(cnpj_com_taxa)]
    df_fundos = df_fundos.rename(columns={'CNPJ_FUNDO_CLASSE':'cnpj', 'DT_COMPTC':'data', 'VL_QUOTA':'cota', 'VL_PATRIM_LIQ':'pl', 'NR_COTST':'cotistas' })
    df_fundos['pl'] = df_fundos['pl'].astype(float)
    df_fundos['cota'] = df_fundos['cota'].astype(float)
    df_fundos = df_fundos.sort_values('data', ascending=True)
    df_fundos['data'] = pd.to_datetime(df_fundos['data'])

    # Pega os fundos e PL da ultima carteira aberta
    data_maxima = df_debentures['DT_COMPTC'].max()
    df_d2 = df_fundos.loc[df_fundos['data'] == pd.to_datetime(data_maxima)]
    if len(df_d2) <=1:
        data_maxima = data_maxima - relativedelta(days=1)
        df_d2 = df_fundos.loc[df_fundos['data'] == data_maxima]

    pl_dos_fundos = df_d2[['cnpj','pl']]
    pl_dos_fundos.columns = ['CNPJ_FUNDO_CLASSE','PL']
    # Minimo 40% do PL em debentures
    df_debentures = df_debentures.groupby(['CNPJ_FUNDO_CLASSE','DENOM_SOCIAL'])['VL_MERC_POS_FINAL'].sum().reset_index()
    df_debentures = df_debentures.merge(pl_dos_fundos,how='left')
    df_debentures = df_debentures.dropna()
    df_debentures = df_debentures.copy()
    df_debentures['deb/pl'] = df_debentures['VL_MERC_POS_FINAL'] / df_debentures['PL']
    
    df_debentures = df_debentures.loc[df_debentures['deb/pl'] > 0.4]
    df_incentivado = df_debentures.loc[df_debentures['DENOM_SOCIAL'].str.contains("INCENTIVADO")]
    df_infra = df_debentures.loc[df_debentures['DENOM_SOCIAL'].str.contains("INFRA")]
    df_debentures = pd.concat([df_incentivado,df_infra])
    df_debentures =  df_debentures.drop_duplicates(subset="CNPJ_FUNDO_CLASSE", keep="first")

    df_debentures = df_debentures.loc[~df_debentures['CNPJ_FUNDO_CLASSE'].isin(lista_negativa_cnpj)]

    lista_cnpj_credito = df_debentures['CNPJ_FUNDO_CLASSE'].unique().tolist()
    df_final = fundos.informe_diario.inf_diario_fi[['CNPJ_FUNDO_CLASSE', 'DT_COMPTC', 'VL_QUOTA', 'VL_PATRIM_LIQ', 'NR_COTST']][fundos.informe_diario.inf_diario_fi.CNPJ_FUNDO_CLASSE.isin(lista_cnpj_credito)]
    df_final = df_final.rename(columns={'CNPJ_FUNDO_CLASSE':'cnpj', 'DT_COMPTC':'data', 'VL_QUOTA':'cota', 'VL_PATRIM_LIQ':'pl', 'NR_COTST':'cotistas' })

    df_final['pl'] = df_final['pl'].astype(float)
    df_final['cota'] = df_final['cota'].astype(float)
    df_final = df_final.sort_values('data', ascending=True)
    df_final = df_final.loc[df_final['data'] == data_maxima]
    df_final = df_final.loc[df_final['cotistas'] > 10]
 
    df_ordenada = df_final.sort_values("pl",ascending=False)
    df_20_maiores = df_ordenada.head(20)
    lista_20 = df_20_maiores['cnpj'].unique().tolist()
    df_filtrada = fundos.informe_diario.inf_diario_fi[['CNPJ_FUNDO_CLASSE', 'DT_COMPTC', 'VL_QUOTA', 'VL_PATRIM_LIQ', 'NR_COTST']][fundos.informe_diario.inf_diario_fi.CNPJ_FUNDO_CLASSE.isin(lista_20)]
    df_filtrada = df_filtrada.rename(columns={'CNPJ_FUNDO_CLASSE':'cnpj', 'DT_COMPTC':'data', 'VL_QUOTA':'cota', 'VL_PATRIM_LIQ':'pl', 'NR_COTST':'cotistas' })

    df_filtrada['pl'] = df_filtrada['pl'].astype(float)
    df_filtrada['cota'] = df_filtrada['cota'].astype(float)
    df_filtrada = df_filtrada.sort_values('data', ascending=True)
   
    # Calculo rentabilidade
    df_filtrada['mes'] = df_filtrada['data'].dt.month
    if mes_rentabilidade == format_m1:
        mes_calculo = mes1
    elif mes_rentabilidade == format_m2:
        mes_calculo = mes2
    elif mes_rentabilidade == format_m0:
        mes_calculo = mes0
    else:
        mes_calculo = mes3

    m1_calculo = mes_calculo.month
    m2_data = mes_calculo - relativedelta(months=1)
    m1_calculo = mes_calculo.month
    m2_calculo = m2_data.month
    data_final = df_filtrada.loc[df_filtrada['mes'] == m1_calculo]['data'].max()
    data_inicial = df_filtrada.loc[df_filtrada['mes'] == m2_calculo]['data'].max()
    dict_rentabilidade = {}
    lista_cnpj = []
    lista_rentabilidade = []
    lista_pl = []
    

    d1_form = data_inicial.strftime('%d/%m/%Y')
    d2_form = data_final.strftime('%d/%m/%Y')
    ### PEGA CDI ###
    df = get_cdi(d1_form,d2_form)
    df['valor'] = df['valor'].str.replace(",",".")
    ### CALCULA CDI ###
    df['valor'] = (df['valor'].apply(float) /100 )+ 1
    df = df.iloc[1:]
    di_acumulado = df['valor'].prod()
    di_acumulado = (di_acumulado - 1) * 100
    df['valor'] = df['valor']- 1
    df['data'] = pd.to_datetime(df['data'],format= "%d/%m/%Y")

    # RENTABILIDADE POR MÊS
    for cnpj in lista_20:
        df1 = df_filtrada.loc[(df_filtrada['cnpj'] == cnpj)]
        df2 = df1.loc[df1['data'] == data_final]
        if len(df2) <1:
            df2 = df1.loc[df1['data'] == data_final - relativedelta(days=1)]

        cota_last = df2['cota'].values[0]
        df3 = df1.loc[df1['data'] == data_inicial]
        pl = df1['pl'].values[0]
        if len(df3) <1:
            pass
        else:
            cota_first = df3['cota'].values[0]
            lista_cnpj.append(cnpj)
            lista_pl.append(pl)
            lista_rentabilidade.append((cota_last/cota_first - 1 )*100)
    dict_rentabilidade['cnpj'] = lista_cnpj
    dict_rentabilidade['rentabilidade'] = lista_rentabilidade
    dict_rentabilidade['pl'] = lista_pl
    df_agrupada_mes = pd.DataFrame(dict_rentabilidade)
    df_cadastro.columns = ['cnpj','nome']
    df_agrupada_mes = df_agrupada_mes.merge(df_cadastro,on='cnpj',how='left').drop_duplicates()
    # DF RENTABILIDADE POR DIA
    df_filtrada = df_filtrada.sort_values(['cnpj', 'data'])
    df_filtrada['retorno'] = df_filtrada.groupby('cnpj')['cota'].pct_change()
    df_diaria = df_filtrada.copy()
    df_diaria = df_diaria.merge(df_cadastro,on='cnpj',how='left')
    df_diaria = df_diaria.loc[df_diaria['mes'] == m1_calculo]
    df_diaria = df_diaria.merge(df,on='data',how='left')
    df_diaria['retorno/cdi'] = df_diaria['retorno'] / df_diaria['valor']
    df_diaria = df_diaria[['data','retorno','retorno/cdi','cnpj','nome','pl']]
    media_diaria = df_diaria.groupby('data')['retorno'].mean().reset_index()
    media_cdi_diaria = df_diaria.groupby('data')['retorno/cdi'].mean().reset_index()
    media_diaria = media_diaria.merge(media_cdi_diaria,how='left')
    # COLOCA NA TELA A RENTABILIDADE
    m1_calculo = mes_calculo.month
    ano_calculo = mes_calculo.year
    data = f"Rentabilidade {m1_calculo}/{ano_calculo}"
    st.subheader(data)
    with st.expander("Rentabilidade diária"):
        st.markdown("#### Rentabilidade diária:")
        # TRANSFORMA EM EXCEL A TABELA DIÁRIA
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            media_diaria.to_excel(writer, index=False, sheet_name="diaria")
        excel_diaria = output.getvalue()
        st.dataframe(media_diaria,hide_index= True)
        st.download_button("Baixar rentabilidade diária",data=excel_diaria,file_name='rent_diaria.xlsx')
        st.markdown("#### Abertura rentabilidade por fundo:")
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df_diaria.to_excel(writer, index=False, sheet_name="diaria")
            writer.close()
        excel_aberto_diaria = output.getvalue()
        st.dataframe(df_diaria,hide_index= True)
        st.download_button("Baixar abertura diária",data=excel_aberto_diaria,file_name='rent_aberta_diaria.xlsx')
   
    
    # CALCULA RENTABILIDADE SOBRE CDI
    rentabilidade_media = df_agrupada_mes['rentabilidade'].mean()
    cdi_acumulado = di_acumulado
    rentabilidade_cdi = rentabilidade_media / cdi_acumulado * 100
    # TRANSFORMA EM EXCEL A TABELA
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df_agrupada_mes.to_excel(writer, index=False, sheet_name="Sheet1")
        writer.close()
    excel_data = output.getvalue()
    
    with st.expander("Fundos considerados"):
        st.dataframe(df_agrupada_mes,hide_index=True)
        st.download_button("Baixar Tabela",excel_data,file_name='rentabilidade_fundos.xlsx')
    
    with st.expander("Informações mensais"):
        st.markdown("#### Rentabilidade média dos fundos:")
        rent_formatada = round(rentabilidade_media,2)
        st.text(f"{rent_formatada} %")
        st.markdown("#### Rentabilidade CDI:")
        cdi_formatado = round(cdi_acumulado,2)
        st.text(f"{cdi_formatado} %")
        st.markdown("#### Rentabilidade sobre o CDI:")
        total_formatado = round(rentabilidade_cdi,2)
        st.success(f"{total_formatado} %")


if __name__ == '__main__':
    main()
