# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.1] - 2025-01-17

### Changed
- **Simplified pandas integration**: Pandas is now a direct dependency (no more ImportError handling)
- **Improved development tooling**: Added comprehensive pytest, mypy, and git configuration
- **Enhanced project metadata**: Added Python 3.13 support, better classifiers, and project URLs
- **Cleaner testing**: Removed unnecessary test coverage HTML/XML output, CLI-only reporting
- **Better gitignore**: Enhanced patterns for modern Python development

### Removed
- Unnecessary pandas ImportError handling (pandas is now always available)
- HTML/XML coverage reports (CLI reporting only)
- Obsolete test for pandas ImportError scenario

## [0.3.0] - 2024-12-01

### Added
- **Complete API redesign**: New class-based architecture with `RoadExtractor`, `RoadSampler`, and `RoadPlotter`
- **Enhanced type system**: Proper `RoadSegment` dataclass with validation and conversion methods
- **Comprehensive CLI**: Click-based command-line interface with multiple commands (`extract`, `sample`, `workflow`, `info`)
- **Rich examples**: Three detailed example scripts demonstrating all functionality:
  - `01_basic_workflow.py`: Complete end-to-end Delhi road sampling workflow
  - `02_advanced_sampling.py`: Advanced sampling strategies and comparative analysis
  - `03_cli_usage.py`: Comprehensive CLI usage examples and Python API equivalents
- **Visualization enhancements**: Improved plotting with road type coloring and comparative visualizations
- **Convenience functions**: High-level API for quick road sampling (`sample_roads_for_region`)
- **DataFrame support**: Optional pandas DataFrame conversion for analysis workflows
- **Modern tooling**: Migration to uv build system, ruff for linting/formatting

### Changed
- **Breaking**: Complete rewrite from CLI-focused to Python library-first approach
- **Breaking**: New import structure - use `import geo_sampling as gs` instead of individual modules
- **Breaking**: New class-based API replaces function-based approach
- **Improved error handling**: Better network failure management and user-friendly error messages
- **Enhanced testing**: Comprehensive test suite with 47 tests covering all functionality
- **Updated dependencies**: Modern dependency versions and optional dependencies for development
- **GitHub workflows**: Updated CI/CD for uv build system and new architecture

### Removed
- **Breaking**: Legacy `geo_roads.py` and `sample_roads.py` CLI-only modules
- **Breaking**: Old function-based API and direct CLI script approach
- Legacy test files for old architecture

### Fixed
- Network dependency handling in examples (fail gracefully when BBBike unavailable)
- Code formatting and linting compliance with modern standards
- Documentation consistency across all modules and examples

### Technical Improvements
- Complete type annotations throughout codebase
- Proper separation of concerns (extraction, sampling, visualization, CLI)
- Consistent error handling and validation
- Comprehensive documentation in docstrings and examples
- Modern Python packaging with pyproject.toml
- Full test coverage with appropriate skips for network-dependent tests

## [0.2.1] - Previous release
- Legacy CLI-based functionality
- Basic road extraction and sampling capabilities

## [0.2.0] - Previous release
- Initial stable release with core functionality

## [0.1.1] - Previous release
- Early development version

## [0.0.7] - Previous release
- Initial development version
