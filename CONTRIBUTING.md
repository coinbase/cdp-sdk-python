# Contributing Guide

## Development

### Python Version

Developing in this repository requires Python 3.10 or higher.

### Set-up

Clone the repo by running:

```bash
git clone git@github.com:coinbase/cdp-sdk-python.git
```

To install all dependencies, run:

```bash
make install-deps
```

<<<<<<< HEAD
### Formatting

To format the code, run:

```bash
make format
```

### Linting

To detect all lint errors, run:

```bash
make lint
```

=======
### Linting

>>>>>>> cf3f5f1 (WIP)
To autocorrect all lint errors, run:

```bash
make lint-fix
```

<<<<<<< HEAD
### Testing
=======
To detect all lint errors, run:

```bash
make lint
```

### Testing

Install the `pytest` and `pytest-cov` packages to run tests:

```bash
pip install pytest pytest-cov
```

>>>>>>> cf3f5f1 (WIP)
To run all tests, run:

```bash
make test
```

### Generating Documentation

<<<<<<< HEAD
To build and view the documentation locally, run:

```bash
make local-docs
```
=======
To generate documentation from the Python docstrings, run:

```bash
make docs
```

To view the documentation, run:

```bash
make local-docs
```
>>>>>>> cf3f5f1 (WIP)
