# Parsers

The parser obtains raw data from a full node (see [Data Collection](data.md) page on how to obtain the required data).
It parses the data into a list of entries (dictionaries), each entry corresponding to a block.

The input file should be placed in the `raw_block_data/` directory and named as `<project_name>_raw_data.json`.

The parsed data is structured as follows:

```
[
    {
        "number": "<block's number>",
        "timestamp": "<block's timestamp of the form: yyyy-mm-dd hh:mm:ss UTC>",
        "reward_addresses": "<address1>,<address2>"
        "identifiers": "<identifiers>"
    }
]
```

`number` and `timestamp` are consistent among different blockchains.
`reward_addresses` and `identifiers` vary, depending on each ledger.

Specifically, `reward_addresses` corresponds to:

- `Bitcoin`, `Bitcoin Cash`, `Dogecoin`, `Litecoin`, `Zcash`: a string of comma-separated addresses which appear in the block's coinbase transaction with non-negative value (i.e., which are given part of the block's fees)
- `Ethereum`: the block's `miner` field
- `Cardano`: the hash of the pool that created the data, if defined, otherwise the empty string
- `Tezos`: the block's `baker` field

The field `identifiers` corresponds to:

- `Bitcoin`, `Bitcoin Cash`, `Dogecoin`, `Litecoin`, `Zcash`: the field `coinbase_param` of the block's coinbase transaction
- `Ethereum`: the block's `extra_data` field
- `Cardano`: the ticker name of the pool that created the block, if defined, otherwise an empty string
- `Tezos`: there is no such field

If using BigQuery, the queries for Bitcoin, Bitcoin Cash, Dogecoin, Litecoin, Zcash (see [Data Collection](data.md))
return data that are parsed with the `default_parser` module in `parsers`.
The query for Ethereum returns data that is parsed using the `ethereum_parser` module in `parsers`.
All other queries return data already in the necessary parsed form, so they are parsed using a "dummy" parser that
only sorts the blocks.
