# data from https://coronavirus.data.gov.uk/details/cases
from pathlib import Path
import json
from datetime import datetime

import pandas as pd

STAR_COUNT = 72
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
EMPTY_CHAR = UNICODE["can_middle_dot"]  # "."


def get_graph_line(perc, c=GRAPH_DOT, none="-", empty_char=EMPTY_CHAR):
    n = int(perc * STAR_COUNT)
    return none if n < 1 else n * c + (STAR_COUNT - n) * empty_char


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
    recent = t.tail(last).copy()
    count_min = recent.new_daily_cases.min()
    print(count_min, recent.new_daily_cases.max())
    span = recent.new_daily_cases.max() - count_min
    recent["perc"] = (recent.new_daily_cases - count_min) / span
    recent["graph"] = recent.perc.apply(get_graph_line)
    print(
        recent.to_string(
            columns="new_daily_cases daily_delta graph".split(),
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
