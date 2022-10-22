"""
locustcompare
This script is used to compare the results of the previous Locust run with the current one.

A Locust run outputs 4 CSV files:
prefix_exceptions.csv
prefix_failures.csv
prefix_stats_history.csv
prefix_stats.csv

locustcompare returns 1 CSV file:
prefix_comparison_stats.csv

With locustcompare you can rename these files to a baseline.
When you have a baseline you can perform a new Locust run.
With locustcompare you can compare and validate these to the baseline.

The dependencies are python3, locustio and pandas.

Sample usage: create baseline
  $ python3 locust_compare.py --prefix example --option create_baseline
Sample usage: create merged results CSV:
  $ locust -f <scenario_file>.py --config=locust.conf
  $ python3 locust_compare.py --prefix example --option create_baseline
  $ locust -f <scenario_file>.py --config=locust.conf
  $ python3 locust_compare.py --prefix example --option create_comparison_stats
Sample usage: render output in HTML:
  $ python3 locust_compare.py --prefix example --option compare_column --column-name "<Column Name>" --renderoutput true
"""


import pandas as pd
import argparse
import os
import sys
from jinja2 import Environment, FileSystemLoader


class LocustCompare:

    def __init__(self, prefix, threshold):
        self._prefix = prefix
        self._threshold = threshold
        self._comparison_tables = []

    def create_baseline(self):
        if os.path.exists(f'{self._prefix}_stats_previous.csv'):
            if os.path.exists(f'{self._prefix}_stats.csv'):
                os.remove(f'{self._prefix}_stats_previous.csv')
                print('Removed old baseline')
        if os.path.exists(f'{self._prefix}_stats.csv'):
            os.rename(f'{self._prefix}_stats.csv', f'{self._prefix}_stats_previous.csv')
            print('Created new baseline')
        elif not os.path.exists(f'{self._prefix}_stats_previous.csv'):
            sys.exit(
                f'An error occured\n'
                f'Make sure you first run a Locust test\n'
                f'Missing: {self._prefix}_stats_previous.csv'
            )
        print('Baseline exists')

    def return_comparison_requests(self):
        new_df2 = pd.read_csv(f'{self._prefix}_stats.csv')
        pre_df2 = pd.read_csv(f'{self._prefix}_stats_previous.csv')
        merged = pd.merge(new_df2, pre_df2, on='Name', how='outer', suffixes=('_new', '_old'))
        return merged

    def create_comparison_requests(self):
        csv = self.return_comparison_requests()
        csv.to_csv(f'{self._prefix}_comparison_stats.csv')

    def compare(self, column_name):
        new_df = pd.read_csv(f'{self._prefix}_stats.csv')
        old_df = pd.read_csv(f'{self._prefix}_stats_previous.csv')

        merged_df = pd.merge(new_df, old_df, on=['Type', 'Name'], how='outer', suffixes=('_new', '_old'))
        compared_columns = merged_df[['Type', 'Name', f'{column_name}_new', f'{column_name}_old']]
        results = compared_columns[f'{column_name}_new'] / compared_columns[f'{column_name}_old']

        compared_columns.insert(len(compared_columns.columns), 'Results', results)
        self._comparison_tables.append(dict(title=column_name, body=compared_columns.to_html()))

        print(f'Comparison for {column_name} column:\n {compared_columns.to_string()}\n\n')

        return results.add_prefix(f'({column_name})_')

    def render_report(self, output_file):
        template = Environment(loader=FileSystemLoader('.')).get_template("comparison-template.html")
        html = template.render(tables=self._comparison_tables)
        html_file = open(output_file, "w")
        html_file.write(html)
        html_file.close()

    def validate(self, results):
        print(f'Threshold factor: {self._threshold}\n')

        if all(result <= self._threshold for result in results.array):
            sys.exit()
        elif any(result > self._threshold for result in results.array):
            sys.exit('Some of the requests are above the given threshold factor!')
        else:
            sys.exit('An error occurred!')

def main():
    parser = argparse.ArgumentParser(
    description='Compare previous Locust run with the current one')

    parser.add_argument('-p', '--prefix',
        required=True,
        help='Prefix for the Locust CSV files')

    parser.add_argument('-o', '--option',
        required=True,
        help='Select an option to run, view the documentation for the possible options')

    parser.add_argument('-c', '--column-name',
        required=False,
        type=str,
        help='Name of column to use for comparison.'
    )       

    parser.add_argument('-t', '--threshold',
        required=False,
        type=float,
        default=1.0,
        help='The allowed threshold factor of difference (default: %(default)s).'
    )

    parser.add_argument('-opt', '--output',
        required=False,
        type=str,
        default='comparison-report.html',
        help='HTML report file name (default: %(default)s).'
    )

    parser.add_argument('--renderoutput',
        type=str,
        help='Render output in HTML format.'
    )

    args = parser.parse_args()

    comparer = LocustCompare(args.prefix, args.threshold)

    results = pd.Series([], dtype=float)

    if args.option == 'create_baseline':
        comparer.create_baseline()
    elif args.option == 'create_comparison_stats':
        comparer.create_comparison_requests()
    elif args.option == 'compare_column':
        for column in args.column_name.split(';'):
            results = results.append(comparer.compare(column))
    else:
        print(
            f'Invalid Option: {args.option}\n'
            'View the documentation for valid options'
        )

    if args.renderoutput == 'true':
        comparer.render_report(args.output)

    comparer.validate(results)

if __name__ == '__main__':
    exit(main())