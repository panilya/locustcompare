# locustcompare

locustcompare is a fork of [Locust-Compare](https://github.com/tlolkema/Locust-Compare)

At the moment, [Locust-Compare](https://github.com/tlolkema/Locust-Compare) is outdated and doesn't work. 

locustcompare is created to replace [Locust-Compare](https://github.com/tlolkema/Locust-Compare) and to add more useful features.

## Features:

- Merge 2 CSV files with test results to 1 CSV file.
- Compare by column(s).
- Compare test results in HTML.

## Installation

`pip3 install pandas`
`pip3 install locustio`

## Configuration

Configure Locust in `locust.conf`

## Step-by-step instruction on how to run

`locust -f <scenario_file>.py --config=locust.conf`

`python3 locust_compare.py --prefix example --option create_baseline`

Run Locust again: `locust -f <scenario_file>.py --config=locust.conf`

If you want to see diff in HTML format procced to the next section.

If you want to see diff as CSV files merged to one CSV file, run the next command:

`python3 locust_compare.py --prefix example --option create_comparison_stats`

Then, you should see `prefix_comparison_stats.csv` with 2 merged CSV files.

## Show tests summary diff in HTML

`python3 locust_compare.py --prefix example --option compare_column --column-name "column1;column2;column3" --renderoutput true` 

For example:

`python3 locust_compare.py --prefix example --option compare_column --column-name "Average Response Time" --renderoutput true`