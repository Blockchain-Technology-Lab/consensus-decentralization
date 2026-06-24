#!/usr/bin/env python3
"""
Fetch Solana validators from Validators.app API and save to file or stdout.

Authentication: requires an API token from Validators.app.
- Provide via --api-token flag, or
- Environment variable VALIDATORS_APP_API_TOKEN, or
- Environment variable API_TOKEN

Docs: https://www.validators.app/api-documentation?locale=en&network=mainnet#validators-list
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Dict, Optional, Tuple, Mapping, Any
import importlib
load_dotenv = None
try:
    _dotenv = importlib.import_module("dotenv")
    load_dotenv = getattr(_dotenv, "load_dotenv", None)
except Exception:
    load_dotenv = None

VALID_NETWORKS = ("mainnet", "testnet", "pythnet")
VALID_ORDERS = ("score", "name", "stake")
VALID_FORMATS = ("json", "csv")

BASE_URL = "https://www.validators.app/api/v1/validators"

# Default output: write next to this script as solana.json
SCRIPT_DIR = os.path.dirname(__file__)
DEFAULT_OUTPUT_PATH = os.path.join(SCRIPT_DIR, "solana.json")


def parse_bool(value: str) -> bool:
    lowered = value.strip().lower()
    if lowered in {"1", "true", "t", "yes", "y"}:
        return True
    if lowered in {"0", "false", "f", "no", "n"}:
        return False
    raise argparse.ArgumentTypeError(f"Invalid boolean value: {value}")


def resolve_token(cli_token: Optional[str]) -> str:
    if cli_token:
        return cli_token
    env_token = os.getenv("VALIDATORS_APP_API_TOKEN") or os.getenv("API_TOKEN")
    if env_token:
        return env_token
    # Try mapping_information/.env (parent of addresses dir)
    mapping_dir = os.path.dirname(SCRIPT_DIR)
    env_path = os.path.join(mapping_dir, ".env")
    if os.path.exists(env_path):
        if load_dotenv is not None:
            load_dotenv(env_path, override=False)
            env_token = os.getenv("VALIDATORS_APP_API_TOKEN") or os.getenv("API_TOKEN")
            if env_token:
                return env_token
        else:
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for raw in f:
                        line = raw.strip()
                        if not line or line.startswith("#") or "=" not in line:
                            continue
                        k, v = line.split("=", 1)
                        key = k.strip()
                        val = v.strip()
                        if key in ("VALIDATORS_APP_API_TOKEN", "API_TOKEN") and val:
                            return val
            except Exception:
                pass
    raise SystemExit(
        "Missing API token. Use --api-token or set VALIDATORS_APP_API_TOKEN or API_TOKEN."
    )


def build_request_url(
    network: str,
    output_format: str,
    order: Optional[str],
    limit: Optional[int],
    page: Optional[int],
    active_only: Optional[bool],
    query: Optional[str],
) -> str:
    ext = "csv" if output_format == "csv" else "json"
    path = f"{BASE_URL}/{network}.{ext}"
    params: Dict[str, str] = {}

    if order:
        params["order"] = order
    if limit is not None:
        params["limit"] = str(limit)
    if page is not None:
        params["page"] = str(page)
    if active_only is not None:
        params["active_only"] = "true" if active_only else "false"
    if query:
        params["q"] = query

    if params:
        return f"{path}?{urllib.parse.urlencode(params)}"
    return path


def http_get_with_retry(url: str, headers: Dict[str, str], max_retries: int = 3, timeout: int = 30) -> Tuple[int, Dict[str, str], bytes]:
    last_err: Optional[Exception] = None
    for attempt in range(1, max_retries + 1):
        req = urllib.request.Request(url, headers=headers, method="GET")
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                status = resp.getcode()
                resp_headers = {k: v for k, v in resp.getheaders()}
                body = resp.read()
                if status == 429:
                    # Respect rate limit reset if provided
                    reset_seconds = int(resp_headers.get("RateLimit-Reset", "0") or 0)
                    sleep_seconds = reset_seconds if reset_seconds > 0 else min(60, 2 ** attempt)
                    if attempt < max_retries:
                        time.sleep(sleep_seconds)
                        continue
                if 500 <= status < 600 and attempt < max_retries:
                    time.sleep(min(60, 2 ** attempt))
                    continue
                return status, resp_headers, body
        except urllib.error.HTTPError as e:
            status = e.code
            resp_headers = {k: v for k, v in e.headers.items()} if e.headers else {}
            body = e.read() if hasattr(e, "read") else b""
            if status == 429 and attempt < max_retries:
                reset_seconds = int(resp_headers.get("RateLimit-Reset", "0") or 0)
                sleep_seconds = reset_seconds if reset_seconds > 0 else min(60, 2 ** attempt)
                time.sleep(sleep_seconds)
                continue
            if 500 <= status < 600 and attempt < max_retries:
                time.sleep(min(60, 2 ** attempt))
                continue
            return status, resp_headers, body
        except Exception as e:  # network error
            last_err = e
            if attempt < max_retries:
                time.sleep(min(60, 2 ** attempt))
                continue
            raise
    if last_err:
        raise last_err
    raise RuntimeError("Request failed and no exception captured")


def write_output(data_bytes: bytes, output_path: str) -> None:
    if output_path == "-":
        # Print to stdout
        sys.stdout.buffer.write(data_bytes)
        if not data_bytes.endswith(b"\n"):
            sys.stdout.buffer.write(b"\n")
        return
    # Write to file (binary to support CSV)
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(data_bytes)


def pretty_print_json_if_stdout(data_bytes: bytes, output_path: str) -> Optional[bytes]:
    if output_path != "-":
        return None
    # If writing to stdout and it's JSON, pretty-print
    try:
        parsed = json.loads(data_bytes.decode("utf-8"))
    except Exception:
        return None
    pretty = json.dumps(parsed, indent=2, ensure_ascii=False).encode("utf-8")
    return pretty


def _parse_validators_array(data_bytes: bytes) -> list[dict]:
    """Parse the validators JSON array from API response with validation."""
    parsed = json.loads(data_bytes.decode("utf-8"))
    if not isinstance(parsed, list):
        raise ValueError("Expected JSON array from API response")
    return [item for item in parsed if isinstance(item, dict)]


def _emit_single_line_json(mapping: Mapping[str, Any]) -> bytes:
    """Emit a JSON object where each top-level key-value pair occupies one line.

    Values are compact-encoded (separators="," and ":") to keep each entry on a single line.
    """
    lines = ["{"]
    total_items = len(mapping)
    if total_items:
        index = 0
        for k, v in mapping.items():
            index += 1
            key_json = json.dumps(k, ensure_ascii=False)
            value_json = json.dumps(v, separators=(",", ":"), ensure_ascii=False)
            trailing_comma = "," if index < total_items else ""
            lines.append(f"\t{key_json}: {value_json}{trailing_comma}")
    lines.append("}")
    return "\n".join(lines).encode("utf-8")


def _build_minimal_address_mapping(
    validators: list[dict], include_vote_accounts: bool, source: str
) -> Dict[str, Dict[str, str]]:
    """Construct address -> {name, source} mapping from validators list."""
    address_map: Dict[str, Dict[str, str]] = {}
    for item in validators:
        name = item.get("name")
        if not name:
            continue
        account = item.get("account")
        if isinstance(account, str) and account:
            address_map[account] = {"name": name, "source": source}
        if include_vote_accounts:
            vote_account = item.get("vote_account")
            if isinstance(vote_account, str) and vote_account:
                address_map[vote_account] = {"name": name, "source": source}
    return address_map


def _build_account_to_full_metadata(validators: list[dict]) -> Dict[str, dict]:
    """Construct account -> full validator object mapping from validators list."""
    account_map: Dict[str, dict] = {}
    for item in validators:
        account = item.get("account")
        if isinstance(account, str) and account:
            account_map[account] = item
    return account_map


def transform_array_to_minimal_address_map(
    data_bytes: bytes,
    include_vote_accounts: bool = False,
    source: str = "https://www.validators.app",
) -> bytes:
    """Transform validator array into a minimal address->owner mapping.

    Output example:
    {
    "AccountPubkey": {"name":"ValidatorName","source":"https://www.validators.app"},
    "VotePubkey": {"name":"ValidatorName","source":"https://www.validators.app"}
    }
    Each top-level key-value is emitted on a single line.
    """
    validators = _parse_validators_array(data_bytes)
    address_map = _build_minimal_address_mapping(
        validators, include_vote_accounts=include_vote_accounts, source=source
    )
    return _emit_single_line_json(address_map)


def transform_array_to_account_map(data_bytes: bytes) -> bytes:
    """Transform an array of validator objects into a dict keyed by 'account'.

    The value for each key is the original validator object unchanged.
    Output JSON has one top-level key-value per line; each value is a
    compact single-line object for readability and grepability.
    """
    validators = _parse_validators_array(data_bytes)
    account_map = _build_account_to_full_metadata(validators)
    return _emit_single_line_json(account_map)


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Fetch Solana validators list from Validators.app")
    parser.add_argument("--network", choices=VALID_NETWORKS, default="mainnet", help="Network to query")
    parser.add_argument("--order", choices=VALID_ORDERS, default=None, help="Sort order: score, name, or stake")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of validators (max 9999)")
    parser.add_argument("--page", type=int, default=None, help="Page number for paginated results")
    parser.add_argument("--active-only", type=parse_bool, default=True, help="Exclude validators delinquent >24h (true/false)")
    parser.add_argument("--query", "-q", dest="query", default=None, help="Filter by name, account, or DC key")
    parser.add_argument("--api-token", dest="api_token", default=None, help="Validators.app API token")
    parser.add_argument(
        "--format",
        dest="output_format",
        choices=VALID_FORMATS,
        default="json",
        help="Response format (json or csv)",
    )
    parser.add_argument(
        "--output",
        "-o",
        dest="output",
        default=DEFAULT_OUTPUT_PATH,
        help="Output path or '-' for stdout (default: solana.json next to this script)",
    )
    parser.add_argument(
        "--copy-to-pool",
        type=parse_bool,
        default=True,
        help=(
            "If true and format=json, also write to mapping_information/solana_preprocessing/solana_pool_data.json"
        ),
    )
    parser.add_argument(
        "--include-vote",
        type=parse_bool,
        default=False,
        help=(
            "If true, include vote accounts in addresses mapping (name/source)."
        ),
    )

    args = parser.parse_args(argv)

    token = resolve_token(args.api_token)
    url = build_request_url(
        network=args.network,
        output_format=args.output_format,
        order=args.order,
        limit=args.limit,
        page=args.page,
        active_only=args.active_only,
        query=args.query,
    )

    headers = {
        "Token": token,
        # Content-Type not strictly required for GET, but harmless
        "Content-Type": "application/json",
        "User-Agent": "consensus-decentralization/collect-solana-validators (Python)",
    }

    status, resp_headers, body = http_get_with_retry(url, headers=headers)

    if status != 200:
        # Try to display error message if JSON body present
        msg = body.decode("utf-8", errors="replace")
        raise SystemExit(f"Request failed with HTTP {status}: {msg}")

    # Write addresses mapping (minimal {name, source}) and pretty print with one entry per line
    if args.output_format == "json":
        try:
            transformed = transform_array_to_minimal_address_map(
                body,
                include_vote_accounts=args.include_vote,
                source="https://www.validators.app",
            )
        except Exception as exc:
            msg = f"Failed to transform API response to account-keyed dict: {exc}"
            logging.error(msg)
            raise SystemExit(msg)
        write_output(transformed, args.output)
        logging.info(f"Transformed API response to account-keyed dict and saved to {args.output}")
    else:
        # CSV or other: write as-is
        pretty = pretty_print_json_if_stdout(body, args.output)
        write_output(pretty if pretty is not None else body, args.output)
        logging.info(f"Wrote API response to {args.output}")

    # Optionally copy full metadata map to solana_pool_data.json (JSON only)
    if args.copy_to_pool:
        if args.output_format != "json":
            raise SystemExit(
                "--copy-to-pool is only supported when --format=json"
            )
        # mapping_information/solana_preprocessing/solana_pool_data.json
        mapping_dir = os.path.dirname(SCRIPT_DIR)  # mapping_information
        pool_dir = os.path.join(mapping_dir, "solana_preprocessing")
        os.makedirs(pool_dir, exist_ok=True)
        pool_path = os.path.join(pool_dir, "solana_pool_data.json")
        # Ensure we copy the full metadata map (not minimal address map)
        try:
            transformed_for_pool = transform_array_to_account_map(body)
        except Exception as exc:
            raise SystemExit(f"Failed to transform for --copy-to-pool: {exc}")
        write_output(transformed_for_pool, pool_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


