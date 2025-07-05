# {py:mod}`slash.core.envs`

```{py:module} slash.core.envs
```

```{autodoc2-docstring} slash.core.envs
:parser: slash.docstrings
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`Env <slash.core.envs.Env>`
  - ```{autodoc2-docstring} slash.core.envs.Env
    :parser: slash.docstrings
    :summary:
    ```
* - {py:obj}`EnvsManager <slash.core.envs.EnvsManager>`
  - ```{autodoc2-docstring} slash.core.envs.EnvsManager
    :parser: slash.docstrings
    :summary:
    ```
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`convert <slash.core.envs.convert>`
  - ```{autodoc2-docstring} slash.core.envs.convert
    :parser: slash.docstrings
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`logger <slash.core.envs.logger>`
  - ```{autodoc2-docstring} slash.core.envs.logger
    :parser: slash.docstrings
    :summary:
    ```
* - {py:obj}`yaml <slash.core.envs.yaml>`
  - ```{autodoc2-docstring} slash.core.envs.yaml
    :parser: slash.docstrings
    :summary:
    ```
````

### API

````{py:data} logger
:canonical: slash.core.envs.logger
:value: >
   None

```{autodoc2-docstring} slash.core.envs.logger
:parser: slash.docstrings
```

````

````{py:data} yaml
:canonical: slash.core.envs.yaml
:value: >
   'YAML(...)'

```{autodoc2-docstring} slash.core.envs.yaml
:parser: slash.docstrings
```

````

````{py:function} convert(sub: typing.Union[str, pathlib.Path], tgt: pathlib.Path) -> pathlib.Path
:canonical: slash.core.envs.convert

```{autodoc2-docstring} slash.core.envs.convert
:parser: slash.docstrings
```
````

`````{py:class} Env(name: str, subscriptions: typing.Optional[typing.List[str]] = None, last_updated: typing.Optional[str] = None)
:canonical: slash.core.envs.Env

```{autodoc2-docstring} slash.core.envs.Env
:parser: slash.docstrings
```

```{rubric} Initialization
```

```{autodoc2-docstring} slash.core.envs.Env.__init__
:parser: slash.docstrings
```

````{py:property} workdir
:canonical: slash.core.envs.Env.workdir
:type: pathlib.Path

```{autodoc2-docstring} slash.core.envs.Env.workdir
:parser: slash.docstrings
```

````

````{py:method} save(path: pathlib.Path = None) -> None
:canonical: slash.core.envs.Env.save

```{autodoc2-docstring} slash.core.envs.Env.save
:parser: slash.docstrings
```

````

````{py:method} save_to(path: pathlib.Path) -> None
:canonical: slash.core.envs.Env.save_to

```{autodoc2-docstring} slash.core.envs.Env.save_to
:parser: slash.docstrings
```

````

````{py:method} load_from(path: pathlib.Path) -> slash.core.envs.Env
:canonical: slash.core.envs.Env.load_from
:classmethod:

```{autodoc2-docstring} slash.core.envs.Env.load_from
:parser: slash.docstrings
```

````

````{py:method} destroy() -> None
:canonical: slash.core.envs.Env.destroy

```{autodoc2-docstring} slash.core.envs.Env.destroy
:parser: slash.docstrings
```

````

````{py:method} update(workdir: pathlib.Path = None) -> bool
:canonical: slash.core.envs.Env.update

```{autodoc2-docstring} slash.core.envs.Env.update
:parser: slash.docstrings
```

````

````{py:method} _get_config() -> dict
:canonical: slash.core.envs.Env._get_config

```{autodoc2-docstring} slash.core.envs.Env._get_config
:parser: slash.docstrings
```

````

````{py:method} _set_config(content: dict)
:canonical: slash.core.envs.Env._set_config

```{autodoc2-docstring} slash.core.envs.Env._set_config
:parser: slash.docstrings
```

````

````{py:method} set_port(port: int = 7890)
:canonical: slash.core.envs.Env.set_port

```{autodoc2-docstring} slash.core.envs.Env.set_port
:parser: slash.docstrings
```

````

````{py:method} set_controller(port: typing.Optional[int] = None, ui_folder: typing.Optional[typing.Union[str, pathlib.Path]] = None, local_only: bool = False, secret: typing.Optional[str] = None) -> str
:canonical: slash.core.envs.Env.set_controller

```{autodoc2-docstring} slash.core.envs.Env.set_controller
:parser: slash.docstrings
```

````

````{py:method} set_dialer_proxy(config: slash.core.config.SlashConfig) -> bool
:canonical: slash.core.envs.Env.set_dialer_proxy

```{autodoc2-docstring} slash.core.envs.Env.set_dialer_proxy
:parser: slash.docstrings
```

````

`````

`````{py:class} EnvsManager()
:canonical: slash.core.envs.EnvsManager

```{autodoc2-docstring} slash.core.envs.EnvsManager
:parser: slash.docstrings
```

```{rubric} Initialization
```

```{autodoc2-docstring} slash.core.envs.EnvsManager.__init__
:parser: slash.docstrings
```

````{py:property} envs
:canonical: slash.core.envs.EnvsManager.envs
:type: typing.Dict[str, slash.core.envs.Env]

```{autodoc2-docstring} slash.core.envs.EnvsManager.envs
:parser: slash.docstrings
```

````

````{py:method} create_env(*args, **kwargs) -> slash.core.envs.Env
:canonical: slash.core.envs.EnvsManager.create_env

```{autodoc2-docstring} slash.core.envs.EnvsManager.create_env
:parser: slash.docstrings
```

````

````{py:method} remove_env(name: str)
:canonical: slash.core.envs.EnvsManager.remove_env

```{autodoc2-docstring} slash.core.envs.EnvsManager.remove_env
:parser: slash.docstrings
```

````

````{py:method} get_env(name)
:canonical: slash.core.envs.EnvsManager.get_env

```{autodoc2-docstring} slash.core.envs.EnvsManager.get_env
:parser: slash.docstrings
```

````

````{py:method} get_envs()
:canonical: slash.core.envs.EnvsManager.get_envs

```{autodoc2-docstring} slash.core.envs.EnvsManager.get_envs
:parser: slash.docstrings
```

````

`````
