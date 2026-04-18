# Contributing to ChainKYC

First off, thank you for considering contributing to ChainKYC! It's people like you that make ChainKYC such a great tool for decentralized identity verification.

## Where do I go from here?

If you've noticed a bug or have a feature request, make sure to check our [Issues](https://github.com/Drago1314/ChainKYC/issues) first to see if someone else has already created a ticket. If not, go ahead and make one!

## Fork & create a branch

If this is something you think you can fix, then fork ChainKYC and create a branch with a descriptive name.

A good branch name would be (where issue #325 is the ticket you're working on):

```sh
git checkout -b 325-add-polygon-support
```

## Running Tests

ChainKYC uses Python and Hardhat for automated testing. You can run tests locally by executing:

```sh
python setup_deploy.py --setup
python setup_deploy.py --test
```

Please make sure all tests pass before submitting a Pull Request!

## Pull Request Process

1. Ensure your PR description clearly describes the problem and solution.
2. Update the README.md with details of changes to the interface or project structure if applicable.
3. Once you submit a PR, the GitHub Actions CI will automatically test your smart contracts. Ensure these checks pass.
4. The repository owner will review and merge your changes!
