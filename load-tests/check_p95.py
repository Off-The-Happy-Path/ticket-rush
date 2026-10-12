"""Fail the build if the 95th percentile is above a limit.

Usage: python check_p95.py results_stats.csv 500
Reads the "Aggregated" row that `locust --csv results` writes.
"""
import csv
import sys

stats_file, limit_ms = sys.argv[1], float(sys.argv[2])

with open(stats_file, newline="") as f:
    total = next(row for row in csv.DictReader(f) if row["Name"] == "Aggregated")

p95 = float(total["95%"])
print(f"p95 = {p95:.0f} ms (limit {limit_ms:.0f} ms)")
if p95 > limit_ms:
    sys.exit("FAIL: p95 is above the limit")
