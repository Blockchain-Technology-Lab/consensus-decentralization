# Data collection

Currently, the data for the analysis of the different ledgers is collected through 
[Google BigQuery](https://console.cloud.google.com/bigquery) .

Note that when saving results from BigQuery you should select the option "JSONL (newline delimited)".

## Sample data & queries

Sample data for all blockchains can be found [here](https://uoe-my.sharepoint.com/:f:/g/personal/s2125265_ed_ac_uk/Eg0L2n9P-txOtibKu9CXfloBt6_D-3D1AEsS2evtXIatVA?e=qHhFp4).
Alternatively, one can retrieve the data directly from BigQuery using the queries below.

### Bitcoin

```
SELECT block_number as number, block_timestamp as timestamp, coinbase_param as identifiers, `bigquery-public-data.crypto_bitcoin.transactions`.outputs
FROM `bigquery-public-data.crypto_bitcoin.transactions`
JOIN `bigquery-public-data.crypto_bitcoin.blocks` ON `bigquery-public-data.crypto_bitcoin.transactions`.block_number = `bigquery-public-data.crypto_bitcoin.blocks`.number
WHERE is_coinbase is TRUE
AND timestamp > '2017-12-31'
```

### Bitcoin Cash

```
SELECT block_number as number, block_timestamp as timestamp, coinbase_param as identifiers, `bigquery-public-data.crypto_bitcoin_cash.transactions`.outputs
FROM `bigquery-public-data.crypto_bitcoin_cash.transactions`
JOIN `bigquery-public-data.crypto_bitcoin_cash.blocks` ON `bigquery-public-data.crypto_bitcoin_cash.transactions`.block_number = `bigquery-public-data.crypto_bitcoin_cash.blocks`.number
WHERE is_coinbase is TRUE
AND timestamp > '2018-12-31'
```

### Cardano

```
SELECT `iog-data-analytics.cardano_mainnet.block`.slot_no as number, `iog-data-analytics.cardano_mainnet.pool_offline_data`.ticker_name as identifiers, `iog-data-analytics.cardano_mainnet.block`.block_time as timestamp,`iog-data-analytics.cardano_mainnet.block`.pool_hash as reward_addresses
FROM `iog-data-analytics.cardano_mainnet.block`
LEFT JOIN `iog-data-analytics.cardano_mainnet.pool_offline_data` ON `iog-data-analytics.cardano_mainnet.block`.pool_hash = `iog-data-analytics.cardano_mainnet.pool_offline_data`.pool_hash
WHERE `iog-data-analytics.cardano_mainnet.block`.block_time > '2020-12-31'
```

### Dogecoin

```
SELECT block_number as number, block_timestamp as timestamp, coinbase_param as identifiers, `bigquery-public-data.crypto_dogecoin.transactions`.outputs
FROM `bigquery-public-data.crypto_dogecoin.transactions`
JOIN `bigquery-public-data.crypto_dogecoin.blocks` ON `bigquery-public-data.crypto_dogecoin.transactions`.block_number = `bigquery-public-data.crypto_dogecoin.blocks`.number
WHERE is_coinbase is TRUE
AND timestamp > '2019-12-31'
```

### Ethereum

```
SELECT number, timestamp, miner as reward_addresses, extra_data as identifiers
FROM `bigquery-public-data.crypto_ethereum.blocks`
WHERE timestamp > '2018-12-31'
```

### Litecoin

```
SELECT block_number as number, block_timestamp as timestamp, coinbase_param as identifiers, `bigquery-public-data.crypto_litecoin.transactions`.outputs
FROM `bigquery-public-data.crypto_litecoin.transactions`
JOIN `bigquery-public-data.crypto_litecoin.blocks` ON `bigquery-public-data.crypto_litecoin.transactions`.block_number = `bigquery-public-data.crypto_litecoin.blocks`.number
WHERE is_coinbase is TRUE
AND timestamp > '2018-12-31'
```

### Tezos

```
SELECT level as number, timestamp, baker as reward_addresses
FROM `public-data-finance.crypto_tezos.blocks`
WHERE timestamp > '2020-12-31'
```

### Zcash

```
SELECT block_number as number, block_timestamp as timestamp, coinbase_param as identifiers, `bigquery-public-data.crypto_zcash.transactions`.outputs
FROM `bigquery-public-data.crypto_zcash.transactions`
JOIN `bigquery-public-data.crypto_zcash.blocks` ON `bigquery-public-data.crypto_zcash.transactions`.block_number = `bigquery-public-data.crypto_zcash.blocks`.number
WHERE is_coinbase is TRUE
AND timestamp > '2018-12-31'
```

## Automating the data collection process

Instead of executing each of these queries separately on the BigQuery console and saving the results manually, it is
also possible to automate the process using
a [script](https://github.com/Blockchain-Technology-Lab/pooling-analysis/blob/main/src/collect_data.py) and collect all
relevant data in one go. Executing this script will run all queries
in [this file](https://github.com/Blockchain-Technology-Lab/pooling-analysis/blob/main/queries.yaml), so you can also
control which queries are run by adding them to or removing them from the file (or turning them into comments by 
adding a `#` in front of each relevant line).

IMPORTANT: the script uses service account credentials for authentication, therefore before running it, you need to
generate the relevant credentials from Google, as described 
[here](https://developers.google.com/workspace/guides/create-credentials#service-account) and save your key in the
root directory of the project under the name 'google-service-account-key.json'. There is a
[sample file](https://github.com/Blockchain-Technology-Lab/pooling-analysis/blob/main/google-service-account-key-SAMPLE.json) 
that you can consult, which shows what your credentials are supposed to look like (but note that this is for
informational purposes only, this file is not used in the code).

Once you have set up the credentials, you can just run the following command from the `src` directory to retrieve data
for all supported blockchains:

`python collect_data.py`

