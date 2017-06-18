import io
import pandas as pd
import requests

from opendatabo.common import retry_on, DataNotAvailableException


@retry_on(Exception, retries=2, delay=lambda i : 2.0 ** i)
def fetch_data(year: int, month: int, municipality: int) -> pd.DataFrame:
  url = 'http://vmpc.economiayfinanzas.gob.bo/reporteGobernaciones.asp'
  query = "gestion={}&mes={}&municipio={}".format(year, month, municipality)

  r = requests.get(url + '?' + query)
  if (r.status_code != 200):
    raise DataNotAvailableException()

  data = r.text

  raw_df = pd.read_html(io.StringIO(data))

  return clean_municipality_data(raw_df[1])


def clean_municipality_data(df: pd.DataFrame) -> pd.DataFrame:
  #df.drop(df.loc[0, :])
  return df

