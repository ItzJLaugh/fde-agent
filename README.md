# fde-agent

[![CI](https://github.com/ItzJLaugh/fde-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/ItzJLaugh/fde-agent/actions/workflows/ci.yml)

A terminal-based Forward Deployed Engineer agent that does the analysis an FDE does on a client engagement. It maps how the business actually runs, finds the bottlenecks, checks data quality across systems, and measures outcomes against a baseline. It's local-first: a small local model through Ollama, a human approval step before any decision with real consequences, and every step logged.

The engagement uses **Olist**, a Brazilian e-commerce marketplace. The question is where Olist's next revenue growth comes from. Candidates include seller acquisition (marketing funnel → closed deals), conversion and repeat purchase, order value, and the effect of delivery experience on reviews.

**Status:** early. The repo has a Python skeleton and CI; the agent is built in phases.

## Data

The raw data is not committed (`data/` is gitignored). Download both datasets from Kaggle (free account needed):

1. [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce): about 100k orders from 2016–2018
2. [Marketing Funnel by Olist](https://www.kaggle.com/datasets/olistbr/marketing-funnel-olist): seller leads (MQLs) and closed deals

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

The data is published by Olist under CC BY-NC-SA 4.0 (non-commercial, with attribution). See each Kaggle page for the details.

## Development

Needs [uv](https://docs.astral.sh/uv/). Python 3.12 is installed by uv if missing.

```bash
git clone https://github.com/ItzJLaugh/fde-agent.git
cd fde-agent
uv sync
uv run ruff check . && uv run ruff format --check . && uv run pyright && uv run pytest -q
```

CI runs the same four checks on every push and pull request to `main`.

## License

Code: [MIT](LICENSE). Data: see [Data](#data).
