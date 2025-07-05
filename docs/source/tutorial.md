# Tutorial

**slash** is designed for users who needs to deploy a proxy service but has to visit a remote server without visual interface. It provides a convenient way to create, manage, and use web environments on remote servers, which is similar to `conda` but more lightweight.

## Quick Start

Before you start, you need a subscription link. If you don't have one, you can use the default subscription link: `https://raw.githubusercontent.com/Pawdroid/Free-servers/main/sub`.

Now, let us create an environment using the subscription link.

```bash
# Create a new environment with a subscription
# -n is the name of the environment, whatever you like
# -f is the subscription link
slash create -n myenv -f <your_subscription>
```

This is may take a while, depending on the Internet speed. After the environment is created, try to run a command with the newly created environment. Just add the prefix `slash run -n myenv` before the command. For example, you can run `wget huggingface.co` with the new environment by executing the following command.

```bash
slash run -n myenv wget huggingface.co
```

You should be able to execute the command with the new environment.

## Advanced Usage

As users we may not want to add the prefix `slash run -n myenv` every time we run a command. We can activate and deactivate the environment to make it easier.

Before doing that, we need to init the environment first. Run

```bash
slash init
```

This is very similar when you are installing `conda`. It will write some configurations to your `.bashrc` file so that next time you open a terminal, the environment is ready.

:::{note}
You need to run `slash init` only once. However, you have to run it to make `slash activate` and `slash deactivate` work.
:::

Then open a new terminal. Now you can activate the environment by running

```bash
slash activate myenv
```

If successful, you should see some information about the environment, with links to the web monitor of the established service. You may choose the proxy service you want to use through the web monitor.

You should also be able to see a prompt like `/myenv\ $` in the terminal. Now any command you run will be executed with the environment.

To deactivate the environment, simply run

```bash
slash deactivate
```

## Common Commands

Here are some common commands you may use.

### List all environments

To list all environments, run

```bash
slash env list
```

:::{note}
There is a built-in environment called `base`, which is a mirror of the Internet on this machine. Useful if you need to forward it to the compute nodes on slurm.
:::

### Remove the environment

To remove an environment, for example, `myenv`, run

```bash
slash remove myenv
```

## FAQ

> My server does not have direct access to the Internet. We use a proxy server to access the Internet and the administrator asks us to use `http_proxy` and `https_proxy` environment variables. How can I use **slash**?

You can config `slash` to redirect the traffic to the proxy server. Please try the following steps:

1. Examinate the proxy server address and port. Run the following command to get the address and port.

    ```bash
    echo $http_proxy
    ```

    The output should be something like `http://proxy.example.com:8080` or `http://172.32.45.1:42134`. Then we know that the proxy server is `proxy.example.com` and the port is `8080`, or the proxy server is `172.32.45.1` and the port is `42134`.

2. Run the following command to config `slash` to use the proxy server. Say the proxy server is `proxy.example.com` and the port is `8080`.

    ```bash
    slash config set http_server proxy.example.com
    slash config set http_port 8080
    ```

3. Now you can create an environment and run commands with the environment. The traffic will be redirected to the proxy server.

> I forget to deactivate the environment before I close the terminal. I am afraid that the service is still running. What should I do?

Don't worry. `slash` implements a daemon to monitor the environment. If you forget to deactivate the environment, the daemon will stop the service after a while. If no service is running, the daemon will also exit automatically.
