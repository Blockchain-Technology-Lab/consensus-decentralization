# Legal links 

The file `src/helpers/legal_links.json` defines information about legal links
between entities. This file is common and corresponds to all ledgers. 

The structure of the file is:
```
{
  "<year>": {
      "<parent company>": [
          ["<pool name>", "<source of information>"]
      ]
  }
}
```

`year` defines the year during which the link is/was active. 

`parent company` is the legal entity, such as a company or foundation, which was
in control of the defined pools for the specified year.

`pool name` is the ledger entity, such as a pool or miner, that participated in
block production.

`source of information` should be a _publicly available_ link to a respectable
webpage, which specifies how the legal link between the parent company and the
pool was established.

## Example

Consider the following example file:
```
{
  "2019": {
      "Company A": [
          ["Pool P1", "example.com/link1"],
          ["Pool P2", "example.com/link2"]
      ]
  },
  "2020": {
      "Company A": [
          ["Pool P2", "example.com/link2"]
      ],
      "Company B": [
          ["Pool P1", "example.com/link3"]
      ]
  },
  "2020": {
      "Company A": [
          ["Pool P2", "example.com/link2"]
      ],
      "Company B": [
          ["Pool P1", "example.com/link3"]
      ],
      "Company C": [
          ["Pool P3", "example.com/link4"]
      ]
  }
}
```

This example defines the following information. In 2019, company A
owned/controlled two pools, P1 and P2. In 2020, the control of pool P1 was
transferred to a different company B. Finally, in 2021 information about the
ownership of pool P3 by company C was published.

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
- If a link was active for multiple years, there should exist a distinct entry for each year.
- The value of the pool's name (that is the first value in each array entry under a company), should be _the same_ as the value that corresponds to a key `name` in the ledger-specific pool information, as defined in the directory `pool_information`. If this string is not _exactly_ the same (including capitalization), the link will not be identified during the mapping process.
