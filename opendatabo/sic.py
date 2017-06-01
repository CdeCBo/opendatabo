import requests
import traceback


def save_market_prices(when, where, output, fformat):
    if when == 'hoy':
        url = 'http://www.sicsantacruz.com/sic/sic2014/pref_sc_hoy_export.php'
    else:
        url = 'http://www.sicsantacruz.com/sic/sic2014/pref_{WHERE}_{WHEN}_ano_export.php'.replace('{WHEN}', when).replace(
            '{WHERE}', where)

    if output is None:
        output_file = 'precios_' + where + '_' + when + '.' + fformat
    else:
        output_file = fformat

    params = {'type': fformat, 'records': 'all'}
    headers = {'Content-type': 'application/x-www-form-urlencoded'}

    try:
        print('Requesting data for ' + where + ' in ' + when + ' from:\n' + url)

        r = requests.post(url, data=params, headers=headers)

        if (r.status_code == 200):
            print('Writing output to ' + output_file)

            with open(output_file, 'w') as the_file:
                the_file.write(r.content)
        elif (r.status_code == 404):
            print('No data for ' + where + ' in ' + when)
    except Exception as e:
        print('Something went wrong :(')
        print(traceback.format_exc())
