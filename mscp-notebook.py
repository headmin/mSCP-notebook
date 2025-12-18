# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
# ]
# description = """
# This notebook facilitates the generation of mSCP baselines using Marimo playbooks,
# as a standalone script to simplify the build baseline process for users. 
# It provides an interactive interface and automated module loading, 
# making it easy to create and manage compliance baselines.
# """
# copyright = "Copyright © 2025, Henry Stamerjohann, Declarative IT GmbH"
# usage = """
# 1. UV must be installed.
# 2. Marimo notebooks will auto-import the necessary module dependencies.
# 3. Just run the script, open the browser,  follow the guide to generate mSCP baselines.
# Example:
#     uv run mscp-standalone.py
# """
# ///

import marimo

__generated_with = "0.10.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import subprocess
    import os
    from pathlib import Path
    return mo, subprocess, os, Path


@app.cell
def _(mo):
    mo.md(
        """
        ![mSCP Banner](https://github.com/usnistgov/macos_security/raw/main/templates/images/mscp_banner_outline.png)

        # mSCP Notebook - Simple Baseline Generator

        Generate macOS Security Compliance Project (mSCP) baselines simply, **without the worry of external dependency overhead**.

        This notebook directly uses the mSCP repository, with **uv** for Python package management.

        ---

        ## Prerequisites

        - **uv** must be installed (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
        - **git** must be installed (for cloning mSCP from GitHub)
        - Internet connection (first run only)

        ---
        """
    )


@app.cell
def _(mo):
    mo.md("## Step 1: Configure mSCP Repository")


@app.cell
def _(mo):
    mscp_path = mo.ui.text(
        value="./macos_security",
        label="mSCP Repository Path",
        full_width=True
    )
    mscp_path


@app.cell
def _(mo, subprocess):
    # Fetch branches from GitHub
    def _get_github_branches():
        try:
            _result = subprocess.run(
                ["git", "ls-remote", "--heads", "https://github.com/usnistgov/macos_security.git"],
                capture_output=True,
                text=True,
                timeout=30
            )
            if _result.returncode == 0:
                _branches = []
                for line in _result.stdout.strip().split("\n"):
                    if line:
                        _branch = line.split("refs/heads/")[-1]
                        _branches.append(_branch)
                return sorted(_branches)
        except Exception:
            pass
        return []

    _raw_branches = _get_github_branches()

    # Map branches to friendly names
    _branch_display = {}
    _platform_map = {
        "tahoe": "macOS 26 Tahoe",
        "sequoia": "macOS 15 Sequoia",
        "sonoma": "macOS 14 Sonoma",
        "ventura": "macOS 13 Ventura",
        "monterey": "macOS 12 Monterey",
        "big_sur": "macOS 11 Big Sur",
        "catalina": "macOS 10.15 Catalina",
        "ios_26": "iOS/iPadOS 26",
        "ios_18": "iOS/iPadOS 18",
        "ios_17": "iOS/iPadOS 17",
        "ios_16": "iOS/iPadOS 16",
        "visionos_26": "visionOS 26",
        "visionos_2": "visionOS 2",
        "main": "⚠️ main (development - not recommended)",
    }

    # Filter to platform branches only (exclude dev/feature branches)
    for _b in _raw_branches:
        if _b in _platform_map:
            _branch_display[_platform_map[_b]] = _b
        elif not _b.startswith(("dev", "nist-", "505-")):
            # Include unknown branches but with raw name
            if not any(x in _b for x in ["_fix", "_typo", "create-"]):
                _branch_display[_b] = _b

    # Fallback if fetch failed
    if not _branch_display:
        _branch_display = {
            "macOS 26 Tahoe": "tahoe",
            "macOS 15 Sequoia": "sequoia",
            "iOS 26": "ios_26"
        }

    # Default to newest macOS
    _default = "macOS 26 Tahoe" if "macOS 26 Tahoe" in _branch_display else (
        "macOS 15 Sequoia" if "macOS 15 Sequoia" in _branch_display else list(_branch_display.keys())[0]
    )

    branch = mo.ui.dropdown(
        options=_branch_display,
        value=_default,
        label="Platform Branch"
    )
    branch


