from __future__ import annotations
import argparse
import json
import logging
import os
import pathlib
import subprocess
import sys
from collections import defaultdict
from typing import Dict, Optional
import importlib
load_dotenv = None
try:
    _dotenv = importlib.import_module("dotenv")
    load_dotenv = getattr(_dotenv, "load_dotenv", None)
except Exception:
    load_dotenv = None


def _resolve_token(cli_token: Optional[str]) -> Optional[str]:
    if cli_token:
        return cli_token
    token = os.getenv("VALIDATORS_APP_API_TOKEN") or os.getenv("API_TOKEN")
    if token:
        return token
    env_path = pathlib.Path(__file__).parent.parent / ".env"  # mapping_information/.env
    if env_path.exists():
        if load_dotenv is not None:
            load_dotenv(env_path, override=False)
            token = os.getenv("VALIDATORS_APP_API_TOKEN") or os.getenv("API_TOKEN")
            if token:
                return token
        else:
            try:
                for raw in env_path.read_text(encoding="utf-8").splitlines():
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
    return None


def get_pool_data(force_query: bool, api_token: Optional[str] = None) -> Optional[Dict[str, dict]]:
    """
    Loads Solana validator pool data from a local json file, optionally re-generating it
    by invoking the collectors script if --force-query is set or the file is missing.

    Returns a dictionary keyed by validator account with the full validator metadata as value.
    """
    logging.info("Getting Solana pool data..")
    script_dir = pathlib.Path(__file__).parent
    file = script_dir / "solana_pool_data.json"

    if not force_query and file.is_file():
        logging.info(
            "Pool data already exists locally. For querying anyway please run the script using the flag --force-query"
        )
        with open(file) as f:
            pool_data = json.load(f)
        return pool_data

    # Re-generate by calling the collector script
    addresses_dir = script_dir.parent / "addresses"
    collector = addresses_dir / "collect_solana_validators.py"
    if not collector.is_file():
        logging.error("collect_solana_validators.py not found; cannot fetch Solana data")
        return None

    env = os.environ.copy()
    token = _resolve_token(api_token)
    if token:
        env["VALIDATORS_APP_API_TOKEN"] = token

    cmd = [
        sys.executable,
        str(collector),
        "--format=json",
        "--copy-to-pool=true",
    ]
    logging.info("Fetching pool data from Validators.app via collector script..")
    try:
        # Also pass the token explicitly to the collector for clarity
        if token:
            cmd.extend(["--api-token", token])
        subprocess.run(cmd, check=True, env=env, cwd=str(addresses_dir))
    except subprocess.CalledProcessError as e:
        logging.error(f"Collector script failed with exit code {e.returncode}")
        return None

    if not file.is_file():
        logging.error("Expected solana_pool_data.json to be created but it was not found")
        return None

    with open(file) as f:
        pool_data = json.load(f)
    logging.info("Pool data saved/loaded locally.")
    return pool_data


def parse_pool_identifiers(pool_data: Dict[str, dict], mapping_info_dir: pathlib.Path) -> None:
    """
    Produces identifiers for Solana validators based on their display name and homepage.
    Duplicate names are ignored to avoid false matches.
    """
    logging.info("Parsing Solana identifiers..")
    identifiers: Dict[str, dict] = {}
    conflicts = set()

    for validator in pool_data.values():
        name = validator.get("name")
        homepage = validator.get("www_url")
        if not name:
            continue

        if name in conflicts:
            continue

        if name in identifiers:
            identifiers.pop(name)
            conflicts.add(name)
            continue

        identifiers[name] = {"name": name, "link": homepage}

    identifiers_dir = mapping_info_dir / "identifiers"
    identifiers_dir.mkdir(parents=True, exist_ok=True)
    with open(identifiers_dir / "solana.json", "w") as f:
        json.dump(identifiers, f, indent=4)
        logging.info("Solana identifiers saved locally.")


def parse_pool_clusters(pool_data: Dict[str, dict], mapping_info_dir: pathlib.Path) -> None:
    """
    Detects clusters of validators that share the same homepage and writes them to a json file.
    """
    logging.info("Detecting Solana clusters..")
    pools_per_homepage: Dict[str, set] = defaultdict(set)
    for account, validator in pool_data.items():
        pool_name = validator.get("name")
        homepage = validator.get("www_url")
        homepage = filter_homepage(homepage)
        if homepage and pool_name:
            pools_per_homepage[homepage].add((account, pool_name))

    clusters: Dict[str, dict] = {}
    for homepage, pools in pools_per_homepage.items():
        pool_names = [pool_name for _, pool_name in pools]

        if len(pool_names) > 1:
            cluster_name = determine_cluster_name(pool_names)
            clusters.update(
                {
                    account: {"cluster": cluster_name, "pool": pool_name, "source": homepage}
                    for account, pool_name in pools
                }
            )

    clusters_dir = mapping_info_dir / "clusters"
    clusters_dir.mkdir(parents=True, exist_ok=True)
    with open(clusters_dir / "solana.json", "w") as f:
        json.dump(clusters, f, indent=4)
        logging.info("Solana clusters detected and saved locally.")


def filter_homepage(homepage: Optional[str]) -> Optional[str]:
    """
    Filters out dummy homepages. Specifically, it ignores homepage entries that are empty,
    have an 'empty' name (e.g. 'n/a') or include a dummy keyword in their name (e.g. foo.com)
    """
    empty_names = [
        "n/a",
        "N/A",
        "NA",
        "https://",
        "http://",
        "-",
        "---",
        "coming",
        "TBD",
        "...",
        "In Process",
        "no webside",
        "Coming Soon",
    ]
    placeholder_keywords = ["foo.com", "example.com", "invalidurl"]
    if homepage:
        homepage = homepage.strip()
        if any(homepage == empty_name for empty_name in empty_names):
            return None
        if any(keyword in homepage.lower() for keyword in placeholder_keywords):
            return None
        return homepage
    return None


def determine_cluster_name(pool_names: list[str]) -> str:
    """
    Determines the name of a cluster of validators.
    Uses common prefix if available, otherwise the first alphabetical name,
    prioritizing names that don't start with a digit.
    """
    pool_names = [pool_name.title() for pool_name in pool_names]
    common_prefix = os.path.commonprefix(pool_names)
    if common_prefix:
        return common_prefix
    pool_names = sorted(pool_names, key=lambda x: (x[0].isdigit(), x))
    return pool_names[0]


if __name__ == "__main__":
    logging.basicConfig(
        format='[%(asctime)s] %(message)s', datefmt='%Y/%m/%d %I:%M:%S %p', level=logging.INFO
    )

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--force-query",
        action="store_true",
        help="Flag to specify whether to query for project data regardless if the relevant data already exist.",
    )
    parser.add_argument(
        "--api-token",
        default=None,
        help="Validators.app API token. If not provided, environment will be used.",
    )
    args = parser.parse_args()

    mapping_info_dir = pathlib.Path(__file__).parent.parent

    pool_data = get_pool_data(force_query=args.force_query, api_token=args.api_token)
    if pool_data:
        parse_pool_identifiers(pool_data, mapping_info_dir)
        parse_pool_clusters(pool_data, mapping_info_dir)

