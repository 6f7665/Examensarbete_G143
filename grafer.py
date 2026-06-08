#!/usr/bin/env python3

import sys
import csv
import statistics

import plotly.graph_objects as go


# ----------------------------------------
# Läs stats.csv
# ----------------------------------------

def read_stats_csv(filename):
    files = []

    with open(filename, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            files.append(row["fil"])

    return files


# ----------------------------------------
# Läs originalfil
# ----------------------------------------

def read_school_csv(filename):
    values = []
    first_url = None

    with open(filename, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)

        for row in reader:
            if len(row) < 2:
                continue

            url = row[0].strip()

            if first_url is None:
                first_url = url

            try:
                lix = float(row[1])
                values.append(lix)
            except ValueError:
                pass

    return first_url, sorted(values)


# ----------------------------------------
# Kvartiler
# ----------------------------------------

def quartiles(values):
    q = statistics.quantiles(
        values,
        n=4,
        method="inclusive"
    )

    q1 = q[0]
    q3 = q[2]

    median = statistics.median(values)

    return q1, median, q3


# ----------------------------------------
# Main
# ----------------------------------------

def main():
    if len(sys.argv) != 2:
        print(
            f"Användning: {sys.argv[0]} stats.csv"
        )
        sys.exit(1)

    stats_file = sys.argv[1]

    csv_files = read_stats_csv(stats_file)

    fig = go.Figure()

    for filename in csv_files:
        school_url, values = read_school_csv(filename)

        if not values:
            continue

        fig.add_trace(
            go.Box(
                y=values,
                name=school_url,
                boxmean=True,
            )
        )

    fig.update_layout(
        title="LIX-värden för gymnasieskolors webbplatser",
        yaxis_title="LIX",
        xaxis_title="Webbplats",
        template="plotly_white",
        width=1600,
        height=900,
        yaxis=dict(range=[10,60]),
    )

    output_file = "lix_boxplot.html"

    fig.write_html(output_file)

    print(f"Skrev {output_file}")


if __name__ == "__main__":
    main()
