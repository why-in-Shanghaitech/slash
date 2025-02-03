# {py:mod}`slash.daemon`

```{py:module} slash.daemon
```

```{autodoc2-docstring} slash.daemon
:parser: slash.docstrings
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`DaemonPid <slash.daemon.DaemonPid>`
  - ```{autodoc2-docstring} slash.daemon.DaemonPid
    :parser: slash.docstrings
    :summary:
    ```
* - {py:obj}`Daemon <slash.daemon.Daemon>`
  - ```{autodoc2-docstring} slash.daemon.Daemon
    :parser: slash.docstrings
    :summary:
    ```
* - {py:obj}`ProcessDaemon <slash.daemon.ProcessDaemon>`
  - ```{autodoc2-docstring} slash.daemon.ProcessDaemon
    :parser: slash.docstrings
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`logger <slash.daemon.logger>`
  - ```{autodoc2-docstring} slash.daemon.logger
    :parser: slash.docstrings
    :summary:
    ```
````

### API

````{py:data} logger
:canonical: slash.daemon.logger
:value: >
   None

```{autodoc2-docstring} slash.daemon.logger
:parser: slash.docstrings
```

````

`````{py:class} DaemonPid(name: str)
:canonical: slash.daemon.DaemonPid

```{autodoc2-docstring} slash.daemon.DaemonPid
:parser: slash.docstrings
```

```{rubric} Initialization
```

```{autodoc2-docstring} slash.daemon.DaemonPid.__init__
:parser: slash.docstrings
```

````{py:property} deamon_pid
:canonical: slash.daemon.DaemonPid.deamon_pid
:type: pathlib.Path

```{autodoc2-docstring} slash.daemon.DaemonPid.deamon_pid
:parser: slash.docstrings
```

````

````{py:property} pid
:canonical: slash.daemon.DaemonPid.pid
:type: int

```{autodoc2-docstring} slash.daemon.DaemonPid.pid
:parser: slash.docstrings
```

````

````{py:property} is_running
:canonical: slash.daemon.DaemonPid.is_running

```{autodoc2-docstring} slash.daemon.DaemonPid.is_running
:parser: slash.docstrings
```

````

`````

`````{py:class} Daemon()
:canonical: slash.daemon.Daemon

```{autodoc2-docstring} slash.daemon.Daemon
:parser: slash.docstrings
```

```{rubric} Initialization
```

```{autodoc2-docstring} slash.daemon.Daemon.__init__
:parser: slash.docstrings
```

````{py:attribute} name
:canonical: slash.daemon.Daemon.name
:value: >
   None

```{autodoc2-docstring} slash.daemon.Daemon.name
:parser: slash.docstrings
```

````

````{py:attribute} interval
:canonical: slash.daemon.Daemon.interval
:value: >
   60

```{autodoc2-docstring} slash.daemon.Daemon.interval
:parser: slash.docstrings
```

````

````{py:method} launch_command() -> typing.List[str]
:canonical: slash.daemon.Daemon.launch_command
:abstractmethod:

```{autodoc2-docstring} slash.daemon.Daemon.launch_command
:parser: slash.docstrings
```

````

````{py:method} getid(job: str) -> re.Match[str]
:canonical: slash.daemon.Daemon.getid
:abstractmethod:

```{autodoc2-docstring} slash.daemon.Daemon.getid
:parser: slash.docstrings
```

````

````{py:method} validate(match: re.Match[str]) -> bool
:canonical: slash.daemon.Daemon.validate
:abstractmethod:

```{autodoc2-docstring} slash.daemon.Daemon.validate
:parser: slash.docstrings
```

````

````{py:method} start()
:canonical: slash.daemon.Daemon.start

```{autodoc2-docstring} slash.daemon.Daemon.start
:parser: slash.docstrings
```

````

````{py:method} stop()
:canonical: slash.daemon.Daemon.stop

```{autodoc2-docstring} slash.daemon.Daemon.stop
:parser: slash.docstrings
```

````

````{py:method} loop(ppid: int)
:canonical: slash.daemon.Daemon.loop

```{autodoc2-docstring} slash.daemon.Daemon.loop
:parser: slash.docstrings
```

````

`````

`````{py:class} ProcessDaemon()
:canonical: slash.daemon.ProcessDaemon

Bases: {py:obj}`slash.daemon.Daemon`

```{autodoc2-docstring} slash.daemon.ProcessDaemon
:parser: slash.docstrings
```

```{rubric} Initialization
```

```{autodoc2-docstring} slash.daemon.ProcessDaemon.__init__
:parser: slash.docstrings
```

````{py:attribute} name
:canonical: slash.daemon.ProcessDaemon.name
:value: >
   'pid'

```{autodoc2-docstring} slash.daemon.ProcessDaemon.name
:parser: slash.docstrings
```

````

````{py:method} launch_command() -> typing.List[str]
:canonical: slash.daemon.ProcessDaemon.launch_command

```{autodoc2-docstring} slash.daemon.ProcessDaemon.launch_command
:parser: slash.docstrings
```

````

````{py:method} getid(job: str) -> re.Match[str]
:canonical: slash.daemon.ProcessDaemon.getid

```{autodoc2-docstring} slash.daemon.ProcessDaemon.getid
:parser: slash.docstrings
```

````

````{py:method} validate(match: re.Match[str]) -> bool
:canonical: slash.daemon.ProcessDaemon.validate

```{autodoc2-docstring} slash.daemon.ProcessDaemon.validate
:parser: slash.docstrings
```

````

`````
