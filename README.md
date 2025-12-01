# winzy-whitelist

[![PyPI](https://img.shields.io/pypi/v/winzy-whitelist.svg)](https://pypi.org/project/winzy-whitelist/)
[![Changelog](https://img.shields.io/github/v/release/sukhbinder/winzy-whitelist?include_prereleases&label=changelog)](https://github.com/sukhbinder/winzy-whitelist/releases)
[![Tests](https://github.com/sukhbinder/winzy-whitelist/workflows/Test/badge.svg)](https://github.com/sukhbinder/winzy-whitelist/actions?query=workflow%3ATest)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/sukhbinder/winzy-whitelist/blob/main/LICENSE)

Whitelist python created exe's to make them bat scripts.

## Installation

First configure your Winzy project [to use Winzy](https://github.com/sukhbinder/winzy).

Then install this plugin in the same environment as your Winzy application.
```bash
pip install winzy-whitelist
```
## Usage

Some orgs doesn't allow using exe created by python, this plugin will create and equivalent batch file that can be used.

usage: Lets say `winzy.exe` created by `pip install winzy` is not usable, do this to call it `wiz`

```bash
winzy wlist winzy --alt-app-name wiz
```

This will create a wiz.bat in the correct place and now you can use winzy using the new name `wiz`. If alt-app-name is not provided `winzy.bat` gets created.

## How it Works

When you run `winzy wlist <app_name>`, the tool performs the following steps:

1.  **Finds the Executable**: It searches for the `<app_name>.exe` file in your system's PATH.
2.  **Creates a Companion Script**: In the same directory as the executable, it creates a Python script named `<app_name>-script.py`. This script is designed to call the main function of your application. The tool automatically detects the correct module to import and function to call by inspecting the `console_scripts` entry points defined in your application's packaging.
3.  **Creates a Batch File**: Finally, it creates a batch file (e.g., `<app_name>.bat` or an alternative name if specified) that executes the companion script using `python`. This allows you to run your application through the batch file without directly using the `.exe`.

## Development

To set up this plugin locally, first checkout the code. Then create a new virtual environment:
```bash
cd winzy-whitelist
python -m venv venv
source venv/bin/activate
```
Now install the dependencies and test dependencies:
```bash
pip install -e '.[test]'
```
### Running Tests
To run the tests:
```bash
python -m pytest
```
