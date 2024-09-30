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

To autocorrect all lint errors, run:

```bash
make lint-fix
```

To run all tests, run:

```bash
make test
```

### Generating Documentation

To build and view the documentation locally, run:

```bash
make local-docs
```