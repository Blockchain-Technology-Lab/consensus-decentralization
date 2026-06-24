## Solana Validators Collector (Validators.app)

This script fetches the Solana validators list from Validators.app and writes either:
- a minimal address → {name, source} JSON map (default JSON mode), or
- the raw CSV response (CSV mode).

Reference: [Validators.app API – Validators List](https://www.validators.app/api-documentation?locale=en&network=mainnet#validators-list)

### Requirements

- Python 3.8+
- An API token from Validators.app

Provide the token in one of the following ways:
- Environment variable `VALIDATORS_APP_API_TOKEN`, or
- Environment variable `API_TOKEN`, or
- `--api-token` flag

The token is sent as the `Token` header (header names are case-insensitive).

### Install

- No external dependencies are required (uses stdlib `urllib`).
- Optional: if a `.env` file is used, the script will look for `mapping_information/.env`. If `python-dotenv` is installed, it will be used; otherwise a simple built-in parser loads `VALIDATORS_APP_API_TOKEN` / `API_TOKEN` from that file.

### Usage

Basic examples (aligned with the script’s behavior):

```bash
# JSON (default transform): writes minimal {address: {name, source}} map
VALIDATORS_APP_API_TOKEN=your_token \
python3 mapping_information/addresses/collect_solana_validators.py \
  --network mainnet \
  --order stake \
  --active-only true \
  --format json \
  --output -

# Save JSON to the default path next to the script
python3 mapping_information/addresses/collect_solana_validators.py \
  --network mainnet --order stake --active-only true --format json
# Default output path: mapping_information/addresses/solana.json

# CSV output (raw API CSV). Note: --copy-to-pool must be false for CSV
python3 mapping_information/addresses/collect_solana_validators.py \
  --network mainnet --order score --active-only true --format csv \
  --copy-to-pool false \
  --output data/solana_validators_mainnet.csv

# Filter (q=) by name/account/DC key, paginate and limit
python3 mapping_information/addresses/collect_solana_validators.py \
  --network mainnet --order name --limit 100 --page 1 --query helius \
  --output -
```

### Arguments

- `--network`: one of `mainnet`, `testnet`, `pythnet` (default: `mainnet`)
- `--order`: one of `score`, `name`, `stake` (optional)
- `--limit`: integer (max 9999 per API docs, optional)
- `--page`: page number for pagination (optional)
- `--active-only`: `true` or `false` (default: `true`)
- `--query` / `-q`: filter string applied to name, account and DC key (optional)
- `--format`: `json` or `csv` (default: `json`)
- `--include-vote`: `true` or `false` (default: `false`). When `true`, vote accounts are also included in the minimal address map.
- `--copy-to-pool`: `true` or `false` (default: `true`, JSON-only). When `true` and `--format=json`, also writes the full account→metadata map to `mapping_information/solana_preprocessing/solana_pool_data.json`.
- `--api-token`: API token if not using env var
- `--output` / `-o`: path or `-` for stdout. Default: `mapping_information/addresses/solana.json` (next to the script) in JSON mode if not set.

### Notes

- The API rate limit is enforced by Validators.app. On HTTP 429 the script backs off using the `RateLimit-Reset` header when present. See API docs for limits.
- JSON output from this script is a transformed minimal address map with one entry per line for readability.
- For CSV output, the raw response is written as-is. `--copy-to-pool` must be `false` when `--format=csv`.

### Equivalent curl (from docs)

```bash
curl --request GET \
  --url 'https://www.validators.app/api/v1/validators/mainnet.json?order=stake&active_only=true' \
  --header 'content-type: application/json' \
  --header "token: $VALIDATORS_APP_API_TOKEN"   # header names are case-insensitive
```

See API docs for more endpoints and parameters: [Validators.app API docs](https://www.validators.app/api-documentation?locale=en&network=mainnet#validators-list).


