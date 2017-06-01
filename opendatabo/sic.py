import io

import pandas as pd
import requests
import traceback


def get_market_prices(when, where):
    if when == 'hoy':
        url = 'http://www.sicsantacruz.com/sic/sic2014/pref_sc_hoy_export.php'
    else:
        url = 'http://www.sicsantacruz.com/sic/sic2014/pref_{WHERE}_{WHEN}_ano_export.php'.format(WHERE=where,
                                                                                                  WHEN=when)

    r = requests.post(url, data={'type': 'csv', 'records': 'all'})

    if r.status_code != 200:
        raise RuntimeError('request was not successful')

    return pd.read_csv(io.StringIO(r.content.decode('utf-8')))


def save_market_prices(when, where, output, fformat):
    if when == 'hoy':
        url = 'http://www.sicsantacruz.com/sic/sic2014/pref_sc_hoy_export.php'
    else:
        url = 'http://www.sicsantacruz.com/sic/sic2014/pref_{WHERE}_{WHEN}_ano_export.php'.format(WHERE=where,
                                                                                                  WHEN=when)

    if output is None:
        output_file = 'precios_' + where + '_' + when + '.' + fformat
    else:
        output_file = output

    params = {'type': fformat, 'records': 'all'}
    headers = {'Content-type': 'application/x-www-form-urlencoded'}

    try:
        print('Requesting data for ' + where + ' in ' + when + ' from:\n' + url)

        r = requests.post(url, data=params, headers=headers)

        if r.status_code == 200:
            print('Writing output to ' + output_file)

            with open(output_file, 'wt') as the_file:
                the_file.write(r.content.decode('utf-8'))
        elif r.status_code == 404:
            print('No data for ' + where + ' in ' + when)
    except Exception as e:
        print('Something went wrong :(')
        print(traceback.format_exc())
