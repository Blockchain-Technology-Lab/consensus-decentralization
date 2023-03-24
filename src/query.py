"""
    This script can be used to run queries on BigQuery for any number of blockchains, and save the results in the input
    directory of the project.
    The relevant queries must be stored in a file named 'queries.yaml' in the root directory of the project.

    Attention! Before running this script, you need to generate service account credentials from Google, as described
    here (https://developers.google.com/workspace/guides/create-credentials#service-account) and save your key in the
    root directory of the project under the name 'google-service-account-key.json'
"""
import google.cloud.bigquery as bq
import json
from yaml import safe_load

from helpers.helper import ROOT_DIR, INPUT_DIR

with open(ROOT_DIR / "queries.yaml") as f:
    queries = safe_load(f)

client = bq.Client.from_service_account_json(json_credentials_path=ROOT_DIR / "google-service-account-key.json")
for ledger in queries.keys():
    print(f"Querying {ledger}...")
    QUERY = (queries[ledger])
    query_job = client.query(QUERY)
    try:
        rows = query_job.result()
    except Exception as e:
        print(f'{ledger} query failed, please make sure it is properly defined.')
        print(f'The following exception was raised: {repr(e)}')
        continue

    result_json = [dict(row) for row in rows]

    filename = f'{ledger}_raw_data.json'
    with open(INPUT_DIR / filename, 'w') as f:
        json.dump(result_json, f, default=str)
