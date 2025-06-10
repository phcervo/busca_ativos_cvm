import pandas as pd
import zipfile
import requests
import io

from bs4 import BeautifulSoup
from datetime import datetime

from typing import List, Optional, Union, Callable


def get_page_files_urls(endpoint: str) -> List[str]:
    """
    Get files URLs from a CVM data page and its subfolders.
    It recursively gets all files from the page and its subfolders.

    Args:
        endpoint (str): CVM data page endpoint. It should end with a slash.

    Returns:
        List[str]: List of files URLs.
    """
    if "https://dados.cvm.gov.br/dados" not in endpoint:
        raise ValueError("Endpoint must be from CVM.")
    response = requests.get(endpoint)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    pre_section = soup.find("pre")
    list_objects = [link.text for link in pre_section.find_all("a")]

    list_url_files = [
        f"{endpoint}{url}" for url in list_objects if not url.endswith("/")
    ]

    list_folders = [
        link for link in list_objects if link.endswith("/") if link != "../"
    ]

    list_urls_in_folders = []
    for folder in list_folders:
        list_urls_in_folders += get_page_files_urls(endpoint + folder)

    return list_url_files + list_urls_in_folders


def get_file_period(filename: str) -> datetime:
    """
    Get file date from a CVM data page.

    Args:
        filename (str): CVM data page filename.

    Returns:
        str: File date.
    """
    filedate = filename.split("_")[-1].split(".")[0]

    if len(filedate) == 4:  # YYYY format
        start_date = datetime.strptime(filedate, "%Y").replace(month=1, day=1)
        end_date = datetime.strptime(filedate, "%Y").replace(month=12, day=31)

    elif len(filedate) == 6:  # YYYYMM format
        start_date = datetime.strptime(filedate, "%Y%m")  # Start of the month

        next_month = (start_date.month % 12) + 1  # Calculate next month

        end_date = start_date.replace(day=1).replace(
            month=next_month,
            year=start_date.year if next_month > 1 else start_date.year + 1,
        ) - pd.Timedelta(
            days=1
        )  # Subtract one day to get the last day of the month
    else:
        raise ValueError(f"Invalid date format: {filedate}.")
    return [start_date, end_date]


def read_zipfile(
    url: str,
    filename: Union[str, List[str], Callable] = "all",
    parser: Optional[Union[Callable, List[Callable]]] = None,
    **kwargs,
) -> dict:
    """
    Read a CSV file from a ZIP file URL.

    Args:
        url (str): URL to the ZIP file.

        verbose (bool, optional): If True, prints messages.
            Defaults to True.

        parser (Optional[Callable], optional):
            Function to parse the DataFrame.
            Should receive a DataFrame, file name, and return a DataFrame.
            Can be used to apply custom transformations to the data.

    Returns:
        dict: Dictionary with the form {filename: pd.DataFrame}
    """

    if not url.endswith(".zip"):
        raise ValueError("Provided URL must point to a ZIP file.")

    response = requests.get(url)
    response.raise_for_status()

    with zipfile.ZipFile(io.BytesIO(response.content)) as zf:

        csv_files = [name for name in zf.namelist() if name.endswith(".csv")]

        # Handle non-CSV files
        non_csv_files = [name for name in zf.namelist() if not name.endswith(".csv")]
        if non_csv_files:
            print(f"Non-CSV files in ZIP: {non_csv_files}")

        # Handle filename parameter logic
        if filename is None and len(csv_files) > 1:
            raise ValueError(
                f"Multiple CSV files found: {csv_files}. Please specify a filename or use 'all'."
            )

        # Read CSV files into DataFrames
        data_frames = {}
        for csv_file in csv_files:
            with zf.open(csv_file) as f:
                df = pd.read_csv(
                    f, encoding="latin-1", sep=";",on_bad_lines='skip', engine='python', **kwargs
                )
                if parser is not None:
                    if callable(parser):
                        df = parser(df)
                    elif isinstance(parser, list):
                        for func in parser:
                            df = func(df)
                    else:
                        raise ValueError(
                            "Parser must be a function or a list of functions"
                        )
                data_frames[csv_file] = df

        return data_frames
