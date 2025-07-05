# {py:mod}`slash.core.config`

```{py:module} slash.core.config
```

```{autodoc2-docstring} slash.core.config
:parser: slash.docstrings
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`SlashConfig <slash.core.config.SlashConfig>`
  - ```{autodoc2-docstring} slash.core.config.SlashConfig
    :parser: slash.docstrings
    :summary:
    ```
* - {py:obj}`ConfigManager <slash.core.config.ConfigManager>`
  - ```{autodoc2-docstring} slash.core.config.ConfigManager
    :parser: slash.docstrings
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`logger <slash.core.config.logger>`
  - ```{autodoc2-docstring} slash.core.config.logger
    :parser: slash.docstrings
    :summary:
    ```
* - {py:obj}`yaml <slash.core.config.yaml>`
  - ```{autodoc2-docstring} slash.core.config.yaml
    :parser: slash.docstrings
    :summary:
    ```
````

### API

````{py:data} logger
:canonical: slash.core.config.logger
:value: >
   None

```{autodoc2-docstring} slash.core.config.logger
:parser: slash.docstrings
```

````

````{py:data} yaml
:canonical: slash.core.config.yaml
:value: >
   'YAML(...)'

```{autodoc2-docstring} slash.core.config.yaml
:parser: slash.docstrings
```

````

`````{py:class} SlashConfig
:canonical: slash.core.config.SlashConfig

```{autodoc2-docstring} slash.core.config.SlashConfig
:parser: slash.docstrings
```

````{py:attribute} http_server
:canonical: slash.core.config.SlashConfig.http_server
:type: typing.Optional[str]
:value: >
   'field(...)'

```{autodoc2-docstring} slash.core.config.SlashConfig.http_server
:parser: slash.docstrings
```

````

````{py:attribute} http_port
:canonical: slash.core.config.SlashConfig.http_port
:type: typing.Optional[int]
:value: >
   'field(...)'

```{autodoc2-docstring} slash.core.config.SlashConfig.http_port
:parser: slash.docstrings
```

````

`````

`````{py:class} ConfigManager()
:canonical: slash.core.config.ConfigManager

```{autodoc2-docstring} slash.core.config.ConfigManager
:parser: slash.docstrings
```

```{rubric} Initialization
```

```{autodoc2-docstring} slash.core.config.ConfigManager.__init__
:parser: slash.docstrings
```

````{py:method} load() -> dict
:canonical: slash.core.config.ConfigManager.load

```{autodoc2-docstring} slash.core.config.ConfigManager.load
:parser: slash.docstrings
```

````

````{py:method} save(config: dict) -> None
:canonical: slash.core.config.ConfigManager.save

```{autodoc2-docstring} slash.core.config.ConfigManager.save
:parser: slash.docstrings
```

````

````{py:method} get_config() -> slash.core.config.SlashConfig
:canonical: slash.core.config.ConfigManager.get_config

```{autodoc2-docstring} slash.core.config.ConfigManager.get_config
:parser: slash.docstrings
```

````

````{py:method} show() -> None
:canonical: slash.core.config.ConfigManager.show

```{autodoc2-docstring} slash.core.config.ConfigManager.show
:parser: slash.docstrings
```

````

````{py:method} get(key: str) -> typing.Any
:canonical: slash.core.config.ConfigManager.get

```{autodoc2-docstring} slash.core.config.ConfigManager.get
:parser: slash.docstrings
```

````

````{py:method} set(key: str, value: typing.Any) -> None
:canonical: slash.core.config.ConfigManager.set

```{autodoc2-docstring} slash.core.config.ConfigManager.set
:parser: slash.docstrings
```

````

````{py:method} remove_key(key: str) -> None
:canonical: slash.core.config.ConfigManager.remove_key

```{autodoc2-docstring} slash.core.config.ConfigManager.remove_key
:parser: slash.docstrings
```

````

`````
