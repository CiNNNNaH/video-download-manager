# End User Quick Start

## 1. Install Python dependencies
Run:

```bat
scriptsootstrap_python_deps.bat
```

## 2. Run validation checks
Run, in order:

```bat
scriptsun_pretest_checks.bat
scriptsun_regression_suite.bat
scriptsun_multisite_validation.bat
```

## 3. Start VDM
Run:

```bat
python .\main.py
```

## 4. Basic use
1. Paste a supported URL.
2. Choose a browser cookie source if needed.
3. Click **Analyze**.
4. Select a format from the table.
5. Choose media mode and container.
6. Click **Download**.

## 5. If something goes wrong
Run:

```bat
scripts\export_debug_info.bat
```

Then send the generated debug archive together with a short note about what failed.
