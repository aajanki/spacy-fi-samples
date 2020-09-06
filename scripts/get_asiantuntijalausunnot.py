# Download Asiantuntijalausunto metadata and documents from
# avoindata.eduskunta.fi

import csv
import io
import requests
import requests.exceptions
import shutil
import time
from datetime import date
from pathlib import Path
from urllib.parse import urlparse, unquote
from tqdm import tqdm
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

avoin_data_host = 'https://avoindata.eduskunta.fi'


def main():
    datadir = Path('data/asiantuntijalausunnot')
    docdir = datadir / 'pdf'
    metadata_filename = datadir / 'metadata.csv'

    docdir.mkdir(parents=True, exist_ok=True)

    metadata = get_asiantuntijalausunnot_metadata()
    metadata2018 = filter_metadata(metadata, 2018)
    print(f'Found metadata for {len(metadata2018)} documents')
    save_metadata(metadata2018, metadata_filename)

    download_documents(metadata2018, docdir)


def get_asiantuntijalausunnot_metadata():
    url = 'https://eduskunta-avoindata-documents-prod.s3-eu-west-1.amazonaws.com/expert-statement/Asiantuntijalausunnot-2015-2019-csv.csv'
    r = requests.get(url)
    r.raise_for_status()
    r.encoding = 'UTF-8'
    
    reader = csv.DictReader(io.StringIO(r.text))
    return [x for x in reader]



def filter_metadata(metadata, year):
    return [
        x for x in metadata
        if x['Url'] and
        date.fromisoformat(x['Laadintapäivämäärä']).year == year and
        not most_likely_swedish(x)
    ]


def save_metadata(metadata, filename):
    with open(filename, 'w', newline='') as f:
        fieldnames = ['Valiokunta', 'Asian tunnus', 'Laadintapäivämäärä',
                      'Asiantuntijalausunnon kuvaus', 'Url']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in metadata:
            writer.writerow(row)


def download_documents(metadata, docdir):
    retry = Retry(total=3,
                  backoff_factor=0.5,
                  status_forcelist=[500, 502, 503, 504])
    session = requests.Session()
    session.mount('http://', HTTPAdapter(max_retries=retry))
    session.mount('https://', HTTPAdapter(max_retries=retry))

    print('Downloading documents')
    for i, x in enumerate(tqdm(metadata)):
        time.sleep(0.2)

        url = x['Url']
        filename = unquote(urlparse(url).path).split('/')[-1]
        destfile = docdir / filename

        try:
            save_as_file(url, destfile, session)
        except requests.exceptions.RequestException as ex:
            print(ex)


def save_as_file(url, filename, session):
    with open(filename, 'wb') as f, \
         session.get(url, stream=True, timeout=60) as r:
        r.raise_for_status()
        shutil.copyfileobj(r.raw, f)


def most_likely_swedish(row):
    description = row['Asiantuntijalausunnon kuvaus'].lower()

    return (('ahvenanmaan' in description or 'åbo akademi' in description or
             ('förbundet' in description and not 'konsumentförbundet' in description))
            and not (' suomennos ' in description or ' su ' in description))


if __name__ == '__main__':
    main()
