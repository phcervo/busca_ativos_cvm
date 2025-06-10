import pandas as pd
import numpy as np

from ._base import Grupo

URL_BASE = "https://dados.cvm.gov.br/dados"


class CIA_ABERTA(Grupo):
    """
    A class to fetch and process CVM data from the CVM website.
    This class provides functionality to retrieve and parse various datasets
    of the group Companhias Abertas (CIA_ABERTA).

    Available datasets are:
        - cadastro
        - dfp
        - itr
        - fca
        - fre
        - ipe
        - valores_mobiliarios
        - informe_cod_governanca

    To fetch a dataset, use the method `fetch` with the dataset name as argument.

    Example:
        ```
        fundos = FI()
        fundos.fetch_historical_data("informe_diario", "2021-01-01", "2021-01-31")
        fundos.fetch_static_data("cadastro")

        cias = CIA_ABERTA()
        cias.fetch_static_data("cadastro")
        cias.fetch_historical_data("dfp", "2021-01-01", "2021-12-31")

        fiis = FII()
        fiis.fetch_historical_data("demonstracoes_financeiras", "2021-01-01", "2021-12-31")
        ```
    """

    _ENDPOINTS = {
        "cadastro": "CIA_ABERTA/CAD/DADOS/cad_cia_aberta.csv",
        "dfp": "CIA_ABERTA/DOC/DFP/DADOS/",
        "itr": "CIA_ABERTA/DOC/ITR/DADOS/",
        "fca": "CIA_ABERTA/DOC/FCA/DADOS/",
        "fre": "CIA_ABERTA/DOC/FRE/DADOS/",
        "ipe": "CIA_ABERTA/DOC/IPE/DADOS/",
        "valores_mobiliarios": "CIA_ABERTA/DOC/VLMO/DADOS/",
        "informe_cod_governanca": "CIA_ABERTA/DOC/CGVN/DADOS/",
    }

    _DEFAULT_PARSERS = {}


class FI(Grupo):
    """
    A class to fetch and process CVM data from the CVM website.
    This class provides functionality to retrieve and parse various datasets
    of the group Fundos de Investimentos (FI).

    Datasets can be found at https://dados.cvm.gov.br/organization/cvm

    Available datasets are:
        - cadastro
        - extrato
        - informe_diario
        - composicao_diversificacao
        - balancete
        - perfil_mensal
        - registro_fundo_classe

    To fetch a dataset, use the method `fetch` with the dataset name as argument.

    Example:
        ```
        fundos = FI()
        fundos.fetch_historical_data("informe_diario", "2021-01-01", "2021-01-31")
        fundos.fetch_static_data("cadastro")

        cias = CIA_ABERTA()
        cias.fetch_static_data("cadastro")
        cias.fetch_historical_data("dfp", "2021-01-01", "2021-12-31")

        fiis = FII()
        fiis.fetch_historical_data("demonstracoes_financeiras", "2021-01-01", "2021-12-31")

        ```
    """

    # Available datasets and their endpoints
    _ENDPOINTS = {
        "cadastro": "FI/CAD/DADOS/cad_fi.csv",
        "extrato": "FI/DOC/EXTRATO/DADOS/extrato_fi.csv",
        "informe_diario": "FI/DOC/INF_DIARIO/DADOS/",
        "composicao_diversificacao": "FI/DOC/CDA/DADOS/",
        "balancete": "FI/DOC/BALANCETE/DADOS/",
        "perfil_mensal": "FI/DOC/PERFIL_MENSAL/DADOS/",
        "registro_fundo_classe": "FI/CAD/DADOS/registro_fundo_classe.zip",
    }

    # Default parsers for datasets
    _DEFAULT_PARSERS = {
        # Informe diario columns are different historically
        "informe_diario": lambda df: df.rename(
            columns={"CNPJ_FUNDO": "CNPJ_FUNDO_CLASSE", "TP_FUNDO": "TP_FUNDO_CLASSE"}
        )
        .assign(
            ID_SUBCLASSE=lambda x: x.get("ID_SUBCLASSE", np.nan),
            DT_COMPTC=lambda x: pd.to_datetime(x["DT_COMPTC"], errors="coerce"),
        )
        .sort_values(["DT_COMPTC", "CNPJ_FUNDO_CLASSE"])
        .reset_index(drop=True),
    }


class FII(Grupo):
    """
    A class to fetch and process CVM data from the CVM website.
    This class provides functionality to retrieve and parse various datasets
    of the group Fundos de Investimentos Imobiliarios (FII).

    Available datasets are:
        - demonstracoes_financeiras
        - informe_anual
        - informe_mensal
        - informe_trimestral

    To fetch a dataset, use the method `fetch` with the dataset name as argument.

    To fetch a dataset, use the method `fetch` with the dataset name as argument.

    Example:
        ```
        fundos = FI()
        fundos.fetch_historical_data("informe_diario", "2021-01-01", "2021-01-31")
        fundos.fetch_static_data("cadastro")

        cias = CIA_ABERTA()
        cias.fetch_static_data("cadastro")
        cias.fetch_historical_data("dfp", "2021-01-01", "2021-12-31")

        fiis = FII()
        fiis.fetch_historical_data("demonstracoes_financeiras", "2021-01-01", "2021-12-31")
        ```
    """

    _ENDPOINTS = {
        "demonstracoes_financeiras": "FII/DOC/DFIN/DADOS/",
        "informe_anual": "FII/DOC/INF_ANUAL/DADOS/",
        "informe_mensal": "FII/DOC/INF_MENSAL/DADOS/",
        "informe_trimestral": "FII/DOC/INF_TRIMESTRAL/DADOS/",
    }

    _DEFAULT_PARSERS = {}
