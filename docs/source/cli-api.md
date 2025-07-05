# Command Line Interface

## slash

Use **slash** as a command line tool to create, manage, and run environments.

```
usage: slash [-h] command ...
```

```{option} -h, --help
Show the help message and exit.
```

```{option} command
The command to run.

:::{list-table}
:header-rows: 1
:align: left

* - Command
  - Description

* - [`run`](#slash-run)
  - Run a command with a Slash environment

* - [`init`](#slash-init)
  - Initialize the Slash environment

* - [`activate`](#slash-activate)
  - Activate the Slash environment

* - [`deactivate`](#slash-deactivate)
  - Deactivate the Slash environment

* - [`create`](#slash-create)
  - Create a new Slash environment

* - [`remove`](#slash-remove)
  - Remove a Slash environment

* - [`shell`](#slash-shell)
  - Slash shell internal command

* - [`env`](#slash-env)
  - Slash environment command

* - [`config`](#slash-config)
  - Modify configuration values in .slashrc.
:::

```


### slash run

Run a command with a Slash environment.

```
usage: slash run [-h] [-n ENV_NAME] command [args ...]
```

```{option} -h, --help
Show the help message and exit.
```

```{option} -n ENV_NAME, --name ENV_NAME
The name of the environment to run the command in.
```

```{option} command
The command to run.
```

```{option} args
The arguments to pass to the command.
```


### slash init

Initialize the Slash environment.

```
usage: slash init [-h]
```

```{option} -h, --help
Show the help message and exit.
```

### slash activate

Activate the Slash environment.

```
usage: slash activate [-h] ENV_NAME
```

```{option} -h, --help
Show the help message and exit.
```

```{option} ENV_NAME
The name of the environment to activate.
```

### slash deactivate

Deactivate the Slash environment.

```
usage: slash deactivate [-h]
```

```{option} -h, --help
Show the help message and exit.
```

### slash create

Create a new Slash environment.

```
usage: slash create [-h] -n ENV_NAME -f SUBSCRIPTION
```

```{option} -h, --help
Show the help message and exit.
```

```{option} -n ENV_NAME, --name ENV_NAME
The name of the environment to create.
```

```{option} -f SUBSCRIPTION, --file SUBSCRIPTION
The subscription to use for the environment.
```

### slash remove

Remove a Slash environment.

```
usage: slash remove [-h] ENV_NAME
```

```{option} -h, --help
Show the help message and exit.
```

```{option} ENV_NAME
The name of the environment to remove.
```

### slash shell

Slash shell internal command. Users should not use this command directly.

```
usage: slash shell [-h]
```

```{option} -h, --help
Show the help message and exit.
```

### slash env

Slash environment command.

```
usage: slash env [-h] command ...
```

```{option} -h, --help
Show the help message and exit.
```

```{option} command
The command to run.

:::{list-table}
:header-rows: 1
:align: left

* - Command
  - Description

* - [`list`](#slash-env-list)
  - List all environments

* - [`activate`](#slash-env-activate)
  - Activate the environment

* - [`deactivate`](#slash-env-deactivate)
  - Deactivate the environment

* - [`remove`](#slash-env-remove)
  - Remove the environment
:::
```

#### slash env list

List all environments.

```
usage: slash env list [-h]
```

```{option} -h, --help
Show the help message and exit.
```

#### slash env activate

Activate the environment.

It will also produce some environment variables that can be used in the current shell.

:::{list-table}
:header-rows: 1
:align: left

* - Environment Variable
  - Description

* - `SLASH_ENV`
  - The name of the activated environment.

* - `SLASH_STASH`
  - The overrided environment variables. It will be restored when the environment is deactivated.
:::

```
usage: slash env activate [-h] ENV_NAME
```

```{option} -h, --help
Show the help message and exit.
```

```{option} ENV_NAME
The name of the environment to activate.
```

#### slash env deactivate

Deactivate the environment.

```
usage: slash env deactivate [-h]
```

```{option} -h, --help
Show the help message and exit.
```

#### slash env remove

Remove the environment.

```
usage: slash env remove [-h] ENV_NAME
```

```{option} -h, --help
Show the help message and exit.
```

```{option} ENV_NAME
The name of the environment to remove.
```

### slash config

Modify configuration values in .slashrc.

:::{list-table}
:header-rows: 1
:align: left

* - Option
  - Type
  - Description

* - `http_server`
  - `str`
  - The proxy server address.

* - `http_port`
  - `int`
  - The proxy server port.
:::

```
usage: slash config [-h] command
```

```{option} -h, --help
Show the help message and exit.
```

```{option} command
Config subcommand. Modify configuration values in .slashrc.

:::{list-table}
:header-rows: 1
:align: left

* - Command
  - Description

* - [`show`](#slash-config-show)
  - Show all configuration values

* - [`get`](#slash-config-get)
  - Get a configuration value

* - [`set`](#slash-config-set)
  - Set a configuration value

* - [`remove-key`](#slash-config-remove-key)
  - Remove a configuration key
:::
```

#### slash config show

Show all configuration values.

```
usage: slash config show [-h]
```

```{option} -h, --help
Show the help message and exit.
```

#### slash config get

Get a configuration value.

```
usage: slash config get [-h] key
```

```{option} -h, --help
Show the help message and exit.
```

```{option} key
The key to get the value of.
```

#### slash config set

Set a configuration value.

```
usage: slash config set [-h] key value
```

```{option} -h, --help
Show the help message and exit.
```

```{option} key
The key to set the value of.
```

```{option} value
The value to set the key to.
```

#### slash config remove-key

Remove a configuration key.

```
usage: slash config remove-key [-h] key
```

```{option} -h, --help
Show the help message and exit.
```

```{option} key
The key to remove.
```


