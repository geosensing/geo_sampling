# Examples Gallery

This section provides complete, working examples that demonstrate geo-sampling capabilities. All examples include real data outputs that you can download and examine.

## 🚀 Getting Started

::::{grid} 1 1 2 2
:gutter: 3

:::{grid-item-card}
:link: python-api
:link-type: doc

🐍 **Python API Examples**
^^^
Complete Python workflows with actual Delhi road data. Includes 1,220 road segments and 1,000-sample outputs.

**Features:** Basic extraction, sampling, visualization
**Data:** Delhi, India road network
**Output:** Sample plots and CSV files
:::

:::{grid-item-card}
:link: cli-usage
:link-type: doc

💻 **Command Line Usage**
^^^
Master the geo-sampling CLI with working examples and real command outputs.

**Features:** All CLI commands with examples
**Data:** Multiple regions and countries
**Output:** Command logs and sample files
:::

:::{grid-item-card}
:link: advanced
:link-type: doc

🎯 **Advanced Sampling**
^^^
Sophisticated sampling strategies with Singapore road network examples.

**Features:** Random, stratified, filtered sampling
**Data:** Singapore Central region (470 segments)
**Output:** Comparison plots and multiple samples
:::

:::{grid-item-card}
:link: /examples/outputs/
:link-type: url
:link-alt: Download Examples

📁 **Download Outputs**
^^^
All example outputs are available for download. Browse CSV files, plots, and sample data.

**Includes:** Sample datasets, visualizations, CLI logs
**Format:** CSV, PNG, TXT files
**Size:** Ready-to-use examples
:::
::::

## 📊 Live Data Examples

All examples use **real OpenStreetMap data** and generate **actual outputs** that are included with the package:

### Delhi Basic Workflow
- **Input**: NCT of Delhi administrative boundary
- **Output**: 1,220 total road segments → 1,000 random sample
- **Files**: [`delhi_all_roads.csv`](../examples/outputs/01_basic_workflow/delhi_all_roads.csv), [`delhi_sampled_roads.csv`](../examples/outputs/01_basic_workflow/delhi_sampled_roads.csv)

### Singapore Advanced Sampling
- **Input**: Singapore Central region
- **Output**: Multiple sampling strategies (random, stratified, filtered)
- **Files**: [`singapore_*.csv`](../examples/outputs/02_advanced_sampling/) with comparison plots

### CLI Command Examples
- **Input**: Various countries and regions
- **Output**: Command logs and sample outputs
- **Files**: [`commands_log.txt`](../examples/outputs/03_cli_usage/commands_log.txt)

## 🔍 Code + Data Philosophy

Each example provides:

1. **🔧 Working code** - Copy-paste ready scripts
2. **📈 Real outputs** - Actual CSV files and plots you can examine
3. **⚡ Both interfaces** - Python API and CLI equivalents
4. **📋 Documentation** - Step-by-step explanations

## Quick Navigation

```{toctree}
:maxdepth: 2
:hidden:

python-api
cli-usage
advanced
```

**By Interface:**
- [Python API Examples](python-api.md) - For programmatic usage
- [CLI Examples](cli-usage.md) - For command-line workflows

**By Complexity:**
- [Basic Workflow](python-api.md#basic-workflow) - Start here
- [Advanced Sampling](advanced.md) - Multiple strategies
- [Custom Integration](python-api.md#integration-examples) - Research workflows

## 💡 Tips for Using Examples

### Running Examples Locally

```bash
# Clone the repository to get example files
git clone https://github.com/geosensing/geo_sampling.git
cd geo_sampling

# Install with example dependencies
pip install -e .

# Run the basic workflow example
python examples/01_basic_workflow.py

# Try CLI examples
python examples/03_cli_usage.py
```

### Adapting for Your Research

1. **Change the region**: Replace country/region names with your study area
2. **Adjust sample size**: Modify `sample_size` parameters for your needs
3. **Filter road types**: Use `road_types` parameter to focus on specific infrastructure
4. **Set random seed**: Use `seed` parameter for reproducible research

### Understanding Output Files

- **`*_all_roads.csv`**: Complete road network for the region
- **`*_sample.csv`**: Random/stratified sample of road segments
- **`*_plot.png`**: Visualization of sampled road segments
- **Metadata**: Each example includes sampling methodology details

---

*Ready to dive in? Start with [Python API Examples](python-api.md) or jump to [CLI Usage](cli-usage.md)!*
