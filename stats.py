#!/usr/bin/env python3

import sys
import csv
import math
from statistics import mean, stdev


def read_lix_values(filename):
    values = []

    with open(filename, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)

        for row in reader:
            if len(row) < 2:
                continue

            try:
                lix = float(row[1])
                values.append(lix)
            except ValueError:
                pass

    return values


def main():
    if len(sys.argv) < 2:
        print(
            f"Användning: {sys.argv[0]} <csv-fil> [fler csv-filer...]",
            file=sys.stderr
        )
        sys.exit(1)

    # CSV-header till stdout
    print("fil,antal_sidor,medel_lix,standardavvikelse,min,max")

    for filename in sys.argv[1:]:
        values = read_lix_values(filename)

        if not values:
            print(f"{filename},0,0,0,0,0")
            continue

        avg = mean(values)

        # standardavvikelse kräver minst 2 värden
        if len(values) >= 2:
            sd = stdev(values)
        else:
            sd = 0.0

        min_value = min(values)
        max_value = max(values)

        print(
            f"{filename},"
            f"{len(values)},"
            f"{avg:.2f},"
            f"{sd:.2f},"
            f"{min_value:.2f},"
            f"{max_value:.2f}"
        )


if __name__ == "__main__":
    main()
