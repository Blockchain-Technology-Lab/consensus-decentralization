# Data collection

Currently, the data for the analysis of the different ledgers is collected through 
[Google BigQuery](https://console.cloud.google.com/bigquery) .

Note that when saving results from BigQuery you should select the option "JSONL (newline delimited)".

## Sample data

### Bitcoin

Sample raw Bitcoin data are available
[here](https://drive.google.com/file/d/12sd6xn8aZE5yBrUFoxE6vVPFIuE_Sw4F/view?usp=sharing).

They can be retrieved using [Google BigQuery](https://console.cloud.google.com/bigquery) with the following query:

```
SELECT block_number as number, block_timestamp as timestamp, coinbase_param, `bigquery-public-data.crypto_bitcoin.transactions`.outputs
FROM `bigquery-public-data.crypto_bitcoin.transactions`
JOIN `bigquery-public-data.crypto_bitcoin.blocks` ON `bigquery-public-data.crypto_bitcoin.transactions`.block_number = `bigquery-public-data.crypto_bitcoin.blocks`.number
WHERE is_coinbase is TRUE
AND timestamp > '2017-12-31'
```

### Bitcoin Cash

Sample raw Bitcoin Cash data are available
[here](https://drive.google.com/file/d/1560i6dbicv5h8bqcYMIPNKZTMgT44qNE/view?usp=sharing).

They can be retrieved using [Google BigQuery](https://console.cloud.google.com/bigquery) with the following query:

```
SELECT block_number as number, block_timestamp as timestamp, coinbase_param, `bigquery-public-data.crypto_bitcoin_cash.transactions`.outputs
FROM `bigquery-public-data.crypto_bitcoin_cash.transactions`
JOIN `bigquery-public-data.crypto_bitcoin_cash.blocks` ON `bigquery-public-data.crypto_bitcoin_cash.transactions`.block_number = `bigquery-public-data.crypto_bitcoin_cash.blocks`.number
WHERE is_coinbase is TRUE
AND timestamp > '2018-12-31'
```

### Cardano

Sample raw Cardano data are available
[here](https://drive.google.com/file/d/1qetBLr7sHccnoTbVTD_t_bCOeWfIjH3D/view?usp=sharing).

They can be retrieved using [Google BigQuery](https://console.cloud.google.com/bigquery) with the following query:

```
SELECT `iog-data-analytics.cardano_mainnet.block`.slot_no as number, `iog-data-analytics.cardano_mainnet.pool_offline_data`.ticker_name as coinbase_param, `iog-data-analytics.cardano_mainnet.block`.block_time as timestamp, `iog-data-analytics.cardano_mainnet.block`.pool_hash
FROM `iog-data-analytics.cardano_mainnet.block` 
LEFT JOIN `iog-data-analytics.cardano_mainnet.pool_offline_data` ON `iog-data-analytics.cardano_mainnet.block`.pool_hash = `iog-data-analytics.cardano_mainnet.pool_offline_data`.pool_hash
WHERE `iog-data-analytics.cardano_mainnet.block`.block_time > '2020-12-31'
```

### Dash

Sample raw Dash data are available
[here](https://drive.google.com/file/d/1DkjAZ7hq45zIan278NA6KVv3B45OG9GU/view?usp=sharing).

They can be retrieved using [Google BigQuery](https://console.cloud.google.com/bigquery) with the following query:

```
SELECT block_number as number, block_timestamp as timestamp, coinbase_param, `bigquery-public-data.crypto_dash.transactions`.outputs
FROM `bigquery-public-data.crypto_dash.transactions`
JOIN `bigquery-public-data.crypto_dash.blocks` ON `bigquery-public-data.crypto_dash.transactions`.block_number = `bigquery-public-data.crypto_dash.blocks`.number
WHERE is_coinbase is TRUE
AND timestamp > '2018-12-31'
```

### Dogecoin

Sample raw Dogecoin data are available
[here](https://drive.google.com/file/d/1eVHop4ciT0f8veLiy2nEd61AeC1iyd-1/view?usp=sharing).

They can be retrieved using [Google BigQuery](https://console.cloud.google.com/bigquery) with the following query:

```
SELECT block_number as number, block_timestamp as timestamp, coinbase_param, `bigquery-public-data.crypto_dogecoin.transactions`.outputs
FROM `bigquery-public-data.crypto_dogecoin.transactions`
JOIN `bigquery-public-data.crypto_dogecoin.blocks` ON `bigquery-public-data.crypto_dogecoin.transactions`.block_number = `bigquery-public-data.crypto_dogecoin.blocks`.number
WHERE is_coinbase is TRUE
AND timestamp > '2019-12-31'
```

### Ethereum

Sample raw Ethereum data are available
[here](https://drive.google.com/file/d/1i9veHVB8nuitXMXWxk3oTOXY6rI_Ex8a/view?usp=sharing).

They can be retrieved using [Google BigQuery](https://console.cloud.google.com/bigquery) with the following query:

```
SELECT number, timestamp, miner as coinbase_addresses, extra_data as coinbase_param
FROM `bigquery-public-data.crypto_ethereum.blocks`
WHERE timestamp > '2018-12-31'
```

### Litecoin

Sample raw Litecoin data are available
[here](https://drive.google.com/file/d/1XR8t0NZ9IfuBBzCGyBw8c_nFyFjSsxd7/view?usp=sharing).

They can be retrieved using [Google BigQuery](https://console.cloud.google.com/bigquery) with the following query:

```
SELECT block_number as number, block_timestamp as timestamp, coinbase_param, `bigquery-public-data.crypto_litecoin.transactions`.outputs
FROM `bigquery-public-data.crypto_litecoin.transactions`
JOIN `bigquery-public-data.crypto_litecoin.blocks` ON `bigquery-public-data.crypto_litecoin.transactions`.block_number = `bigquery-public-data.crypto_litecoin.blocks`.number
WHERE is_coinbase is TRUE
AND timestamp > '2018-12-31'
```

### Tezos

Sample raw Tezos data are available
[here](https://drive.google.com/file/d/1Jn4A2hxanwniiexzHySFa6CFU8aS03mB/view?usp=sharing).

They can be retrieved using [Google BigQuery](https://console.cloud.google.com/bigquery) with the following query:

```
SELECT level as number, timestamp, baker as coinbase_addresses
FROM `public-data-finance.crypto_tezos.blocks`
WHERE timestamp > '2020-12-31'
```

### Zcash

Sample raw Zcash data are available
[here](https://drive.google.com/file/d/1WEkUAaIaRsGXuemAZj_DbNIlhkWtOn5A/view?usp=sharing).

They can be retrieved using [Google BigQuery](https://console.cloud.google.com/bigquery) with the following query:

```
SELECT block_number as number, block_timestamp as timestamp, coinbase_param, `bigquery-public-data.crypto_zcash.transactions`.outputs
FROM `bigquery-public-data.crypto_zcash.transactions`
JOIN `bigquery-public-data.crypto_zcash.blocks` ON `bigquery-public-data.crypto_zcash.transactions`.block_number = `bigquery-public-data.crypto_zcash.blocks`.number
WHERE is_coinbase is TRUE
AND timestamp > '2018-12-31'
```
