# Pool Information

This directory contains pool information about the supported projects.

There exist three subdirectories. In each subdirectory there exists a file for
the corresponding ledger data, if such data exists.

`identifiers` defines information about pools and miners. Each key
corresponds to a tag or ticker, by which the pool is identifiable in its
produced blocks. The value for each key is a dictionary of pool-related
information, specifically its name, a url to its homepage, etc. Each file's
structure is as follows:
```
{
  "P1": {
      "name": "Pool P1",
      "homepage": "example.com/p1"
  },
  "--P2--": {
      "name": "Pool P2",
      "homepage": "example.com/p2"
  }
}
```

`addresses` defines ownership information about addresses. As with
clusters, for each address the pool ownership information defines the pool's
name and a public source of information about the ownership.  Each file's
structure is as follows:
```
{
  "address1": {"name": "Pool P2", "source": "example.com"},
}
```

`clusters` defines information about pool clusters. This information is
organized per cluster. For each cluster, an array of pool-related information is
defined. Each item in the array defines the pool's name, the time window during
which the pool belonged to the cluster (from the beginning of `from` until the
beginning of `to` _excluding_), and the _publicly available_ source of
information, via which the link between the pool and the cluster is established.
Each file's structure is as follows:
```
{
  "cluster A": [
      {"name": "P1", "from": "", "to": "2023", "source": "example.com/link1"}
  ],
  "cluster B": [
      {"name": "--P2--", "from": "", "to": "", "source": "example.com/link2"}
  ]
}
```

## Example

Consider the following example:
```
clusters:
{
      "cluster A": [
          {"name": "P1", "from": "", "to": "2023", "source": "example.com/link1"}
      ],
      "cluster B": [
          {"name": "--P2--", "from": "", "to": "", "source": "example.com/link2"}
      ]
}

identifiers: 
{
      "P1": {
          "name": "Pool P1",
          "homepage": "example.com/p1"
      },
      "--P2--": {
          "name": "Pool P2",
          "homepage": "example.com/p2"
      }
}

addresses:
{
    "address1": {"name": "Pool P2", "from": "2019", "to": "", "source": ""},
}
```

This example defines the following information. There exist two pools, P1 and
P2, identifiable by the tags `P1` and `--P2--` respectively. Since its
beginning and until the end of 2022, P1 belonged to a cluster named "cluster A".
Throughout all years, P2 belonged to a cluster named "cluster B". Also, the
address "address1" is known to be controlled by P2 since the beginning of 2019.

## Contributing

To update or add information, you should open a Pull
Request that changes one of the files. To do this:

- Open the file (e.g., for Bitcoin, follow [this link](https://github.
  com/Blockchain-Technology-Lab/pooling-analysis/blob/main/src/helpers/pool_information/identifiers/bitcoin.json)) on
  your browser.
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
