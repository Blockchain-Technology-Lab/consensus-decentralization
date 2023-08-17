All Submissions:

* [ ] Have you followed the guidelines in our [Contributing documentation](https://blockchain-technology-lab.github.io/pooling-analysis/contribute)?
* [ ] Have you verified that there aren't any other open Pull Requests for the same update/change?
* [ ] Does the Pull Request pass all tests?

# Description

/* Add a short description of your Pull Request */

## Checklist

/* Keep from below the appropriate checklist for your Pull Request and remove the others */

### Update Mapping Support Information Submissions:

- For which ledger do you update the mapping information?
  - [ ] /* ledger name */
- What mapping information do you update?
  - [ ] identifiers
  - [ ] addresses
  - [ ] clusters
  - [ ] legal links
- [ ] Did you update the tests (if needed)?

### New Ledger Support Submissions:

- What mapping information did you add for the new ledger?
  - [ ] identifiers
  - [ ] addresses
  - [ ] clusters
  - [ ] legal links
- Did you create a new parser?
  - [ ] If yes, did you create a unit test for the new parser?
  - [ ] If no, which parser did you reuse? /* parser name */
- Did you create a new mapping?
  - [ ] If yes, did you create a unit test for the new mapping?
  - [ ] If no, which mapping did you reuse? /* mapping name */
- [ ] Did you enable the parser for the new ledger in `src/parse.py`?
- [ ] Did you enable the mapping for the new ledger in `src/map.py`?
- [ ] Did you document support for the new ledger as described in our [Contributing documentation](https://blockchain-technology-lab.github.io/pooling-analysis/contribute)?

### New Metric Support Submissions:

- [ ] Did you put the metric's script under `src/metrics`?
- [ ] Did you name the metric's main function of the script `compute_{metric name}`?
- [ ] Did you import the metric's main function to `src/analyze.py`?
- [ ] Did you add the new metric (and possible parameter values) to `config.yaml`?
- [ ] Did you write unit tests for the new metric?
- [ ] Did you document the new metric in the documentation pages?
