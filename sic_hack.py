import argparse
import requests
import traceback

parser = argparse.ArgumentParser(description="Export data from SIC's website to a file")

# Not an FB plug
parser.add_argument('-f', '--format', type=str, default='csv', help='File format to request', choices=['csv', 'xml'])
parser.add_argument('-l', '--location', type=str, default='sc', help="City code, known values are [sc, trd, cbb]")
parser.add_argument('-o', '--output', type=str, help='Output file')
parser.add_argument('-w', '--when', type=str, default='hoy', help="Year for the dataset you want")

args = parser.parse_args()

when = args.when
where = args.location

if when == 'hoy':
  url = 'http://www.sicsantacruz.com/sic/sic2014/pref_sc_hoy_export.php'
else:
  url = 'http://www.sicsantacruz.com/sic/sic2014/pref_{WHERE}_{WHEN}_ano_export.php'.replace('{WHEN}', when).replace('{WHERE}', where)

if args.output is None:
  output_file = 'precios_' + where + '_' + when + '.' + args.format
else:
  output_file = args.fformat

params = {'type': args.format, 'records': 'all'}
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

