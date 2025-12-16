# Geo Sampling Documentation

**Randomly sample locations on streets for data collection and research**

[![CI](https://github.com/geosensing/geo_sampling/actions/workflows/ci.yml/badge.svg)](https://github.com/geosensing/geo_sampling/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/geo_sampling.svg?maxAge=3600)](https://pypi.python.org/pypi/geo_sampling)
[![Downloads](https://pepy.tech/badge/geo-sampling)](https://pepy.tech/project/geo-sampling)

Geo-sampling is a Python package that helps researchers randomly sample street locations for data collection. Whether you're studying potholes, street conditions, or conducting urban research, this package provides a systematic approach to selecting representative road segments from OpenStreetMap data.

## Features

✨ **Simple CLI & Python API** - Easy to use from command line or Python scripts
🌍 **Global Coverage** - Works with any country/region via OpenStreetMap
📊 **Multiple Sampling Strategies** - Random, stratified, and filtered sampling
🎯 **Road Type Filtering** - Focus on specific road types (highways, residential, etc.)
📈 **Built-in Visualization** - Plot samples on maps for validation
💾 **CSV Export** - Standard output format for analysis tools

## Quick Start

Get started in 5 minutes with the complete workflow:

```bash
# Install the package
pip install geo-sampling

# Sample 100 road segments from Singapore
geo-sampling workflow "Singapore" "Central" \
    --sample-size 100 \
    --output singapore_sample.csv \
    --plot
```

```{include} _includes/sampling-strategy.md
```

## Documentation Sections

```{toctree}
:maxdepth: 2

installation
quickstart
examples/index
reference/index
```

## Example Gallery

::::{grid} 1 1 2 2
:gutter: 3

:::{grid-item-card}
:link: examples/python-api
:link-type: doc

🐍 **Python API Examples**
^^^
Learn the programmatic interface with complete examples
:::

:::{grid-item-card}
:link: examples/cli-usage
:link-type: doc

💻 **CLI Usage Guide**
^^^
Master the command-line interface for batch processing
:::

:::{grid-item-card}
:link: examples/advanced
:link-type: doc

🎯 **Advanced Sampling**
^^^
Sophisticated sampling strategies for complex research designs
:::

:::{grid-item-card}
:link: reference/index
:link-type: doc

📚 **API Reference**
^^^
Complete documentation of classes and functions
:::
::::

## Support

- 📖 **Documentation**: You're reading it!
- 🐛 **Issues**: [GitHub Issues](https://github.com/geosensing/geo_sampling/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/geosensing/geo_sampling/discussions)

## License

Released under the [MIT License](https://github.com/geosensing/geo_sampling/blob/public/LICENSE).

---

*Built with ❤️ by [Suriyan Laohaprapanon](https://github.com/soodoku) and [Gaurav Sood](https://github.com/soodoku)*
