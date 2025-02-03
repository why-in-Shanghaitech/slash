# {py:mod}`slash.core.service`

```{py:module} slash.core.service
```

```{autodoc2-docstring} slash.core.service
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`Service <slash.core.service.Service>`
  - ```{autodoc2-docstring} slash.core.service.Service
    :summary:
    ```
* - {py:obj}`ServiceManager <slash.core.service.ServiceManager>`
  - ```{autodoc2-docstring} slash.core.service.ServiceManager
    :summary:
    ```
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`get_yacd_workdir <slash.core.service.get_yacd_workdir>`
  - ```{autodoc2-docstring} slash.core.service.get_yacd_workdir
    :summary:
    ```
* - {py:obj}`get_executable <slash.core.service.get_executable>`
  - ```{autodoc2-docstring} slash.core.service.get_executable
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`logger <slash.core.service.logger>`
  - ```{autodoc2-docstring} slash.core.service.logger
    :summary:
    ```
````

### API

````{py:data} logger
:canonical: slash.core.service.logger
:value: >
   None

```{autodoc2-docstring} slash.core.service.logger
```

````

````{py:function} get_yacd_workdir() -> pathlib.Path
:canonical: slash.core.service.get_yacd_workdir

```{autodoc2-docstring} slash.core.service.get_yacd_workdir
```
````

````{py:function} get_executable() -> pathlib.Path
:canonical: slash.core.service.get_executable

```{autodoc2-docstring} slash.core.service.get_executable
```
````

`````{py:class} Service(pid: int, port: int, ctl: typing.Tuple[int, str], env: slash.core.Env, jobs: typing.List[str])
:canonical: slash.core.service.Service

```{autodoc2-docstring} slash.core.service.Service
```

```{rubric} Initialization
```

```{autodoc2-docstring} slash.core.service.Service.__init__
```

````{py:method} get_controller_urls() -> typing.List[str]
:canonical: slash.core.service.Service.get_controller_urls

```{autodoc2-docstring} slash.core.service.Service.get_controller_urls
```

````

````{py:method} is_alive() -> bool
:canonical: slash.core.service.Service.is_alive

```{autodoc2-docstring} slash.core.service.Service.is_alive
```

````

````{py:method} is_operational() -> bool
:canonical: slash.core.service.Service.is_operational

```{autodoc2-docstring} slash.core.service.Service.is_operational
```

````

````{py:method} launch(env: slash.core.Env, job: str) -> slash.core.service.Service
:canonical: slash.core.service.Service.launch
:classmethod:

```{autodoc2-docstring} slash.core.service.Service.launch
```

````

````{py:method} update() -> bool
:canonical: slash.core.service.Service.update

```{autodoc2-docstring} slash.core.service.Service.update
```

````

````{py:method} stop() -> None
:canonical: slash.core.service.Service.stop

```{autodoc2-docstring} slash.core.service.Service.stop
```

````

````{py:method} load(env: slash.core.Env) -> typing.Union[slash.core.service.Service, None]
:canonical: slash.core.service.Service.load
:classmethod:

```{autodoc2-docstring} slash.core.service.Service.load
```

````

````{py:method} load_from(env: slash.core.Env, path: pathlib.Path) -> typing.Union[slash.core.service.Service, None]
:canonical: slash.core.service.Service.load_from
:classmethod:

```{autodoc2-docstring} slash.core.service.Service.load_from
```

````

````{py:method} save() -> None
:canonical: slash.core.service.Service.save

```{autodoc2-docstring} slash.core.service.Service.save
```

````

````{py:method} save_to(path: pathlib.Path) -> None
:canonical: slash.core.service.Service.save_to

```{autodoc2-docstring} slash.core.service.Service.save_to
```

````

`````

`````{py:class} ServiceManager()
:canonical: slash.core.service.ServiceManager

```{autodoc2-docstring} slash.core.service.ServiceManager
```

```{rubric} Initialization
```

```{autodoc2-docstring} slash.core.service.ServiceManager.__init__
```

````{py:property} services
:canonical: slash.core.service.ServiceManager.services
:type: typing.Dict[str, slash.core.service.Service]

```{autodoc2-docstring} slash.core.service.ServiceManager.services
```

````

````{py:method} launch(env: slash.core.Env, job: str) -> slash.core.service.Service
:canonical: slash.core.service.ServiceManager.launch

```{autodoc2-docstring} slash.core.service.ServiceManager.launch
```

````

````{py:method} stop(env: slash.core.Env, job: str) -> None
:canonical: slash.core.service.ServiceManager.stop

```{autodoc2-docstring} slash.core.service.ServiceManager.stop
```

````

`````
