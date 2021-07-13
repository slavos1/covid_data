# data from https://coronavirus.data.gov.uk/details/cases
from pathlib import Path
import json
from datetime import datetime
from functools import partial

import pandas as pd

STAR_COUNT = 40
UNICODE = {
    "middle_dot": "\u00B7",
    "half_triangular_colon": "\u02D1",
    "Greek Ano Teleia": "\u0387",
    "Syriac Harklean Asteriscus": "\u070D",
    "Nko Letter Ee": "\u07CB",
    "bullet": "\u2022",
    "can_middle_dot": "\u1427",
}
GRAPH_DOT = UNICODE["bullet"]
# EMPTY_CHAR = UNICODE["can_middle_dot"]  # "."
EMPTY_CHAR = " "


def get_graph_line(perc, width=STAR_COUNT, c=GRAPH_DOT, none="-", empty_char=EMPTY_CHAR):
    n = int(perc * width)
    graph_line = none if n < 1 else n * c
    return graph_line + (width - len(graph_line)) * empty_char


def add_graph(t, column, out_column, width=STAR_COUNT):
    count_min = t[column].min()
    span = t[column].max() - count_min
    perc = (t[column] - count_min) / span
    t[out_column] = perc.apply(partial(get_graph_line, width=width))


def parse(path, last=40):
    def _iter():
        for d in json.load(path.open())["data"]:
            d.update(date=datetime.strptime(d["date"], "%Y-%m-%d"))
            yield d

    date_type = pd.DatetimeTZDtype(tz="Europe/London")
    t = (
        pd.DataFrame(_iter())
        .rename(columns=dict(newCasesByPublishDate="new_daily_cases"))
        .set_index("date")
        .sort_index()
    )
    t["daily_delta"] = t.diff()
    t["7day_rolling_avg"] = t.new_daily_cases.rolling(7).mean()
    recent = t.tail(last).copy()
    add_graph(recent, "new_daily_cases", "daily_graph", width=20)
    add_graph(recent, "7day_rolling_avg", "7day_rolling_avg_graph")
    print(
        recent.to_string(
            columns="new_daily_cases daily_delta daily_graph 7day_rolling_avg 7day_rolling_avg_graph".split(),
            formatters=dict(
                # justify left
                graph=lambda x: f"{{:{STAR_COUNT}s}}".format(x),
                # show comma as thousands delimiter
                new_daily_cases=lambda x: "{:,d}".format(x),
            ),
        )
    )


if __name__ == "__main__":
    parse(Path("daily_cases.json"))
