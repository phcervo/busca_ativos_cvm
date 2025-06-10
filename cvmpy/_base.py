import pandas as pd
import os

from typing import Optional, Callable, Union, List, Dict
from ._utils import get_file_period, get_page_files_urls, read_zipfile

URL_BASE = "https://dados.cvm.gov.br/dados"


class Conjunto:
    """
    A class to fetch and process CVM data from the CVM website.
    """

    @staticmethod
    def _validate_endpoint(endpoint: str) -> None:
        if not (endpoint.endswith("csv") or endpoint.endswith("zip")):
            raise ValueError("Invalid endpoint. Must be a CSV or ZIP file.")

    @staticmethod
    def _read_static_data(
        endpoint: str, verbose: bool = True
    ) -> Union[pd.DataFrame, Dict[str, pd.DataFrame]]:
        """
        Reads static data from a given endpoint.

        Args:
            endpoint (str): Complementary URL to https://dados.cvm.gov.br/dados.
            verbose (bool, optional): Print messages. Defaults to True.

        Returns:
            Union[pd.DataFrame, Dict[str, pd.DataFrame]]: Static data.
        """
        Conjunto._validate_endpoint(endpoint)
        url = f"{URL_BASE}/{endpoint}"
        if verbose:
            print(f"Fetching data from: {url}")
        if url.endswith("csv"):
            data = pd.read_csv(url, sep=";", encoding="latin-1", low_memory=False,on_bad_lines='skip')
        else:  # ZIP file
            data = read_zipfile(url)

        if isinstance(data, dict) and len(data) == 1:
            # Return the single DataFrame directly
            return next(iter(data.values()))  
        return data

    @staticmethod
    def _read_historical_data(
        endpoint: str,
        start_date: str,
        end_date: Optional[str] = None,
        verbose: bool = True,
        parser: Optional[Union[Callable, List[Callable]]] = None,
    ) -> dict:
        """
        Reads historical data from a given endpoint.

        Args:
            endpoint (str): Complementary URL to https://dados.cvm.gov.br/dados.

            start_date (str): Start date in the format 'YYYY-MM-DD'.

            end_date (str, optional): End date in the format 'YYYY-MM-DD'. Defaults to None.

            verbose (bool, optional): Print messages. Defaults to True.

            parser (Optional[Callable], optional): Function to parse the data. Defaults to None.

        Returns:
            dict: Dictionary with the form {filename: pd.DataFrame}.
        """
        if not endpoint.endswith("/"):
            if "." in endpoint:
                raise ValueError("Endpoint given is not historical.")
            raise ValueError("Endpoint must end with a slash.")

        start_date = pd.Timestamp(start_date)
        end_date = pd.Timestamp(end_date or pd.Timestamp.today())

        if start_date > end_date:
            raise ValueError("Start date must be less than end date.")

        # Get URLs for of the files for the specified endpoint
        # It also returns url of subdirectories
        list_urls = get_page_files_urls(f"{URL_BASE}/{endpoint}")
        if not list_urls:
            raise RuntimeError("No URLs found. The source URL may have changed.")

        # Dictionary with the form {url: [start_date, end_date]}
        dict_url_periods = {
            url: get_file_period(os.path.basename(url)) for url in list_urls
        }

        # Filter URLs based on date range
        selected_urls = [
            url
            for url, period in dict_url_periods.items()
            if period[0] <= end_date and period[1] >= start_date
        ]

        # Reading files and storing them in dict_dfs
        dict_dfs = {}
        for url in selected_urls:
            print(url) if verbose else None
            if url.endswith("zip"):
                dict_dfs.update(read_zipfile(url, parser=parser))
            else:
                df = pd.read_csv(url, sep=";", encoding="latin-1", low_memory=False,on_bad_lines='skip')
                if parser is not None:
                    if isinstance(parser, list):
                        for func in parser:
                            df = func(df)
                    elif callable(parser):
                        df = parser(df)
                    else:
                        raise ValueError("Invalid parser.")
                filename = os.path.basename(url)
                dict_dfs[filename] = df

        if not dict_dfs:
            if verbose:
                print("No data available for the specified date range.")
            return None

        return dict_dfs


