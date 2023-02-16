# Blockchain Pooling Analysis - Documentation

This is the documentation for the Blockchain Pooling Analysis tool developed by the University of Edinburgh's Blockchain 
Technology Lab. The tool is responsible for analyzing pooling behavior of various blockchains and measuring their 
subsequent decentralization levels.

The relevant source code is available on [GitHub](https://github.com/Blockchain-Technology-Lab/pooling-analysis).

## Overview
The tool consists of the following modules:
- Parser
- Mapping
- Metrics

In short, the Parser is responsible for pre-processing the raw data that comes from a full node; it produces a file 
with all the information that is needed for the Mapping. The Mapping takes the output of the parser and combines it with 
some other sources of information to produce a file that reveals the distribution of resources to different entities
(note that in this context "resources" correspond to the number of produced blocks). This distribution is the input for 
the Metrics module, which tracks various decentralization-related metrics and produces a file with the results. 

More details about the different modules can be found in the corresponding [Parser](parsers.md), [Mapping](mappings.md) 
and [Metrics](metrics.md) pages.

Currently, the supported ledgers are:
- Bitcoin
- Bitcoin Cash
- Cardano
- Dash
- Dogecoin
- Ethereum 
- Litecoin
- Tezos
- Zcash

We intend add more ledgers to this list in the future. 

## Contributing
This is an open source project licensed  under the terms and conditions of the [MIT license](LICENSE). Everyone 
is welcome to contribute to it by proposing or implementing their ideas. Example contributions include, but are not 
limited to, reporting potential bugs, supplying useful information for the mappings of supported ledgers, adding support 
for a new ledger, or making the code more efficient. 
Note that all contributions to the project will also be covered by the above-mentioned license.

When making changes in the code, contributors are required to fork the project's repository first and then issue a pull 
request with their changes, which will be reviewed before being integrated to the main branch. Bugs can be reported 
in the [Issues](https://github.com/Blockchain-Technology-Lab/pooling-analysis/issues) page, and all sorts of comments 
and ideas can be brought up in the project's 
[Disccussions](https://github.com/Blockchain-Technology-Lab/pooling-analysis/discussions).
