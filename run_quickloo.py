import argparse
from pathlib import Path
from io import StringIO

import pandas as pd
import requests
import matplotlib.pyplot as plt

BASE = "https://soto.podaac.earthdatacloud.nasa.gov/hydrocron/v1/timeseries"
FIELDS = "reach_id,time_str,wse,width,slope"

def fetch_reach(reach_id: str, start: str, end: str) -> pd.DataFrame:
    params = {
        "feature": "Reach",
        "feature_id": str(reach_id),
        "start_time": start,
        "end_time": end,
        "fields": FIELDS,
    }
    r = requests.get(BASE, params=params, headers={"Accept": "text/csv"}, timeout=60)
    r.raise_for_status()

    txt = r.text.strip()
    # Hydrocron sometimes wraps the CSV in quotes and escapes newlines
    if txt.startswith('"') and txt.endswith('"'):
        txt = txt[1:-1]
    txt = txt.replace("\\n", "\n")

    df = pd.read_csv(StringIO(txt))
    if "time_str" not in df.columns:
        raise KeyError(f"'time_str' missing. Columns: {list(df.columns)}")

    df = df[df["time_str"].ne("no_data")].copy()

    for col in ["wse", "width", "slope"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        df.loc[df[col] <= -1e11, col] = pd.NA

    df["time"] = pd.to_datetime(df["time_str"], utc=True, errors="coerce")
    df = df.dropna(subset=["time"]).sort_values("time").reset_index(drop=True)
    return df

def plot_series(df: pd.DataFrame, y: str, ylabel: str, outpath: Path, rolling: str = "60D"):
    d = df[["time", y]].dropna().sort_values("time").set_index("time")
    roll = d[y].rolling(rolling).median()

    plt.rcParams.update({
        "figure.dpi": 140,
        "savefig.dpi": 300,
        "font.size": 12,
        "axes.titlesize": 18,
        "axes.labelsize": 13
    })

    fig, ax = plt.subplots(figsize=(13, 6.5))
    ax.plot(d.index, d[y].values, marker="o", markersize=4, linewidth=1, alpha=0.9)
    ax.plot(roll.index, roll.values, linewidth=3, alpha=0.95)
    ax.set_title(f"Reach {REACH_ID} — SWOT {y.upper()} (Hydrocron)\nRaw observations + {rolling} rolling median")
    ax.set_xlabel("Date (UTC)")
    ax.set_ylabel(ylabel)
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(outpath, bbox_inches="tight")
    plt.close(fig)

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="SWOT Hydrocron reach quicklook")
    ap.add_argument("--reach-id", required=True, help="SWORD reach_id (e.g., 73218000131)")
    ap.add_argument("--start", default="2023-01-01T00:00:00Z", help="ISO time like 2023-01-01T00:00:00Z")
    ap.add_argument("--end", default="2025-12-31T23:59:59Z", help="ISO time like 2025-12-31T23:59:59Z")
    ap.add_argument("--rolling", default="60D", help="Rolling median window (e.g., 60D, 90D)")
    ap.add_argument("--outdir", default="outputs", help="Output folder")
    args = ap.parse_args()

    REACH_ID = args.reach_id

    out = Path(args.outdir) / str(REACH_ID)
    out.mkdir(parents=True, exist_ok=True)

    df = fetch_reach(REACH_ID, args.start, args.end)
    df.to_csv(out / f"reach_{REACH_ID}_hydrocron.csv", index=False)

    plot_series(df, "wse", "WSE (m)", out / "WSE.png", rolling=args.rolling)
    plot_series(df, "width", "Width (m)", out / "WIDTH.png", rolling=args.rolling)
    plot_series(df, "slope", "Slope (m/m)", out / "SLOPE.png", rolling=args.rolling)

    print("Saved to:", out)
