# Evaluation Results Summary

Document your team's evaluation results below.

## Summary Overview

- **Date of Evaluation:** 2026-10-22
- **Model Evaluated:** (e.g., `qwen3:1.7b`)
- **Total Test Cases Executed:** 19
- **Passed:** 11
- **Failed:** 8
- **Pass Rate:** 58%

## Performance by Category

| Category | Total Cases | Passed | Failed | Pass Rate |
| :--- | :---: | :---: | :---: | :---: |
| Successful Cases | 4 | 4 | 0 | 100% |
| Difficult Cases | 6 | 2 | 4 | 33% |
| Failure / Edge Cases | 9 | 5 | 4 | 55% |

## Key Findings & Failure Analysis

### What worked well
- The system was generally able to find requested information
- If the system could not find anything that matched the criteria given, it simply informed the user of it.
- The system did not come up with fake events or places to fit the given criteria.

### Observed failure modes
- The system had trouble keeping in with certain restrictions given, particularly if asked for events or places in a certain area of Helsinki, it would still give results based anywhere general in Helsinki.
- The system had mixed results when answering out-of-scope inputs, sometimes it would correctly inform the user that the input wasn't in the scope of the system, other times gave a straing answer to the out-of-scope input

## Action Items & Improvements
- [ ] Strenghten prevention of out-of-scope, erroneus and adversarial inputs.
- [ ] Improve on the system's ability to find and pass more information about events and places to the user.
