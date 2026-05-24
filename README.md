# quantumsite
A tool that uses quantum-inspired optimization algorithms to plan optimal robot movement paths on a construction site, visualized in a web interface

# Installation

## Requirements
- Python 3.12+

## Install (standard)

To clone and install the repository, run:

```bash
git clone https://github.com/jr173555/quantumsite.git
cd quantumsite
pip install .
```

## Install (development)

Install in editable mode so changes to the source are reflected immediately without reinstalling

```bash
pip install -e ".[dev]"
```

If this is your first time installing the package in your environment, make sure to run:

```bash
pre-commit install
```

To also install test and documentation dependencies:

```bash
pip install -e ".[dev,test,docs]"
```
