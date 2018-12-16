#!/usr/bin/env python3

import argparse
from bs4 import BeautifulSoup
from collections import Counter
from scipy.interpolate import spline

import matplotlib as mpl

mpl.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np


def main(input_filename, output_filename):

    with open(input_filename, "r", encoding="utf8") as f:
        xml = f.read()

    soup = BeautifulSoup(xml, "lxml")

    y = []
    for record in soup.xml.records:
        try:
            year = record.dates.year.text.strip()
            y.append(int(year))
        except AttributeError:
            # Sometimes we end up on a NavigableString node,
            # which won't have any child nodes. Just skip it
            pass

    counter = Counter(y)

    years = sorted([int(x) for x in counter.keys()])
    count = []
    for c in sorted(counter.keys()):
        count.append(counter[c])
    total = list(np.cumsum(count))

    ax1 = plt.figure().add_subplot(111)
    ax1.bar(years, count, color="#FF8888", label="Publications")
    plt.ylabel("Peer-Reviewed Publications")

    ynew = np.linspace(min(years), max(years), 100)
    smooth = spline(years, total, ynew)

    ax2 = plt.twinx()
    ax2.plot(ynew, smooth, label="Cumulative")

    rows = ["Publications", "Cumulative"]
    table = plt.table(
        cellText=[count, total], rowLabels=rows, colLabels=years, loc="bottom"
    )

    props = table.properties()
    cells = props["child_artists"]
    for cell in cells:
        cell.set_height(0.1)
        cell.set_width(0.104)

    red = mpatches.Patch(color="#FF8888", label="Publications")
    blue = mpatches.Rectangle((0, 0), 1, 8, color="#1F77B4", label="Cumulative")
    plt.legend(handles=[red, blue])

    ax2.set_ylim(ymin=0)

    plt.savefig(output_filename, bbox_inches="tight")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate svg graph of TCIA papers by year")

    parser.add_argument(
        'input_file',
        help='EndNote XML export file'
    )
    parser.add_argument(
        'output_file',
        help='Output filename, SVG'
    )

    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_args()
    main(args.input_file, args.output_file)
