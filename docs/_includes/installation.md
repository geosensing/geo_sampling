# Installation

## Prerequisites

The package requires Python 3.11 or higher. Install the package from PyPI:

```bash
pip install geo-sampling
```

## Development Installation

For development, install with development dependencies:

```bash
git clone https://github.com/geosensing/geo_sampling.git
cd geo_sampling
uv sync --group dev
```

### Pre-commit Hooks

To ensure code quality, install pre-commit hooks:

```bash
uv run pre-commit install
```

This will automatically run linting, formatting, and type checking before each commit. You can also run the hooks manually:

```bash
uv run pre-commit run --all-files
```
