#!/bin/zsh

set -euo pipefail

# Hitta alla CSV-filer utom stats.csv
csv_filer=()
for fil in *.csv; do
    [[ "$fil" == "stats.csv" ]] && continue
    [[ -f "$fil" ]] || continue
    csv_filer+=("$fil")
done

# Kör lix.py för varje första adress i varje CSV-fil
for fil in "${csv_filer[@]}"; do
    echo "Bearbetar $fil ..."

    # Läs första raden och ta första kolumnen (adress)
    adress=$(head -n 1 "$fil" | cut -d',' -f1)

    if [[ -z "$adress" ]]; then
        echo "Ingen adress hittades i $fil, hoppar över."
        continue
    fi

    echo "Kör lix.py för $adress"

    python3 lix.py "$adress" \
        | grep -v "showSendMessage" \
        | grep -v "printable" \
        > "$fil"
done

# Bygg argumentlista till stats.py
stats_args=()
for fil in *.csv; do
    [[ "$fil" == "stats.csv" ]] && continue
    [[ -f "$fil" ]] || continue
    stats_args+=("$fil")
done

echo "Kör stats.py ..."
python3 stats.py "${stats_args[@]}" | tee stats.csv

echo "Kör grafer.py ..."
python3 grafer.py stats.csv

echo "Klart."
