import argparse

import requests
import xml.etree.ElementTree as ET
import pandas as pd
from urllib3.exceptions import ConnectTimeoutError

DEFAULT_OUTPUT_CSV_FILE = "researcher_ids.csv"

DEFAULT_INPUT_CSV_FILE = "researcher_ids_base.csv"

SUBSET = None

with_idref = 0
with_orcid = 0
with_idhal = 0
with_orcid_and_idhal = 0


def _parse_args():
    parser = argparse.ArgumentParser()
    # Required positional argument
    parser.add_argument(
        "--input_csv",
        help="Researcher identifiers input file",
        required=False,
        type=str,
        default=DEFAULT_INPUT_CSV_FILE,
    )
    parser.add_argument(
        "--output_csv",
        help="Researcher identifiers output file",
        required=False,
        type=str,
        default=DEFAULT_OUTPUT_CSV_FILE,
    )
    return parser.parse_args()


def _get_identifiers(idref):
    global with_idref, with_orcid, with_idhal, with_orcid_and_idhal
    if idref:
        with_idref += 1
    else:
        return None, None
    if with_idref % 100 == 0:
        _print_stats(with_idhal, with_idref, with_orcid, with_orcid_and_idhal)
    url = f"https://www.idref.fr/services/idref2id/{idref}"
    try:
        response = requests.get(url)
    except ConnectTimeoutError:
        print(f"Timeout for {idref}")
        return _get_identifiers(idref)

    if response.status_code == 200:
        root = ET.fromstring(response.text)
        orcid = None
        idhal = None

        for query in root.findall(".//query/result"):
            source = query.find("source").text
            identifier = query.find("identifiant").text
            if source == "ORCID":
                orcid = identifier
                with_orcid += 1
            elif source == "HAL":
                idhal = identifier
                with_idhal += 1
        print(orcid, idhal)
    else:
        print(f"Error: {response.status_code} for {idref}")
        return None, None
    if orcid and idhal:
        with_orcid_and_idhal += 1
    return orcid, idhal


def _print_stats(with_idhal, with_idref, with_orcid, with_orcid_and_idhal):
    print(
        f"with_idref: {with_idref}, with_orcid: {with_orcid}, with_idhal: {with_idhal}, with_orcid_and_idhal: {with_orcid_and_idhal}"
    )


def update_csv(input_csv, output_csv):
    df = pd.read_csv(input_csv, sep=",")
    if SUBSET:
        df = df.head(SUBSET)
    df["orcid"], df["idhal"] = zip(*df["idref"].apply(_get_identifiers))
    df.to_csv(output_csv, index=False)


if __name__ == "__main__":
    args = _parse_args()
    update_csv(args.input_csv, args.output_csv)
    _print_stats(with_idhal, with_idref, with_orcid, with_orcid_and_idhal)
