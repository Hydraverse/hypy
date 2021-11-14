# Hydra Chain Integration & Tools Library [PREVIEW]

This is a Python support library for the Hydra Chain project (https://hydrachain.org) aimed at simplifying the process of using and developing apps for the blockchain.

Primarily, `hypy` (pronounced "hippie") currently provides:
- RPC tools to access the Hydra JSON-RPC service.
- A flexible command line tool with simple integration.
- Application infrastructure to extend apps & tools.

# Quick Start

If you know what this is and just want to get going, install:

`$ pip install git+https://github.com/hydraverse/hypy`

And then run!

`$ hy --help`

Full download/install and usage instructions follow.

# Clone & Install

This is both a library that you can import into your Python code and a command line tool that you can use and extend.

When installing `hypy`, the command line tools become available as well.

To install without cloning the repository,  jump down to the [Remote Installation](#Remote-Installation) section.

Starting with v0.1-final, a pip-installable `.whl` will be available as a release for each `release` tag. 

### **(Note: 'λ' is the command shell prompt in all following command examples)**

### Clone/Download Sources:

```text
λ git clone https://github.com/hydraverse/hypy

Cloning into 'hypy'...
...
```

Cloning via ssh is possible as well, removing the need to repeatedly enter credentials.

Add your SSH public key to GitHub and make sure to have the following contents in `~/.ssh/config`:

```text
Host github.com
        User git
```

You can then clone this or any other repo easily:

`λ git clone ssh://github.com/hydraverse/hypy`

### Environment

The simplest way to use `hypy` is to install it at the system level, but sometimes it can be hard to manage varying Python
version needs and dependencies.

If installing at the system level, jump down to the [Install Prerequisites](#Install-Prerequisites) section.

Otherwise, you can choose between `venv`, `Anaconda`, `pipenv` and many others;
however, `venv` is considered to be the supported environment for this library.

#### Virtualenv

In case you'd like to use/install `hypy` within a virtual environment, run
the following within the library's top folder:

```text
λ mkdir .env
λ python3 -m venv .env/hypy
...
λ source .env/hypy/bin/activate
(hypy) λ which python
/home/halo/.env/hypy/bin/python
(hypy) λ pip install --upgrade pip  # Ensure that pip is the newest version.
...
```
<!-- TODO: Add example output from `which python` etc -->

Requires the Debian/Ubuntu packages `python3-distutils` and `python3-virtualenv`.

#### Anaconda

[Installing Conda on Linux](https://docs.conda.io/projects/conda/en/latest/user-guide/install/linux.html#install-linux-silent)
summary:

```text

λ wget https://repo.anaconda.com/archive/Anaconda3-2021.05-Linux-x86_64.sh

λ chmod +x Anaconda*.sh

λ ./Anaconda*.sh
```

##### Create & Activate Anaconda Environment:

```text
λ conda create -n hypy python=3.8.10

λ conda activate hypy
```
<!-- TODO: Add example output from `which python` etc -->

## Install Prerequisites:  

First, check your python and pip versions: both should be 3.8+.

```text
(hypy) λ pip --version; python --version

pip 20.0.2 from /home/halo/pr/hy/hypy/.env/hypy/lib/python3.8/site-packages/pip (python 3.8)
Python 3.8.10
```

If you get an error that says `Command 'python' not found` (e.g. with default Ubuntu 20.04.3 LTS `python3` installs), it can be fixed by installing the `python-is-python3` package:

`(hypy) λ sudo apt install -y python-is-python3`

### Prerequisites from `requirements.txt`:

`(hypy) λ pip install -r requirements.txt`

**Mac:** Must specify HTTP proxy manually when needed, add the following parameter: `--proxy='https://user:pass@proxy.example.com:911'`


At this point, prior to installation you can optionally run the tests to validate your environment:

`(hypy) λ ./hy test -`

More details on unit testing below.

# Install

If you prefer, you can use the main library tool, `hy`, without installing by running `./hy` within
the library folder. Otherwise, you can install from a cloned copy of this repository or directly from the remote URL.

### From Source

Installing from the cloned `hypy` library folder:

`λ pip install .`

Use `sudo -H` when installing at the system level, otherwise don't forget to make sure that your environment activated.

### Remote Installation <a name="Remote-Installation"></a>

Installing directly from GitHub:

`λ pip install git+https://github.com/hydraverse/hypy`

Or to get a specific branch, tag, or revision:

`λ pip install git+https://github.com/hydraverse/hypy@v0.2-final`

This example installs the `v0.2-final` tagged version.

### Uninstall

`λ pip uninstall hypy`

### Packaging

You can create a redistributable wheel package for later installation with the following command:

`λ pip wheel .`

The resulting `hypy-N.N-py3-none-any.whl` file can be `pip install`-ed.
Don't attempt to change the file name, `pip` will complain.

You can also create wheels directly from repository URLs using the same URL format as you would for installation.

# Use: `hy`

`hy` is the *Hydra Chain Tool*, a command-line toolkit meant to run standalone modules, aka `apps`, with convenient access to instantiated library objects.

Some apps are provided by the library, and the `hy` module provides you with a means to
integrate your own apps and run them as if they were part of the tool. More on that in the example app below.

Running an app on the command line looks something like this **(note: 'λ' is the command shell prompt)**:

```text
λ hy [-h] <some-app> [-h] [options] [app params]
```

Use the `-h` option *before* the app name to see a list of apps, and after to get usage for a particular app.

The primary apps currently available are `cli`, `rpc`, and `test`. These are provided as system-level
commands alongside `hy` when you install `hypy`.

This means that instead of calling `hy cli ...`, for example, you can use `hy-cli ...` instead.

Note that all program options (except `-h` or `-v`) must appear *after* the app name.

# Run Unit Tests

In the top level project folder:

`./hy test - [-k "<test_name_pattern> or <test_name_pattern> ..."]`

This command is also available globally (with slight variation, no need for `-` param) after installation as `hy-test`.

You can also specify different parameters for the tests with environment variables, such as `HYPY_LOG`.
These variables also work with `hy`.

```test
(.env.test) halo@blade:hypy ֍ HYPY_LOG=ERROR ./hy test -
================================================ test session starts ================================================
platform linux -- Python 3.8.10, pytest-6.2.5, py-1.11.0, pluggy-1.0.0 -- /home/halo/pr/hy/hypy/.env.test/bin/python3
rootdir: /home/halo/pr/hy/hypy
collected 3 items                                                                                                   

hydra/test/app/cli.py::HydraCLIAppTest::test_app_cli_runnable PASSED                                          [ 33%]
hydra/test/app/rpc.py::HydraRPCAppTest::test_app_rpc_runnable PASSED                                          [ 66%]
hydra/test/rpc.py::HydraRPCTest::test_rpc_stub PASSED                                                         [100%]

================================================= 3 passed in 0.01s =================================================
```

### Standalone Testing

When developing ouside the library, tests can be run for standalone Application implementations.

`hy-test examples/my_hydra_app.py`

<!--
See `examples/aapp.py` to learn how to run `hy` commands directly as tests.
-->

<!--
# Full Usage: `hy`

### `hy`

```text
λ ./hy -h

usage: hy [-h] METH ...

Hydra Chain Tool.

```

### `cli`

```text
λ ./hy cli -h

usage: hy cli ...
```

Only the last section in an app's help message (`cli` in the above case) will differ
between apps.

### Apps with Parameters

These are snips of the usage block and parameter descriptions for apps containing any
special parameters.

### `blend`

```text
λ hy blend -h

usage: hy ...

```

### `echo`

```text
λ hy echo -h

...
echo:
  print text

  --all                 show as much information as possible.
```

-->
