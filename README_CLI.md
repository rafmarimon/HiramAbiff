# HiramAbiff CLI

HiramAbiff CLI is a command-line interface for accessing the functionality of the HiramAbiff DeFi agent framework.

## Installation

To install HiramAbiff and its CLI, run:

```bash
git clone https://github.com/yourusername/HiramAbiff.git
cd HiramAbiff
pip install -e .
```

## Usage

After installation, you can use the CLI with the following commands:

### Finding Yield Opportunities

The `yield` command finds and displays the best yield opportunities across different blockchains:

```bash
hiramabiff-cli yield --chains Solana Ethereum --min-yield 10 --max-results 5
```

Options:
- `--chains`, `-c`: Blockchains to analyze (e.g., Solana, Ethereum, etc.)
- `--min-yield`, `-y`: Minimum yield percentage to include (default: 5.0%)
- `--min-tvl`, `-t`: Minimum Total Value Locked to include (default: $500,000)
- `--max-results`, `-r`: Maximum number of results to display (default: 5)
- `--name`, `-n`: Name for the agent (default: "YieldHunter")

### Getting Help

To see available commands and options:

```bash
hiramabiff-cli --help
```

For help with a specific command:

```bash
hiramabiff-cli yield --help
```

## Running Directly from Source

If you don't want to install the package, you can run the CLI directly from the source:

```bash
cd HiramAbiff
python src/hiramabiff/cli.py yield --chains Solana Ethereum
```

## Examples

Find the top 3 yield opportunities with at least 15% APY:

```bash
hiramabiff-cli yield --min-yield 15 --max-results 3
```

Focus only on Solana opportunities:

```bash
hiramabiff-cli yield --chains Solana
```

Get more detailed logs:

```bash
hiramabiff-cli --verbose yield
```

## Logs

The CLI creates log files with detailed information in the current directory. 
Log files are named `hiramabiff_YYYY-MM-DD_HH-MM-SS.log` and are rotated when they reach 10MB.

## Development

To extend the CLI with new commands, modify the `src/hiramabiff/cli.py` file and add new subcommands
to the argument parser. 