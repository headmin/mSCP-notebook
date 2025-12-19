# mSCP Notebook

A Marimo-based interactive notebook for generating [macOS Security Compliance Project (mSCP)](https://github.com/usnistgov/macos_security) baselines.

## Why?

Generating mSCP baselines traditionally requires:

- Cloning the mSCP repository manually
- Installing Python dependencies (yaml, xlwt, markdown, etc.)
- Understanding the CLI flags and baseline file paths
- Running terminal commands with the correct arguments
- Managing different git branches to target different OS versions

**This is friction that slows down admins to get started with mSCP.**

This mSCP Notebook removes some of this overhead by providing a **point-and-click interface** that:

- Auto-fetches available platform branches (macOS, iOS, visionOS) from GitHub
- Dynamically loads baselines from your local clone
- Handles repository cloning and branch switching
- Manages Python dependencies automatically via `uv`
- Shows exactly what command will run before execution

For mSCP beginners and occasional explorers who tend to get distracted, this tool is a valuable asset. It eliminates the need to memorize flags and avoid typos in baseline paths. Simply select the desired options, and the tool will generate the necessary commands for you. However, it also offers a learning experience but not abstracts away the CLI tooling. This allows you to comprehend the underlying CLI tool and its flags in a more interactive manner through a structured learning path.

Nonetheless, in your learning path, keep track of the excellent [mSCP documentation](https://pages.nist.gov/macos_security/) and dont be scared to take alook at the [generate_guidance.py](https://github.com/usnistgov/macos_security/blob/main/generate_guidance.py) CLI tool this notebook wraps.

## How Marimo Helps

[Marimo](https://marimo.io) is a reactive Python notebook that runs as a local web app. It solves several problems:

| Traditional Approach | Marimo Approach |
|---------------------|-----------------|
| Terminal commands | Interactive UI dropdowns and buttons |
| Manual dependency install | `uv run` handles dependencies inline |
| Edit scripts to change options | Check/uncheck boxes |
| Read docs for flag meanings | Self-documenting interface |
| Output scrolls past | Persistent output cells |

**Zero external dependency setup.** This Marimo notebook includes all dependencies inline using [PEP 723](https://peps.python.org/pep-0723/) script metadata. When you run with `uv run`, dependencies are installed automatically into an isolated environment. No virtualenv activation. No `pip install -r requirements.txt`. Just run the script.

This is build on next-generation Python tooling, particularly beneficial for those who have been hesitant to use Python in the past. Python has become even more enjoyable with the advent of uv, ruff, Marimo, and numerous other developments in recent years.

## Requirements

- **uv** - Modern Python package manager ([install](https://docs.astral.sh/uv/getting-started/installation/))
- **git** - For cloning/updating the mSCP repository
- **Internet connection** - First run only (to clone mSCP and download dependencies)

That's it. No Python version management. No system Python pollution.

### Install uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Quick Start

Donwload or clone this repository, open the folder and run with `uv`.

```bash
# Clone this repository
git clone https://github.com/your-org/mSCP-notebook.git
cd mSCP-notebook

# Run the notebook (dependencies install automatically)
uv run mscp-notebook.py
```

Your browser opens to `http://127.0.0.1:2718`. From there:

1. **Select a platform branch** (macOS 26 Tahoe, iOS 26, etc.)
2. **Click "Sync Repository"** to clone/update mSCP
3. **Choose a baseline** (CIS Level 1, NIST 800-53, CMMC, indigo, etc.)
4. **Select output options** (profiles, scripts, DDM artifacts)
5. **Click "Generate Baseline"**
6. **View output summary and files**
7. **Open the output folder**
8. **Repeat as needed**

Output appears in `./macos_security/build/<baseline>/`.

## Supported Platforms & Baselines

### Platforms

| Platform | Branches |
|----------|----------|
| macOS | `tahoe` (26), `sequoia` (15), `sonoma` (14), `ventura` (13), `monterey` (12) |
| iOS/iPadOS | `ios_26`, `ios_18`, `ios_17`, `ios_16` |
| visionOS | `visionos_26`, `visionos_2` |

### Baselines

| Framework | Baselines |
|-----------|-----------|
| CIS | Level 1, Level 2, CISv8 |
| NIST 800-53r5 | Low, Moderate, High |
| NIST 800-171 | Single baseline |
| CMMC | Level 1, Level 2 |
| CNSSI-1253 | Low, Moderate, High |

iOS/iPadOS also includes CIS BYOD/Enterprise and indigo baselines.

## Generation Options

| Option | Flag | Description |
|--------|------|-------------|
| Profiles | `-p` | Configuration profiles (.mobileconfig) for MDM deployment |
| Scripts | `-s` | Bash scripts for compliance checking and remediation |
| DDM | `-D` | Declarative Device Management artifacts |
| SCAP/XCCDF | `-g` | Security Content Automation Protocol tags |

## How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                     mSCP Notebook (Marimo)                  │
├─────────────────────────────────────────────────────────────┤
│  1. Fetch branches from github.com/usnistgov/macos_security │
│  2. Clone/checkout selected branch locally                  │
│  3. Load available baselines from baselines/*.yaml          │
│  4. Run generate_guidance.py with selected options          │
│  5. Display output summary and file listing                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    ./macos_security/build/                  │
├─────────────────────────────────────────────────────────────┤
│  └── <baseline>/                                            │
│      ├── *.mobileconfig      (configuration profiles)       │
│      ├── *_compliance.sh     (check/remediation script)     │
│      └── ddm/                (DDM artifacts if enabled)     │
└─────────────────────────────────────────────────────────────┘
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `uv: command not found` | Install uv: `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| `git: command not found` | Install Xcode CLI tools: `xcode-select --install` |
| Baseline not found | Ensure branch matches your target OS version |
| Slow first run | Normal - uv is caching dependencies (subsequent runs are fast) |
| Port 2718 in use | Kill existing process or edit the port in `mscp-notebook.py` |

## Resources

- [mSCP Documentation](https://pages.nist.gov/macos_security/) - Official NIST documentation
- [mSCP GitHub](https://github.com/usnistgov/macos_security) - Source repository
- [Marimo](https://marimo.io) - Reactive Python notebooks
- [uv](https://docs.astral.sh/uv/) - Fast Python package manager

## License

Copyright © 2025, Henry Stamerjohann, Declarative IT GmbH
