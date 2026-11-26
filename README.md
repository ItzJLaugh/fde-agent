# Olist E-commerce Revenue Growth: A Forward Deployed Engineering Project

[![CI](https://github.com/ItzJLaugh/olist-revenue-growth-fde/actions/workflows/ci.yml/badge.svg)](https://github.com/ItzJLaugh/olist-revenue-growth-fde/actions/workflows/ci.yml)

A Forward Deployed Engineer (FDE) engagement run end to end on real marketplace data. I treat **Olist**, a Brazilian e-commerce marketplace, as the client. The work follows the FDE loop: frame the business problem, set a measured baseline, audit data quality, form hypotheses, test them with statistical and machine learning methods, size each opportunity in revenue (R$), and recommend interventions with costs, risks, and a pilot (A/B test) design.

**Business question:** Where does Olist's next revenue growth come from?

## Results so far

| Metric (delivered orders, 2016–2018) | Value | Evidence |
|---|---:|---|
| Total revenue (item price + freight) | R$ 15,419,773.75 | [E2](docs/evidence/E2-baseline.md) |
| Delivered orders | 96,478 | [E2](docs/evidence/E2-baseline.md) |
| Average order value (AOV) | R$ 159.83 | [E2](docs/evidence/E2-baseline.md) |
| Orders not delivered | 2,963 (2.98%) | [E1](docs/evidence/E1-order-status.md) |

The full engagement log has the revenue levers, the data quality log, and the hypotheses with
kill criteria, solution costing, and pilot designs: **[docs/notes.md](docs/notes.md)**.

## Approach

| Phase | What it covers | Status |
|---|---|---|
| 1. Problem framing | Revenue levers: seller acquisition, repeat purchase, order value, customer retention | ✅ Done |
| 2. Data audit | Entity relationships across 11 tables, data quality log (identity keys, encoding, revenue definition) | ✅ Done |
| 3. Baseline KPIs | Revenue, delivered orders, AOV; tested, reproducible pipeline | ✅ Done |
| 4. Hypothesis testing | Failed delivery → customer churn; cohort retention; confidence intervals | 🟡 In progress |
| 5. Modeling | Delivery delay vs review score threshold (scikit-learn), logistic regression with confounders, revenue concentration (Lorenz curve / Gini) | ⬜ Planned |
| 6. Recommendations | Interventions ranked by net value, plus A/B test pilot design and success metrics | ⬜ Planned |

## How the work is organized

- **Every number is reproducible.** One command regenerates all evidence files
  (`uv run python -m fde_agent.evidence`), and each finding in the notes links to its evidence.
- **Hypotheses have kill criteria.** Each one states what result would disprove it before any
  testing.
- **Solutions are ranked by net value** (gain minus cost) and checked for side effects across
  revenue levers.
- **Engineering standards:** Python 3.12 with strict type checking (pyright), linting and
  formatting (ruff), and unit tests (pytest). A GitHub Actions CI pipeline runs on every push,
  and branch protection guards `main`.

## Tech stack

Python · pandas · scikit-learn *(planned)* · matplotlib *(planned)* · SciPy *(planned)* ·
uv · pytest · pyright · ruff · GitHub Actions

## Repository layout

```
docs/
├── notes.md              engagement log: levers, data quality, baseline, hypotheses
└── evidence/             generated evidence files (E1, E2, …) behind every number
src/fde_agent/
├── data.py               typed CSV loader for the Olist tables
├── baseline.py           baseline KPIs (revenue, orders, AOV)
└── evidence.py           regenerates docs/evidence/
tests/                    unit tests on small hand-made DataFrames (no raw data needed in CI)
```

## Data

The raw data is not committed (`data/` is gitignored). Download both public datasets from
Kaggle (free account needed):

1. [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce): about 100k orders, 2016–2018
2. [Marketing Funnel by Olist](https://www.kaggle.com/datasets/olistbr/marketing-funnel-olist): 8,000 seller leads (MQLs) and 842 closed deals

Unzip all the CSVs into one folder:

```
data/raw/
├── olist_orders_dataset.csv
├── olist_order_items_dataset.csv
├── olist_order_payments_dataset.csv
├── olist_order_reviews_dataset.csv
├── olist_customers_dataset.csv
├── olist_sellers_dataset.csv
├── olist_products_dataset.csv
├── olist_geolocation_dataset.csv
├── product_category_name_translation.csv
├── olist_marketing_qualified_leads_dataset.csv
└── olist_closed_deals_dataset.csv
```

The data is published by Olist under CC BY-NC-SA 4.0 (non-commercial, with attribution). See each Kaggle page for details. This is an independent portfolio project, not affiliated with Olist.

## Reproduce

Needs [uv](https://docs.astral.sh/uv/). uv installs Python 3.12 if it's missing.

```bash
git clone https://github.com/ItzJLaugh/olist-revenue-growth-fde.git
cd olist-revenue-growth-fde
uv sync
uv run python -m fde_agent.evidence      # regenerate evidence (needs data/raw/)
uv run ruff check . && uv run ruff format --check . && uv run pyright && uv run pytest -q
```

## License

Code: [MIT](LICENSE). Data: see [Data](#data).
