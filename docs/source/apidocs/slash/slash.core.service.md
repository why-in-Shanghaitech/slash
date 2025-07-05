# {py:mod}`slash.core.service`

```{py:module} slash.core.service
```

```{autodoc2-docstring} slash.core.service
:parser: slash.docstrings
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`Service <slash.core.service.Service>`
  - ```{autodoc2-docstring} slash.core.service.Service
    :parser: slash.docstrings
    :summary:
    ```
* - {py:obj}`ServiceManager <slash.core.service.ServiceManager>`
  - ```{autodoc2-docstring} slash.core.service.ServiceManager
    :parser: slash.docstrings
    :summary:
    ```
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`get_yacd_workdir <slash.core.service.get_yacd_workdir>`
  - ```{autodoc2-docstring} slash.core.service.get_yacd_workdir
    :parser: slash.docstrings
    :summary:
    ```
* - {py:obj}`get_executable <slash.core.service.get_executable>`
  - ```{autodoc2-docstring} slash.core.service.get_executable
    :parser: slash.docstrings
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`logger <slash.core.service.logger>`
  - ```{autodoc2-docstring} slash.core.service.logger
    :parser: slash.docstrings
    :summary:
    ```
````

### API

````{py:data} logger
:canonical: slash.core.service.logger
:value: >
   None

```{autodoc2-docstring} slash.core.service.logger
:parser: slash.docstrings
```

````

````{py:function} get_yacd_workdir() -> pathlib.Path
:canonical: slash.core.service.get_yacd_workdir

```{autodoc2-docstring} slash.core.service.get_yacd_workdir
:parser: slash.docstrings
```
````

````{py:function} get_executable() -> pathlib.Path
:canonical: slash.core.service.get_executable

```{autodoc2-docstring} slash.core.service.get_executable
:parser: slash.docstrings
```
````

`````{py:class} Service(pid: int, port: int, ctl: typing.Tuple[int, str], env: slash.core.Env, jobs: typing.List[str])
:canonical: slash.core.service.Service

```{autodoc2-docstring} slash.core.service.Service
:parser: slash.docstrings
```

```{rubric} Initialization
```

```{autodoc2-docstring} slash.core.service.Service.__init__
:parser: slash.docstrings
```

````{py:method} get_controller_urls() -> typing.List[str]
:canonical: slash.core.service.Service.get_controller_urls

```{autodoc2-docstring} slash.core.service.Service.get_controller_urls
:parser: slash.docstrings
```

````

````{py:method} is_alive() -> bool
:canonical: slash.core.service.Service.is_alive

```{autodoc2-docstring} slash.core.service.Service.is_alive
:parser: slash.docstrings
```

````

````{py:method} is_operational() -> bool
:canonical: slash.core.service.Service.is_operational

```{autodoc2-docstring} slash.core.service.Service.is_operational
:parser: slash.docstrings
```

````

````{py:method} launch(env: slash.core.Env, job: str) -> slash.core.service.Service
:canonical: slash.core.service.Service.launch
:classmethod:

```{autodoc2-docstring} slash.core.service.Service.launch
:parser: slash.docstrings
```

````

````{py:method} update() -> bool
:canonical: slash.core.service.Service.update

```{autodoc2-docstring} slash.core.service.Service.update
:parser: slash.docstrings
```

````

````{py:method} stop() -> None
:canonical: slash.core.service.Service.stop

```{autodoc2-docstring} slash.core.service.Service.stop
:parser: slash.docstrings
```

````

````{py:method} load(env: slash.core.Env) -> typing.Union[slash.core.service.Service, None]
:canonical: slash.core.service.Service.load
:classmethod:

```{autodoc2-docstring} slash.core.service.Service.load
:parser: slash.docstrings
```

````

````{py:method} load_from(env: slash.core.Env, path: pathlib.Path) -> typing.Union[slash.core.service.Service, None]
:canonical: slash.core.service.Service.load_from
:classmethod:

```{autodoc2-docstring} slash.core.service.Service.load_from
:parser: slash.docstrings
```

````

````{py:method} save() -> None
:canonical: slash.core.service.Service.save

```{autodoc2-docstring} slash.core.service.Service.save
:parser: slash.docstrings
```

````

````{py:method} save_to(path: pathlib.Path) -> None
:canonical: slash.core.service.Service.save_to

```{autodoc2-docstring} slash.core.service.Service.save_to
:parser: slash.docstrings
```

````

`````

`````{py:class} ServiceManager()
:canonical: slash.core.service.ServiceManager

```{autodoc2-docstring} slash.core.service.ServiceManager
:parser: slash.docstrings
```

```{rubric} Initialization
```

```{autodoc2-docstring} slash.core.service.ServiceManager.__init__
:parser: slash.docstrings
```

````{py:property} services
:canonical: slash.core.service.ServiceManager.services
:type: typing.Dict[str, slash.core.service.Service]

```{autodoc2-docstring} slash.core.service.ServiceManager.services
:parser: slash.docstrings
```

````

````{py:method} launch(env: slash.core.Env, job: str) -> slash.core.service.Service
:canonical: slash.core.service.ServiceManager.launch

```{autodoc2-docstring} slash.core.service.ServiceManager.launch
:parser: slash.docstrings
```

````

````{py:method} stop(env: slash.core.Env, job: str) -> None
:canonical: slash.core.service.ServiceManager.stop

```{autodoc2-docstring} slash.core.service.ServiceManager.stop
:parser: slash.docstrings
```

````

`````
