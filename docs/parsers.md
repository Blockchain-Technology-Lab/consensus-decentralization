# Parsers

The parser obtains raw data from a full node (see [Data Collection](data.md) page on how to obtain the required data), 
parses them and outputs a `json` file that contains a list of entries, each entry corresponding to a block in the chain. 
Specifically, the input file should be placed in the `input` directory and named as `<project_name>_raw_data.json`. 
The output file is saved under `output/<project_name>/parsed_data.json`, and it is structured as follows:

```
[
    {
        "number": "<block's number>",
        "timestamp": "<block's timestamp of the form: yyyy-mm-dd hh:mm:ss UTC>",
        "coinbase_addresses": "<address1>,<address2>"
        "coinbase_param": "<coinbase parameter>"
    }
]
```
While `number` and `timestamp` are consistent among different blockchains, the exact information that is included in 
`coinbase_addresses` and `coinbase_param` may vary. Specifically, the field `coinbase_addresses` corresponds to:
- `Bitcoin`, `Bitcoin Cash`, `Dogecoin`, `Litecoin`, `Zcash`, `Dash`: a string of comma-separated addresses which appear 
in the block's coinbase transaction with non-negative value (i.e., which are given some part of the block's fees)
- `Ethereum`: the `miner` field of the block
- `Cardano`: the hash of the pool that created the data, if defined, otherwise the empty string
- `Tezos`: the `baker` field of the block.

And the field `coinbase_param` corresponds to:
- `Bitcoin`, `Bitcoin Cash`, `Dogecoin`, `Litecoin`, `Zcash`, `Dash`: the field `coinbase_param` of the block's coinbase 
transaction
- `Ethereum`: the field `extra_data` of the block
- `Cardano`: the ticker name of the pool that created the block, if defined, otherwise an empty string
- `Tezos`: there is no such field.

If using BigQuery, the queries for Bitcoin, Bitcoin Cash, Dogecoin, Litecoin, Zcash, Dash return data that are parsed 
with the `default_parser` script in `parsers`. 
The query for Cardano returns data that is parsed using the `cardano_parser` script in `parsers`. 
All other queries return data already in the necessary parsed form, so they are parsed using a "dummy" parser.