class Grupo:
    """
    A class to fetch and process CVM data from the CVM website.
    Grupo classes should inherit from this class.
    """

    # Available datasets and their endpoints
    _ENDPOINTS = {}

    # Default parsers for datasets
    _DEFAULT_PARSERS = {}

    def fetch_historical_data(
        self,
        dataset: str,
        start_date: str,
        end_date: Optional[str] = None,
        verbose: bool = True,
        parser: Optional[Callable] = None,
        return_df: bool = False,
    ) -> None:
        """
        Fetch historical data from the CVM website.

        Args:
            dataset (str): Dataset to fetch.
                See datasets for available options.

            start_date (str): Start date in the format 'YYYY-MM-DD'.

            end_date (Optional[str], optional): End date in the format 'YYYY-MM-DD'.
                If None, uses the current date.
                Defaults to None.

            verbose (bool, optional): If True, prints messages.

            parser (Optional[Callable], optional): Function to parse the data.
                Defaults to None.

            return_df (bool, optional): If True, returns the DataFrame instead of
                setting it as an attribute.
                Defaults to False.

        Returns:
            None or pd.DataFrame: If return_df is True, returns the DataFrame.
        """

        # Check if dataset is valid
        if dataset not in self._ENDPOINTS.keys():
            err_msg = (
                f"Invalid dataset: {dataset}. "
                f"Available options: {list(self._ENDPOINTS.keys())}"
            )
            raise ValueError(err_msg)

        parsers = [self._DEFAULT_PARSERS.get(dataset), parser]
        parsers = [p for p in parsers if p]

        dict_dfs = Conjunto._read_historical_data(
            endpoint=self._ENDPOINTS[dataset],
            start_date=start_date,
            end_date=end_date,
            verbose=verbose,
            parser=parsers if parsers else None,
        )

        # Group by root filenames
        list_root = list(set([s.rsplit("_", 1)[0] for s in dict_dfs.keys()]))

        grouped_dfs = {}
        for root_name in list_root:
            list_dfs = [
                df
                for file, df in dict_dfs.items()
                if file.startswith(root_name) and not df.isna().all().all()
            ]
            grouped_dfs[root_name] = (
                pd.concat(list_dfs, ignore_index=True) if list_dfs else pd.DataFrame()
            )

        for df in grouped_dfs.values():
            for col in ["DT_REFER", "DT_COMPTC"]:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors="coerce")
                    df = df[(df[col] >= start_date) & (df[col] <= end_date)]

        if return_df:
            return (
                grouped_dfs
                if len(grouped_dfs) > 1
                else next(iter(grouped_dfs.values()))
            )

        conjunto = Conjunto()
        for file, df in grouped_dfs.items():
            setattr(conjunto, file, df)
        setattr(self, dataset, conjunto)

        if verbose:
            print("Done.")

    def fetch_static_data(
        self, dataset: str, verbose: bool = True, return_df: bool = False
    ) -> None:
        """
        Fetch static data from the CVM website.

        Args:
            dataset (str): Dataset to fetch.
                See datasets for available options.

            verbose (bool, optional): If True, prints messages. Defaults to True.

            return_df (bool, optional): If True, returns the DataFrame instead of
                setting it as an attribute.
                Defaults to False.

        Returns:
            None, pd.DataFrame, dict: If return_df is True, returns the DataFrame.
        """
        if dataset not in self._ENDPOINTS.keys():
            err_msg = (
                f"Invalid dataset: {dataset}. "
                f"Available options: {list(self._ENDPOINTS.keys())}"
            )
            raise ValueError(err_msg)

        static_data = Conjunto._read_static_data(
            self._ENDPOINTS[dataset], verbose=verbose
        )

        print("Done.") if verbose else None

        if return_df:
            return static_data

        if isinstance(static_data, dict):
            for file, df in static_data.items():
                if file.endswith(".csv"):
                    file = file.rsplit(".", 1)[0]
                setattr(self, file, df)
        elif isinstance(static_data, pd.DataFrame):
            setattr(self, dataset, static_data)
        else:
            raise ValueError("Invalid return type.")

    @property
    def datasets(self) -> List[str]:
        return list(self._ENDPOINTS.keys())