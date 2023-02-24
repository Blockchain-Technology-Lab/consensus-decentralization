# Pool Information

The file `src/helpers/legal_links.json` defines information about legal links
between entities. This file is common and corresponds to all ledgers. 

The file defines three main types of information.

`coinbase_tags` defines information about pools and miners. Each key
corresponds to a tag or ticker, by which the pool is identifiable in its
produced blocks. The value for each key is a dictionary of pool-related
information, specifically its name, a url to its homepage, etc.

`clusters` defines information about pool clusters. This information is
organized in years (or, if the keyword "all" is used, across all years of
analysis). For each year, a dictionary is defined. Here, each key is the name of
the cluster. Each value is an array of tuples; the first tuple element is the
tag of the pool that belongs in the cluster; the second tuple element is the
_publicly available_ source of information, via which the link between the pool
and the cluster is established.

`pool_addresses` defines ownership information about addresses. As with
clusters, the information is organized per year. For each year a dictionary is
defined; each key is the address, which is present in the created blocks, and
each value is the name of the pool which controls the address.

## Example

Consider the following example file:
```
{
  "clusters": {
      "all": {
          "cluster A": [
              ["P1", "example.com/link1"]
          ]
      },
      "2020": {
          "cluster B": [
              ["--P2--", "example.com/link2"]
          ]
      }
  },
  "coinbase_tags": {
      "P1": {
          "name": "Pool P1",
          "homepage": "example.com/p1"
      },
      "--P2--": {
          "name": "Pool P2",
          "homepage": "example.com/p2"
      }
  },
  "pool_addresses": {
      "2021": {
          "address1": "Pool P2"
      }
  }
}
```

This example defines the following information. There exist two pools, P1
and P2, identifiable by the tags `P1` and `--P2--` respectively. Throughout all
years, P1 belonged to a cluster named "cluster A" and P2 belonged to a cluster
named "cluster B". Also, the address "address1" is known to be controlled by P2.

## Contributing

To update or add information, you should open a Pull
Request that changes one of the files. To do this:

- Open the file (e.g., for Bitcoin, follow [this link](https://github.com/Blockchain-Technology-Lab/pooling-analysis/blob/main/src/helpers/pool_information/bitcoin.json)) on your browser.
- Click `Edit this file`.
- Make your changes in the file.
- On the bottom, initiate a Pull Request.
  - Write a short and descriptive commit title message (e.g., "Update 2019 links for company A").
  - Select `Create a new branch for this commit and start a pull request.`
  - In the page that opens, change the PR title (if necessary) and click on `Create pull request`.

Notes:

- The link to a pool's website should be active and public. 
- The source of the clustering information should be public. You can use specific keywords, in the cases when the information is available on-chain. Specifically:
  - `homepage`: this keyword is used in Cardano, to denote that two pools define the same homepage in their metadata (which are published on-chain)
- The source of address control should be public and trustworthy.
