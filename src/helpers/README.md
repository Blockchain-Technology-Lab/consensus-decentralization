# Legal links 

The file `src/helpers/legal_links.json` defines information about legal links
between entities. This file is common and corresponds to all ledgers. 

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

## Example

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

## Contributing

To update or add information, you should do open a Pull
Request that changes `legal_links.json`. To do this:

- Open the file ([here](https://github.com/Blockchain-Technology-Lab/pooling-analysis/blob/main/src/helpers/legal_links.json)) on your browser.
- Click `Edit this file` (or open [this link](https://github.com/Blockchain-Technology-Lab/pooling-analysis/edit/main/src/helpers/legal_links.json)).
- Make your changes in the file.
- On the bottom, initiate a Pull Request.
  - Write a short and descriptive commit title message (e.g., "Update 2019 links for company A").
  - Select `Create a new branch for this commit and start a pull request.`
  - In the page that opens, change the PR title (if necessary) and click on `Create pull request`.

Notes:

- The source should be publicly available and respectable. Unofficial tweets or unavailable or private sources will be rejected.
- The value of the pool's name (that is the first value in each array entry under a company), should be _the same_ as the value that corresponds to a key `name` in the ledger-specific pool information, as defined in the directory `pool_information`. If this string is not _exactly_ the same (including capitalization), the link will not be identified during the mapping process.
- There should exist _no gaps_ in a pool's ownership structure.
