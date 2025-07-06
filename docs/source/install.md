# Installation

**slash** is a Python package. You can install it with `pip`.

## Install

Simply run the following command to install the package.

```bash
pip install slash-py
```

The following command allows you to install the latest version directly from the GitHub repository, which is useful if you want to try the latest features or bug fixes that haven't been released yet.

```bash
pip install git+https://github.com/why-in-Shanghaitech/slash.git
```

## Uninstall

To uninstall the package, follow the uninstall procedure below:

1. (Optional) Remove initialization scripts if you have run `slash init` before. This step is not necessary, but it helps to clean up your environment.

```bash
slash init --reverse
```

2. Remove the entire `slash` directory from your system. Since this directory contains your credentials and configurations, you may want to back it up before deleting it.

```bash
rm -rf ~/.cache/slash
```

3. Uninstall the package using pip:

```bash
pip uninstall slash-py
```