@app.cell
def _(mo, mscp_path, Path, subprocess, sync_complete):
    # This cell depends on sync_complete to refresh AFTER sync finishes
    _ = sync_complete

    _path = Path(mscp_path.value).expanduser()
    _exists = _path.exists() and (_path / "scripts" / "generate_guidance.py").exists()

    if _exists:
        # Get current branch
        try:
            _result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=_path,
                capture_output=True,
                text=True
            )
            _current_branch = _result.stdout.strip() if _result.returncode == 0 else "unknown"
        except:
            _current_branch = "unknown"

        _status = mo.callout(
            mo.md(f"mSCP repository found at `{_path}`\n\nCurrent branch: **{_current_branch}**"),
            kind="success"
        )
    else:
        _status = mo.callout(
            mo.md(f"mSCP repository not found at `{_path}`\n\nClick **Sync Repository** below to download."),
            kind="warn"
        )
    _status


@app.cell
def _(mo, mscp_path, branch):
    sync_button = mo.ui.run_button(label="Sync Repository")
    mo.md(f"**Selected:** {branch.value} → "), sync_button


@app.cell
def _(mo, sync_button, mscp_path, branch, subprocess, Path):
    _output = ""
    _path = Path(mscp_path.value).expanduser()

    if sync_button.value:
        # Check current state
        _needs_clone = not _path.exists()
        _current_branch = None

        if not _needs_clone:
            try:
                _result = subprocess.run(
                    ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                    cwd=_path,
                    capture_output=True,
                    text=True
                )
                _current_branch = _result.stdout.strip() if _result.returncode == 0 else None
            except:
                pass

        _needs_switch = _current_branch and _current_branch != branch.value

        if _needs_clone:
            _output = f"Cloning mSCP ({branch.value})...\n\n"
            try:
                _result = subprocess.run(
                    ["git", "clone", "--depth", "1", "-b", branch.value,
                     "https://github.com/usnistgov/macos_security.git", str(_path)],
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                _output += _result.stdout + _result.stderr
                if _result.returncode == 0:
                    _output += f"\n\nReady: mSCP ({branch.value})"
                else:
                    _output += f"\n\nClone failed."
            except subprocess.TimeoutExpired:
                _output += "Error: Clone timed out (2 min limit)"
            except Exception as e:
                _output += f"Error: {e}"
        elif _needs_switch:
            _output = f"Switching from {_current_branch} to {branch.value}...\n\n"
            try:
                # Fetch the target branch
                _result = subprocess.run(
                    ["git", "remote", "set-branches", "--add", "origin", branch.value],
                    cwd=_path,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                _result = subprocess.run(
                    ["git", "fetch", "--depth", "1", "origin", branch.value],
                    cwd=_path,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                _output += _result.stdout + _result.stderr

                # Checkout the branch
                _result = subprocess.run(
                    ["git", "checkout", branch.value],
                    cwd=_path,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                _output += _result.stdout + _result.stderr

                if _result.returncode == 0:
                    _output += f"\n\nSwitched to: mSCP ({branch.value})"
                else:
                    _output += f"\n\nSwitch failed."
            except subprocess.TimeoutExpired:
                _output += "Error: Branch switch timed out"
            except Exception as e:
                _output += f"Error: {e}"
        else:
            _output = f"Already on {branch.value}. Updating...\n\n"
            # Just pull latest
            try:
                _result = subprocess.run(
                    ["git", "pull", "--ff-only"],
                    cwd=_path,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                _output += _result.stdout + _result.stderr
                _output += "\n\nRepository up to date."
            except Exception as e:
                _output += f"Error updating: {e}"

    sync_complete = sync_button.value  # Export for dependent cells
    mo.md(f"```\n{_output}\n```") if _output else mo.md("_Click **Sync Repository** to clone or switch branches_")
    return sync_complete,


@app.cell
def _(mo):
    mo.md(
        """
        ---

        ## Step 2: Select Baseline

        > **Note:** Baselines are loaded from your local mSCP clone. After switching branches, the baseline list will update automatically.
        """
    )


@app.cell
def _(mo, mscp_path, Path, sync_complete):
    # Refresh AFTER sync completes
    _ = sync_complete

    # Dynamically load baselines from repo
    _path = Path(mscp_path.value).expanduser() / "baselines"
    _baselines = {}

    if _path.exists():
        for _f in sorted(_path.glob("*.yaml")):
            _name = _f.stem
            # Create friendly display names
            _display = _name.replace("_", " ").replace("-", " ")

            # iOS/mobile-specific baselines
            if "byod" in _name.lower():
                _display = f"CIS {_display.replace('cis ', '').replace('byod', 'BYOD').title()}"
            elif "enterprise" in _name.lower():
                _display = f"CIS {_display.replace('cis ', '').replace('enterprise', 'Enterprise').title()}"
            elif "indigo" in _name.lower():
                _display = f"Indigo {_display.replace('indigo ', '').title()}"
            # Standard macOS baselines
            elif "cis" in _name.lower():
                _display = f"CIS {_display.replace('cis ', '').title()}"
            elif "800-53" in _name:
                _display = f"NIST {_name.upper()}"
            elif "800-171" in _name:
                _display = "NIST SP 800-171"
            elif "cmmc" in _name.lower():
                _display = f"CMMC {_display.replace('cmmc ', '').title()}"
            elif "cnssi" in _name.lower():
                _display = _name.upper().replace("_", " ")
            elif "all_rules" in _name.lower():
                _display = "All Rules (complete)"
            else:
                _display = _display.title()
            _baselines[_display] = _name

    if not _baselines:
        _baselines = {
            "CIS Level 1": "cis_lvl1",
            "CIS Level 2": "cis_lvl2",
            "NIST 800-53r5 Low": "800-53r5_low",
            "NIST 800-53r5 Moderate": "800-53r5_moderate",
            "NIST 800-53r5 High": "800-53r5_high",
        }

    baseline = mo.ui.dropdown(
        options=_baselines,
        value=list(_baselines.keys())[0] if _baselines else "CIS Level 1",
        label="Security Baseline"
    )
    baseline


@app.cell
def _(mo):
    mo.md(
        """
        ---

        ## Step 3: Configure Generation Options
        """
    )


@app.cell
def _(mo):
    output_dir = mo.ui.text(
        value="./mscp-output",
        label="Output Directory",
        full_width=True
    )
    output_dir


@app.cell
def _(mo):
    generate_profiles = mo.ui.checkbox(label="Generate Profiles (-p)", value=True)
    generate_scripts = mo.ui.checkbox(label="Generate Scripts (-s)", value=True)
    generate_ddm = mo.ui.checkbox(label="Generate DDM Artifacts (-D)", value=False)
    generate_guidance = mo.ui.checkbox(label="Generate SCAP/XCCDF Tags (-g)", value=False)

    mo.hstack([generate_profiles, generate_scripts, generate_ddm, generate_guidance], gap=2)


@app.cell
def _(mo, mscp_path, baseline, output_dir, generate_profiles, generate_scripts, generate_ddm, generate_guidance, Path):
    _path = Path(mscp_path.value).expanduser()
    _flags = []
    if generate_profiles.value:
        _flags.append("-p")
    if generate_scripts.value:
        _flags.append("-s")
    if generate_ddm.value:
        _flags.append("-D")
    if generate_guidance.value:
        _flags.append("-g")

    _flags_str = " ".join(_flags)
    _baseline_file = f"baselines/{baseline.value}.yaml"

    _cmd = f"""cd {_path}
uv run --with-requirements requirements.txt \\
    python scripts/generate_guidance.py {_flags_str} {_baseline_file}"""

    mo.callout(
        mo.md(f"**Command to execute:**\n```bash\n{_cmd}\n```"),
        kind="info"
    )


@app.cell
def _(mo):
    generate_button = mo.ui.run_button(label="Generate Baseline")
    generate_button


@app.cell
def _(mo, generate_button, mscp_path, baseline, generate_profiles, generate_scripts, generate_ddm, generate_guidance, subprocess, Path, os):
    _output = ""

    if generate_button.value:
        _path = Path(mscp_path.value).expanduser()

        if not _path.exists():
            _output = f"Error: mSCP repository not found at {_path}\nClone it first using the button above."
        elif not (_path / "scripts" / "generate_guidance.py").exists():
            _output = f"Error: generate_guidance.py not found. Is this a valid mSCP repository?"
        else:
            # Build flags
            _flags = []
            if generate_profiles.value:
                _flags.append("-p")
            if generate_scripts.value:
                _flags.append("-s")
            if generate_ddm.value:
                _flags.append("-D")
            if generate_guidance.value:
                _flags.append("-g")

            if not _flags:
                _output = "Error: Select at least one output type (profiles, scripts, etc.)"
            else:
                _baseline_file = f"baselines/{baseline.value}.yaml"

                # Check baseline exists
                if not (_path / _baseline_file).exists():
                    _output = f"Error: Baseline file not found: {_baseline_file}"
                else:
                    try:
                        # Run with uv
                        _cmd = [
                            "uv", "run",
                            "--with-requirements", "requirements.txt",
                            "python", "scripts/generate_guidance.py"
                        ] + _flags + [_baseline_file]

                        _result = subprocess.run(
                            _cmd,
                            cwd=_path,
                            capture_output=True,
                            text=True,
                            timeout=300,
                            env={**os.environ, "PYTHONUNBUFFERED": "1"}
                        )
                        _output = _result.stdout + _result.stderr

                        if _result.returncode == 0:
                            _output += f"\n\nGeneration complete! Output in: {_path}/build/{baseline.value}/"
                        else:
                            _output += f"\n\nGeneration failed with exit code {_result.returncode}"

                    except FileNotFoundError:
                        _output = "Error: uv not found. Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"
                    except subprocess.TimeoutExpired:
                        _output = "Error: Generation timed out (5 min limit)"
                    except Exception as e:
                        _output = f"Error: {e}"

    mo.md(f"```\n{_output}\n```") if _output else mo.md("_Click **Generate Baseline** to run mSCP generation_")


@app.cell
def _(mo):
    mo.md(
        """
        ---

        ## Step 4: View Generated Output
        """
    )


@app.cell
def _(mo, mscp_path, baseline, Path, subprocess):
    _path = Path(mscp_path.value).expanduser() / "build" / baseline.value

    if _path.exists():
        # List generated files
        try:
            _result = subprocess.run(
                ["find", ".", "-type", "f", "-name", "*.mobileconfig"],
                cwd=_path,
                capture_output=True,
                text=True
            )
            _profiles = [f for f in _result.stdout.strip().split("\n") if f]
            _profile_count = len(_profiles)

            # Check for scripts
            _scripts = list(_path.glob("*_compliance.sh"))

            # Check for DDM
            _ddm_path = _path / "ddm"
            _ddm_exists = _ddm_path.exists()

            _summary = f"""### Generated Output Summary

| Category | Count/Status |
|----------|--------------|
| Profiles (.mobileconfig) | {_profile_count} |
| Compliance Script | {'Yes' if _scripts else 'No'} |
| DDM Artifacts | {'Yes' if _ddm_exists else 'No'} |

**Output location:** `{_path}`
"""
            mo.md(_summary)
        except Exception as e:
            mo.callout(mo.md(f"Error listing files: {e}"), kind="danger")
    else:
        mo.callout(
            mo.md(f"No output found at `{_path}`\n\nRun generation first."),
            kind="neutral"
        )


@app.cell
def _(mo):
    list_button = mo.ui.run_button(label="List All Generated Files")
    list_button


@app.cell
def _(mo, list_button, mscp_path, baseline, subprocess, Path):
    _output = ""
    _show_open = False
    _path = Path(mscp_path.value).expanduser() / "build" / baseline.value

    if list_button.value:
        if not _path.exists():
            _output = f"Output directory not found: {_path}"
        else:
            try:
                _result = subprocess.run(
                    ["find", ".", "-type", "f"],
                    cwd=_path,
                    capture_output=True,
                    text=True
                )
                _files = sorted(_result.stdout.strip().split("\n"))
                _output = f"Files in {_path}:\n\n" + "\n".join(_files)
                _show_open = True
            except Exception as e:
                _output = f"Error: {e}"

    open_button = mo.ui.run_button(label="Open Build Folder")

    _display = mo.vstack([
        mo.md(f"```\n{_output}\n```"),
        open_button
    ]) if _show_open else (mo.md(f"```\n{_output}\n```") if _output else mo.md(""))

    _display


@app.cell
def _(open_button, mscp_path, baseline, subprocess, Path):
    if open_button.value:
        _path = Path(mscp_path.value).expanduser() / "build" / baseline.value
        if _path.exists():
            subprocess.run(["open", str(_path)])


@app.cell
def _(mo):
    mo.md(
        """
        ---

        ## External Resources

        - [mSCP Documentation](https://pages.nist.gov/macos_security/) - Official NIST macOS Security Compliance Project documentation
        - [mSCP GitHub Repository](https://github.com/usnistgov/macos_security) - Source code, baselines, and rules

        ---

        ## Quick Reference

        ### Platform Branches

        Branches are fetched dynamically from GitHub. Platform branches include:

        | Platform | Branch Pattern |
        |----------|----------------|
        | macOS | `tahoe`, `sequoia`, `sonoma`, `ventura`, `monterey`, `big_sur`, `catalina` |
        | iOS/iPadOS | `ios_26`, `ios_18`, `ios_17`, `ios_16` |
        | visionOS | `visionos_26`, `visionos_2` |

        > New branches appear automatically when added to the mSCP repository.

        ### Baselines

        **macOS baselines:**
        | Category | Baselines |
        |----------|-----------|
        | CIS | `cis_lvl1`, `cis_lvl2`, `cisv8` |
        | NIST 800-53 | `800-53r5_low`, `800-53r5_moderate`, `800-53r5_high` |
        | NIST 800-171 | `800-171` |
        | CMMC | `cmmc_lvl1`, `cmmc_lvl2` |
        | CNSSI | `cnssi-1253_low`, `cnssi-1253_moderate`, `cnssi-1253_high` |

        **iOS/iPadOS baselines:**
        | Category | Baselines |
        |----------|-----------|
        | CIS BYOD | `cis_lvl1_byod`, `cis_lvl2_byod` |
        | CIS Enterprise | `cis_lvl1_enterprise`, `cis_lvl2_enterprise` |
        | Indigo | `indigo_base`, `indigo_high` |

        ### Generation Flags

        | Flag | Output |
        |------|--------|
        | `-p` | Configuration profiles (.mobileconfig) |
        | `-s` | Compliance check/remediation scripts |
        | `-D` | Declarative Device Management (DDM) artifacts |
        | `-g` | SCAP/XCCDF tags (disables PDF generation) |

        ### Troubleshooting

        | Issue | Solution |
        |-------|----------|
        | "uv not found" | `curl -LsSf https://astral.sh/uv/install.sh \\| sh` |
        | "Permission denied" | `chmod +x scripts/generate_guidance.py` |
        | "Baseline not found" | Check branch matches OS version |
        | Slow first run | uv is downloading dependencies (cached after) |
        """
    )


# Self-contained: run with `uv run playbooks/mscp-standalone.py`
if __name__ == "__main__":
    import sys
    import os
    os.execvp("marimo", ["marimo", "run", sys.argv[0], "--host", "127.0.0.1", "--port", "2718"])
