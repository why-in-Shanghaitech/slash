# {py:mod}`slash.utils`

```{py:module} slash.utils
```

```{autodoc2-docstring} slash.utils
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`Logger <slash.utils.Logger>`
  - ```{autodoc2-docstring} slash.utils.Logger
    :summary:
    ```
* - {py:obj}`FreePort <slash.utils.FreePort>`
  - ```{autodoc2-docstring} slash.utils.FreePort
    :summary:
    ```
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`dals <slash.utils.dals>`
  - ```{autodoc2-docstring} slash.utils.dals
    :summary:
    ```
* - {py:obj}`download_file <slash.utils.download_file>`
  - ```{autodoc2-docstring} slash.utils.download_file
    :summary:
    ```
* - {py:obj}`runbg <slash.utils.runbg>`
  - ```{autodoc2-docstring} slash.utils.runbg
    :summary:
    ```
* - {py:obj}`get_process <slash.utils.get_process>`
  - ```{autodoc2-docstring} slash.utils.get_process
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`PROXY_RULES <slash.utils.PROXY_RULES>`
  - ```{autodoc2-docstring} slash.utils.PROXY_RULES
    :summary:
    ```
* - {py:obj}`logger <slash.utils.logger>`
  - ```{autodoc2-docstring} slash.utils.logger
    :summary:
    ```
````

### API

````{py:data} PROXY_RULES
:canonical: slash.utils.PROXY_RULES
:value: >
   [['^https?://raw.githubusercontent.com/([^/]*)/([^/]*)/([^/]*)/(.*)$', ['https://cdn.jsdelivr.net/gh...

```{autodoc2-docstring} slash.utils.PROXY_RULES
```

````

`````{py:class} Logger()
:canonical: slash.utils.Logger

```{autodoc2-docstring} slash.utils.Logger
```

```{rubric} Initialization
```

```{autodoc2-docstring} slash.utils.Logger.__init__
```

````{py:method} debug(*args, **kwargs) -> None
:canonical: slash.utils.Logger.debug

```{autodoc2-docstring} slash.utils.Logger.debug
```

````

````{py:method} info(*args, **kwargs) -> None
:canonical: slash.utils.Logger.info

```{autodoc2-docstring} slash.utils.Logger.info
```

````

````{py:method} warn(*args, **kwargs) -> None
:canonical: slash.utils.Logger.warn

```{autodoc2-docstring} slash.utils.Logger.warn
```

````

````{py:method} error(*args, **kwargs) -> None
:canonical: slash.utils.Logger.error

```{autodoc2-docstring} slash.utils.Logger.error
```

````

````{py:method} status(*args, **kwargs) -> rich.status.Status
:canonical: slash.utils.Logger.status

```{autodoc2-docstring} slash.utils.Logger.status
```

````

````{py:method} mute() -> None
:canonical: slash.utils.Logger.mute

```{autodoc2-docstring} slash.utils.Logger.mute
```

````

````{py:method} unmute() -> None
:canonical: slash.utils.Logger.unmute

```{autodoc2-docstring} slash.utils.Logger.unmute
```

````

`````

````{py:data} logger
:canonical: slash.utils.logger
:value: >
   'Logger(...)'

```{autodoc2-docstring} slash.utils.logger
```

````

`````{py:class} FreePort(ports: typing.Iterable = None, timeout: int = -1)
:canonical: slash.utils.FreePort

```{autodoc2-docstring} slash.utils.FreePort
```

```{rubric} Initialization
```

```{autodoc2-docstring} slash.utils.FreePort.__init__
```

````{py:method} is_free(port: int) -> bool
:canonical: slash.utils.FreePort.is_free
:staticmethod:

```{autodoc2-docstring} slash.utils.FreePort.is_free
```

````

````{py:method} acquire() -> slash.utils.FreePort
:canonical: slash.utils.FreePort.acquire

```{autodoc2-docstring} slash.utils.FreePort.acquire
```

````

````{py:method} release() -> None
:canonical: slash.utils.FreePort.release

```{autodoc2-docstring} slash.utils.FreePort.release
```

````

````{py:method} __enter__() -> slash.utils.FreePort
:canonical: slash.utils.FreePort.__enter__

```{autodoc2-docstring} slash.utils.FreePort.__enter__
```

````

````{py:method} __exit__(exc_type, exc_value, traceback) -> None
:canonical: slash.utils.FreePort.__exit__

```{autodoc2-docstring} slash.utils.FreePort.__exit__
```

````

`````

````{py:function} dals(string)
:canonical: slash.utils.dals

```{autodoc2-docstring} slash.utils.dals
```
````

````{py:function} download_file(urls: typing.Union[str, typing.List[str]], path: typing.Union[str, pathlib.Path], desc: str = 'Downloading...', timeout: typing.Union[int, typing.Tuple[int, int]] = (15, 180), write_callback=None)
:canonical: slash.utils.download_file

```{autodoc2-docstring} slash.utils.download_file
```
````

````{py:function} runbg(command: typing.List[str]) -> int
:canonical: slash.utils.runbg

```{autodoc2-docstring} slash.utils.runbg
```
````

````{py:function} get_process(pid: typing.Optional[int] = None) -> typing.Union[psutil.Process, None]
:canonical: slash.utils.get_process

```{autodoc2-docstring} slash.utils.get_process
```
````
