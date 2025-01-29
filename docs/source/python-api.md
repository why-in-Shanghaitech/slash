# Python Interface

Use the python interface to python codes.

```python
import os
from slash import Slash

# excute a command with the environment
with Slash('myenv'):
    os.system('wget huggingface.co')
```

```{autodoc2-object} slash.slash.Slash
no_index = true
```

