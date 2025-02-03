# {py:mod}`slash.slash`

```{py:module} slash.slash
```

```{autodoc2-docstring} slash.slash
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`Slash <slash.slash.Slash>`
  - ```{autodoc2-docstring} slash.slash.Slash
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`logger <slash.slash.logger>`
  - ```{autodoc2-docstring} slash.slash.logger
    :summary:
    ```
````

### API

````{py:data} logger
:canonical: slash.slash.logger
:value: >
   None

```{autodoc2-docstring} slash.slash.logger
```

````

`````{py:class} Slash(env_name: str = 'base')
:canonical: slash.slash.Slash

```{autodoc2-docstring} slash.slash.Slash
```

```{rubric} Initialization
```

```{autodoc2-docstring} slash.slash.Slash.__init__
```

````{py:attribute} daemons
:canonical: slash.slash.Slash.daemons
:value: >
   None

```{autodoc2-docstring} slash.slash.Slash.daemons
```

````

````{py:attribute} config
:canonical: slash.slash.Slash.config
:value: >
   'ConfigManager(...)'

```{autodoc2-docstring} slash.slash.Slash.config
```

````

````{py:attribute} envs_manager
:canonical: slash.slash.Slash.envs_manager
:value: >
   'EnvsManager(...)'

```{autodoc2-docstring} slash.slash.Slash.envs_manager
```

````

````{py:attribute} service_manager
:canonical: slash.slash.Slash.service_manager
:value: >
   'ServiceManager(...)'

```{autodoc2-docstring} slash.slash.Slash.service_manager
```

````

````{py:property} env
:canonical: slash.slash.Slash.env
:type: slash.core.Env

```{autodoc2-docstring} slash.slash.Slash.env
```

````

````{py:property} service
:canonical: slash.slash.Slash.service
:type: slash.core.Service

```{autodoc2-docstring} slash.slash.Slash.service
```

````

````{py:method} launch(job: str) -> slash.core.Service
:canonical: slash.slash.Slash.launch

```{autodoc2-docstring} slash.slash.Slash.launch
```

````

````{py:method} stop(job: str) -> None
:canonical: slash.slash.Slash.stop

```{autodoc2-docstring} slash.slash.Slash.stop
```

````

````{py:method} update() -> bool
:canonical: slash.slash.Slash.update

```{autodoc2-docstring} slash.slash.Slash.update
```

````

````{py:method} info() -> typing.Dict[str, str]
:canonical: slash.slash.Slash.info

```{autodoc2-docstring} slash.slash.Slash.info
```

````

````{py:method} create(name: str, file: str) -> None
:canonical: slash.slash.Slash.create
:classmethod:

```{autodoc2-docstring} slash.slash.Slash.create
```

````

````{py:method} remove(name: str) -> None
:canonical: slash.slash.Slash.remove
:classmethod:

```{autodoc2-docstring} slash.slash.Slash.remove
```

````

````{py:method} list() -> typing.Dict[str, slash.core.Env]
:canonical: slash.slash.Slash.list
:classmethod:

```{autodoc2-docstring} slash.slash.Slash.list
```

````

````{py:method} __enter__() -> slash.slash.Slash
:canonical: slash.slash.Slash.__enter__

```{autodoc2-docstring} slash.slash.Slash.__enter__
```

````

````{py:method} __exit__(type, value, trace) -> None
:canonical: slash.slash.Slash.__exit__

```{autodoc2-docstring} slash.slash.Slash.__exit__
```

````

`````
