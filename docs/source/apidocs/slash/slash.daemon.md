# {py:mod}`slash.daemon`

```{py:module} slash.daemon
```

```{autodoc2-docstring} slash.daemon
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`DaemonPid <slash.daemon.DaemonPid>`
  - ```{autodoc2-docstring} slash.daemon.DaemonPid
    :summary:
    ```
* - {py:obj}`Daemon <slash.daemon.Daemon>`
  - ```{autodoc2-docstring} slash.daemon.Daemon
    :summary:
    ```
* - {py:obj}`ProcessDaemon <slash.daemon.ProcessDaemon>`
  - ```{autodoc2-docstring} slash.daemon.ProcessDaemon
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`logger <slash.daemon.logger>`
  - ```{autodoc2-docstring} slash.daemon.logger
    :summary:
    ```
````

### API

````{py:data} logger
:canonical: slash.daemon.logger
:value: >
   None

```{autodoc2-docstring} slash.daemon.logger
```

````

`````{py:class} DaemonPid(name: str)
:canonical: slash.daemon.DaemonPid

```{autodoc2-docstring} slash.daemon.DaemonPid
```

```{rubric} Initialization
```

```{autodoc2-docstring} slash.daemon.DaemonPid.__init__
```

````{py:property} deamon_pid
:canonical: slash.daemon.DaemonPid.deamon_pid
:type: pathlib.Path

```{autodoc2-docstring} slash.daemon.DaemonPid.deamon_pid
```

````

````{py:property} pid
:canonical: slash.daemon.DaemonPid.pid
:type: int

```{autodoc2-docstring} slash.daemon.DaemonPid.pid
```

````

````{py:property} is_running
:canonical: slash.daemon.DaemonPid.is_running

```{autodoc2-docstring} slash.daemon.DaemonPid.is_running
```

````

`````

`````{py:class} Daemon()
:canonical: slash.daemon.Daemon

```{autodoc2-docstring} slash.daemon.Daemon
```

```{rubric} Initialization
```

```{autodoc2-docstring} slash.daemon.Daemon.__init__
```

````{py:attribute} name
:canonical: slash.daemon.Daemon.name
:value: >
   None

```{autodoc2-docstring} slash.daemon.Daemon.name
```

````

````{py:attribute} interval
:canonical: slash.daemon.Daemon.interval
:value: >
   60

```{autodoc2-docstring} slash.daemon.Daemon.interval
```

````

````{py:method} launch_command() -> typing.List[str]
:canonical: slash.daemon.Daemon.launch_command
:abstractmethod:

```{autodoc2-docstring} slash.daemon.Daemon.launch_command
```

````

````{py:method} getid(job: str) -> re.Match[str]
:canonical: slash.daemon.Daemon.getid
:abstractmethod:

```{autodoc2-docstring} slash.daemon.Daemon.getid
```

````

````{py:method} validate(match: re.Match[str]) -> bool
:canonical: slash.daemon.Daemon.validate
:abstractmethod:

```{autodoc2-docstring} slash.daemon.Daemon.validate
```

````

````{py:method} start()
:canonical: slash.daemon.Daemon.start

```{autodoc2-docstring} slash.daemon.Daemon.start
```

````

````{py:method} stop()
:canonical: slash.daemon.Daemon.stop

```{autodoc2-docstring} slash.daemon.Daemon.stop
```

````

````{py:method} loop(ppid: int)
:canonical: slash.daemon.Daemon.loop

```{autodoc2-docstring} slash.daemon.Daemon.loop
```

````

`````

`````{py:class} ProcessDaemon()
:canonical: slash.daemon.ProcessDaemon

Bases: {py:obj}`slash.daemon.Daemon`

```{autodoc2-docstring} slash.daemon.ProcessDaemon
```

```{rubric} Initialization
```

```{autodoc2-docstring} slash.daemon.ProcessDaemon.__init__
```

````{py:attribute} name
:canonical: slash.daemon.ProcessDaemon.name
:value: >
   'pid'

```{autodoc2-docstring} slash.daemon.ProcessDaemon.name
```

````

````{py:method} launch_command() -> typing.List[str]
:canonical: slash.daemon.ProcessDaemon.launch_command

```{autodoc2-docstring} slash.daemon.ProcessDaemon.launch_command
```

````

````{py:method} getid(job: str) -> re.Match[str]
:canonical: slash.daemon.ProcessDaemon.getid

```{autodoc2-docstring} slash.daemon.ProcessDaemon.getid
```

````

````{py:method} validate(match: re.Match[str]) -> bool
:canonical: slash.daemon.ProcessDaemon.validate

```{autodoc2-docstring} slash.daemon.ProcessDaemon.validate
```

````

`````
