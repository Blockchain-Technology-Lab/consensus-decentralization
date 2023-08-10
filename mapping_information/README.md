# Mapping Information

This directory contains mapping information about the supported projects.

There exist three subdirectories and two additional files. In each subdirectory, there exists a file for
the corresponding ledger data, if such data exists.

## Identifiers

The files under `identifiers` define information about pools and miners. Each key
corresponds to a tag or ticker, by which the entity is identifiable in its
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

## Clusters

The files under `clusters` define information about pool clusters. This information is
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

## Addresses

The files under `addresses` define ownership information about addresses. As with
clusters, for each address the pool ownership information defines the pool's
name and a public source of information about the ownership.  Each file's
structure is as follows:
```
{
  "address1": {"name": "Pool P2", "source": "example.com"},
}
```

### Example

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



## Legal links

The file `legal_links.json` defines information about legal links between entities. This file is common for all ledgers.

The structure of the file is:
```
{
  "<parent company>": [
      {"name": "<pool name>", "from": "<start date>", "to": "<end date>", "source": "<source of information>"}
  ]
}
```

`parent company` is the legal entity, such as a company or foundation, which was
in control of the defined pools for the specified year.

`pool name` is the ledger entity, such as a pool or miner, that participated in
block production.

`source of information` should be a _publicly available_ link to a respectable
webpage, which specifies how the legal link between the parent company and the
pool was established.

Finally, `from` and `to` define the time frame, during which the pool was controlled by the company. Specifically, `from` is inclusive, so it defines the start of the control, and `to` is exclusive, so it defines the start of the transition of control to another company. If `from` is empty then the control existed since the beginning of the pool's operation; if `to` is empty, then the link between the company and the pool still exists.

### Example

Consider the following example file:
```
{
  "Company A": [
      {"name": "Pool P1", "from": "", "to": "2020", "source": "example.com/link1"},
      {"name": "Pool P2", "from": "", "to": "", "source": "example.com/link2"}
  ],
  "Company B": [
      {"name": "Pool P1", "from": "2020", "to": "", "source": "example.com/link3"}
  ],
  "Company C": [
      {"name": "Pool P3", "from": "2021-03", "to": "", "source": "example.com/link4"}
  ]
}
```

This example defines the following information. P2 has been controlled by company A since its inception and still is. P1 was originally controlled by company A, until the end of 2019, but from the beginning of 2020 it is controlled by company B. Finally, P3 has been controlled since the beginning of March 2021 by company C.


## Special addresses

The file `special_addresses.json` defines per-project information about addresses that are not related to some entity 
but are used for protocol-specific reasons (e.g. treasury address). The format of the file is the following:
```
{
  "Project A": [
      {"address": "A special address 1", "source": "some.public.source"},
      {"address": "A special address 2", "source": "some.public.source"}
  ],
  "Project B": [
      {"address": "B special address", "source": "some.public.source"}
  ]
}
```

## Contributing

To update or add information, you should open a Pull Request that changes one of the files. To do this:

- Open the file (e.g., for Bitcoin, follow [this link](https://github.
  com/Blockchain-Technology-Lab/pooling-analysis/blob/main/mapping_information/identifiers/bitcoin.json)) on
  your browser.
- Click `Edit this file`.
- Make your changes in the file.
- On the bottom, initiate a Pull Request.
  - Write a short and descriptive commit title message (e.g., "Update 2019 links for company A").
  - Select `Create a new branch for this commit and start a pull request.`
  - In the page that opens, change the PR title (if necessary) and click on `Create pull request`.

Notes:

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
  - There should exist _no gaps_ in a pool's ownership structure.
