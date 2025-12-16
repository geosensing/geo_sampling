```{include} _includes/installation.md
```

## Verify Installation

Once installed, verify that the package works:

```bash
# Check CLI is available
geo-sampling --help

# Test Python import
python -c "import geo_sampling as gs; print(f'geo-sampling v{gs.__version__} ready!')"
```

## Troubleshooting

### Common Issues

**Import Error for shapefile module**
```bash
pip install pyshp
```

**Network timeouts when downloading data**
- Check your internet connection
- Some regions may have large datasets - try smaller administrative areas first

**Permission errors on Windows**
```bash
pip install --user geo-sampling
```

### Development Setup

For contributors and advanced users:

```bash
# Clone the repository
git clone https://github.com/geosensing/geo-sampling.git
cd geo-sampling

# Install in development mode with all dependencies
uv sync --group dev --group test --group docs

# Run tests
uv run pytest

# Build documentation
cd docs
uv run make html
```

## Next Steps

- 🚀 Try the [Quick Start Guide](quickstart.md)
- 🔍 Explore [detailed examples](examples/index.md)
- 📚 Browse the [API reference](reference/index.md)
