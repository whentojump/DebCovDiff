import csv
import sys


with open('data/bugs.csv', 'r', newline='', encoding='utf-8') as b_file:
    reader_b = csv.reader(b_file)
    for row in reader_b:
        print(f"{row[0]} @@@@@ {row[2]}")
