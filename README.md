# Slash

SLURM Link Assistant Service Hub (SLASH) is a submodule for the python package [sapp](https://github.com/why-in-Shanghaitech/sapp), dealing with the Internect connection problems on slurm compute nodes.

## How to use

### Quick Start

```bash
# Create a new environment with a subscription
# e.g. https://raw.githubusercontent.com/Pawdroid/Free-servers/main/sub
slash create -n myenv -f <your_subscription>
# Run a command with the newly created environment
slash run -n myenv wget huggingface.co
```

### Advanced Usage

The usage is very similar to `conda`. You can activate and deactivate the environment.

```bash
# Initialize the Slash environment, then open a new terminal
slash init
# (In a new terminal) Activate the environment
slash activate myenv
# Run a command with the environment
wget huggingface.co
# Deactivate the environment
slash deactivate

# List all environments
slash env list
# Remove the environment
slash remove myenv
```

### Python Interface

Use the python interface to python codes.

```python
import os
from slash import Slash

# excute a command with the environment
with Slash('myenv'):
    os.system('wget huggingface.co')
```

## Install

```bash
pip install git+https://github.com/why-in-Shanghaitech/slash.git
```

## Uninstall

```sh
pip uninstall slash
```
