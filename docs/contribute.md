# How to contribute

You can contribute to the tool by adding support for a ledger, updating the
mapping process for an existing ledger, or adding a new metric. In all cases,
the information should be submitted via a GitHub PR.

## Add support for ledgers

You can add support for a ledger that is not already supported as follows.

### Mapping information

In the directory `mapping_information`, there exist three folders (`addresses`,
`clusters`, `identifiers`). In each folder, add a file named
`<project_name>.json`, if there exist such information for the new ledger (for
more details on what type of information each folder corresponds to see the
[mapping
documentation](https://blockchain-technology-lab.github.io/pooling-analysis/mappings/)).

### Parser and mapping

In the directory `src/parsers`, create a file named `<project_name>_parser.py`,
if no existing parser can be reused. In this file create a new class, which
inherits from the `DefaultParser` class of `default_parser.py`. Then,
override its `parse` method in order to implement the new parser (or override another
method if there are only small changes needed, e.g. `parse_identifiers` if the only thing
that is different from the default parser is the way identifiers are decoded).

In the directory `src/mappings`, create a file named
`<project_name>_mapping.py`, if no existing mapping can be reused. In this file
create a new class, which inherits from the `DefaultMapping` class of `default_mapping.py`.
Then, override its `process` method. This method takes as input a time period in
the form `yyyy-mm-dd` (e.g., '2022' for the year 2022, '2022-11' for November
2022, '2022-11-12' for 12 November 2022), returns a dictionary of the form
`{'<entity name>': <number of resources>}`, and creates a csv file with the mapped
data for this timeframe in the `output` directory.

Then, you should enable support for the new ledger in the parser and mapping
module scripts. Specifically:

- in the script `src/parse.py`, import the parser class and assign it to the
  project's name in the `ledger_parser` dictionary;
- in the script `src/map.py`, import the mapping class and assign it to the
  project's name in the dictionary `ledger_mapping`.

*Notes*:

- You should add an entry in each dictionary, regardless of whether you use a new or existing parser or mapping – if no
  new parser or mapping class was created for the project, simply assign the suitable class (e.g. DefaultParser or
  DefaultMapping) to the project's name in the corresponding dictionary.
- If you create a new parser/mapping, you should also add unit
  tests [here](https://github.com/Blockchain-Technology-Lab/pooling-analysis/tree/main/tests)

### Documentation

Finally, you should include the new ledger in the documentation pages;
specifically:

- add the ledger in the list of supported ledgers in the repository's main [README file](https://github.com/Blockchain-Technology-Lab/pooling-analysis/blob/main/README.md)
- add the ledger in the list of supported ledgers in the [index documentation page](https://github.com/Blockchain-Technology-Lab/pooling-analysis/blob/main/docs/index.md)
- document the new ledger's parser in the [corresponding documentation page](https://github.com/Blockchain-Technology-Lab/pooling-analysis/blob/main/docs/parsers.md)
- document how the new ledger's data is retrieved in the [corresponding documentation page](https://github.com/Blockchain-Technology-Lab/pooling-analysis/blob/main/docs/data.md);
  if Google BigQuery is used, add the new query to [queries.yaml](https://github.com/Blockchain-Technology-Lab/pooling-analysis/blob/main/queries.yaml)

## Update existing mapping information

All mapping data are in the folder `mapping_information`. To update or add
information about a supported ledger's mapping, you should open a Pull Request.
This can be done either via console or as follows, via the browser:

- Open the file that you want to change (e.g., for Bitcoin, follow 
  [this link](https://github.com/Blockchain-Technology-Lab/pooling-analysis/blob/main/mapping_information/identifiers/bitcoin.json))
  on your browser.
- Click `Edit this file`.
- Make your changes in the file.
- On the bottom, initiate a Pull Request.
  - Write a short and descriptive commit title message (e.g., "Update 2019 links for company A").
  - Select `Create a new branch for this commit and start a pull request.`
  - In the page that opens, change the PR title (if necessary) and click on `Create pull request`.

When updating the mapping information, the following guidelines should be
observed:

- The link to a pool's website should be active and public. 
- All sources cited should be publicly available and respectable. Unofficial tweets or 
unavailable or private sources will be rejected.You can use specific keywords, in the cases when the information is 
available on-chain. Specifically:
  - `homepage`: this keyword is used in Cardano, to denote that two pools define the same homepage in their metadata 
(which are published on-chain)
- Specifically, for `legal_links.json`:
  - The value of the pool's name (that is the first value in each array entry under a company), should be _the same_ as 
  the value that corresponds to a key `name` in the ledger-specific pool information, as defined in the 
  corresponding `addresses`, `clusters` or `identifiers` file. If this string is not _exactly_ the same 
  (including capitalization), the link will not be identified during the mapping process.
  - There should exist _no time gaps_ in a pool's ownership structure.

## Add metrics

To add a new metric, you should do the following steps.

First, create a relevant script in the folder `src/metrics`. The script should
include a function named `compute_{metric_name}` that, given a dictionary of
entities (as keys) to number of blocks (as values), outputs a single value (the
outcome of the metric).

Second, import this new function to `src/analyze.py`.

Finally, add the name of the metric (which should be the same as the one used in
the filename above) and any parameter values it might require to the file
`config.yaml`, under `metrics`.
