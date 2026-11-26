from pathlib import Path

import pandas as pd

# src/fde_agent/data.py → parents[0]=fde_agent, [1]=src, [2]=repo root
DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"


def load_table(name: str) -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / f"olist_{name}_dataset.csv")
