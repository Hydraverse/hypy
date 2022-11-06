# [Hydra Chain Integration & Tools Library](https://pypi.org/project/hydra-chain-py/)

This is a Python support library for the Hydra Chain project (https://hydrachain.org) aimed at simplifying the process of using and developing apps for the blockchain.

Primarily, `hypy` (pronounced "hippie") currently provides:
- RPC tools to access the Hydra JSON-RPC service.
- A flexible command line tool with simple integration.
- Application infrastructure to extend apps & tools.
- Integrated apps for common tasks such as monitoring or connecting to new nodes.

# Quick Start

If you know what this is and just want to get going, install:

```commandline
pip install hydra-chain-py
```

Or with poetry:

```commandline
poetry add hydra-chain-py
```

This adds the `hydra` package to your Python installation. 

Then, to get started, run:

```commandline
hy --help
```

Full download/install and usage instructions follow.

# Usage

This library connects to a Hydra node on a local system or over a network.

The primary tool to interface with the node is called `hycli`, and for the most part behaves exactly the same as `hydra-cli`,
with some nicer output options:

```commandline
hycli getinfo
```
```shell
getinfo                
  .version             180506
  .protocolversion     70017
  .walletversion       169900
  .balance             28047.31917165
  .stake               1452.99760027
  .locked              
    .used              128
    .free              65408
    .total             65536
    .locked            65536
    .chunks_used       2
    .chunks_free       2
  .blocks              155763
  .timeoffset          0
  .connections         8
  .proxy               
  .difficulty          
    .proof-of-work     1.52587890625e-05
    .proof-of-stake    797825.1819042678
  .testnet             True
  .moneysupply         20931869.76468454
  .burnedcoins         73748.17511400
  .keypoololdest       1635530802
  .keypoolsize         2000
  .unlocked_until      1741407462
  .relayfee            0.004
  .errors 
```

There's also `hytop`, which periodically displays useful node status info in a human-readable format:

```commandline
hytop -C
```
```shell
now                           2022-01-05 16:21:36.930567-08:00
utcnow                        2022-01-06 00:21:36.930584
connectioncount               8
apr                           107.2079665372164

stakinginfo
  .enabled                    True
  .staking                    True
  .difficulty                 797825.1819042678
  .search-interval            1:51:28
  .weight                     28047.31917165
  .netstakeweight             3918664.173517
  .expectedtime               4:58:03

walletinfo
  .walletname                 ''
  .balance                    28047.31917165
  .stake                      1452.99760027
  .txcount                    2769
  .unlocked_until             2025-03-07 20:17:42
```

And `peerscan`, which attempts to connect to new nodes:

```commandline
peerscan -vv
```
```shell
INFO:hypy:server reports 327 connections
INFO:hypy:loaded 327 peers
INFO:hypy:loaded 1201 nodes
INFO:hypy:trying 883 potential new peers
INFO:hypy:server now reports 329 connections
```

# Clone & Install

This is both a library that you can import into your Python code and a command line tool that you can use and extend.

When installing `hypy`, the command line tools become available as well.

To install the latest from git without cloning the repository,  jump down to the [Remote Installation](#Remote-Installation) section.

### Clone/Download Sources:

```commandline
git clone https://github.com/hydraverse/hypy
```
```shell
Cloning into 'hypy'...
...
```

### Environment

The simplest way to use `hypy` is to install it at the system level, but sometimes it can be hard to manage varying Python
version needs and dependencies.

If installing at the system level, jump down to the [Installation](#Installing) section.

#### Poetry

This is now the only recommended/supported way to install or develop with this package.

Create a new poetry project:

```commandline
poetry new myproject && cd myproject && poetry add hydra-chain-py
```

# Installing

### From Source

Installing from the cloned `hypy` library folder:

```commandline
poetry install .
```

### Remote Installation <a name="Remote-Installation"></a>

Installing directly from GitHub:

```commandline
poetry add git+https://github.com/hydraverse/hypy
```

Or to get a specific branch, tag, or revision:

```commandline
poetry add git+https://github.com/hydraverse/hypy@v2.7.2
```

This example installs the `v2.7.2` tagged version.

### Uninstall

```commandline
pip uninstall hypy
```
Or
```commandline
poetry remove hydra-chain-py
```

### Packaging

You can create a redistributable wheel package for later installation with the following command:

```commandline
poetry build
```

# Use: `hy`

`hy` is the *Hydra Chain Tool*, a command-line toolkit meant to run standalone modules, aka `apps`, with convenient access to instantiated library objects.

Some apps are provided by the library, and the `hy` module provides you with a means to
integrate your own apps and run them as if they were part of the tool. More on that in the example app below.

Running an app on the command line looks something like this **(note: '֍' is the command shell prompt)**:

```commandline
hy [-h] <some-app> [-h] [options] [app params]
```

Use the `-h` option *before* the app name to see a list of apps, and after to get usage for a particular app.

The primary apps currently available are `cli` and `test`. These are provided as system-level
commands alongside `hy` when you install `hypy`.

This means that instead of calling `hy cli ...`, for example, you can use `hycli ...` instead.

Note that all program options (except `-h` or `-v`) must appear *after* the app name.

# Run Unit Tests

`hy test - [-k "<test_name_pattern> or <test_name_pattern> ..."]`

This command is also available globally (with slight variation, no need for `-` param) after installation as `hytest`.

You can also specify different parameters for the tests with environment variables, such as `HYPY_LOG`.
These variables also work with `hy`.

```commandline
HY_RPC_WALLET=watch HY_LOG=ERROR hy test -
```
```shell
=========================== test session starts ============================
platform linux -- Python 3.8.10, pytest-6.2.5, py-1.11.0, pluggy-1.0.0
rootdir: /home/halo/pr/hy/hypy
collected 13 items                                                         

hydra/test/app/cli.py::HydraCLIAppTest::test_app_cli_runnable PASSED [  7%]
hydra/test/rpc.py::HydraRPCTest::test_rpc_stub PASSED                [ 15%]
hydra/app/txvio.py::TxVIOAppTest::test_0_txvio_runnable PASSED       [ 23%]
hydra/app/txvio.py::TxVIOAppTest::test_1_txvio_run PASSED            [ 30%]
hydra/app/ascan.py::AScanAppTest::test_0_ascan_runnable PASSED       [ 38%]
hydra/app/ascan.py::AScanAppTest::test_1_ascan_run PASSED            [ 46%]
hydra/app/atrace.py::ATraceAppTest::test_0_atrace_runnable PASSED    [ 53%]
hydra/app/atrace.py::ATraceAppTest::test_1_atrace_run PASSED         [ 61%]
hydra/app/lstx.py::TxListAppTest::test_0_lstx_runnable PASSED        [ 69%]
hydra/app/lstx.py::TxListAppTest::test_1_lstx_run PASSED             [ 76%]
hydra/app/peerscan.py::PeerScanTest::test_0_peerscan_runnable PASSED [ 84%]
hydra/app/peerscan.py::PeerScanTest::test_1_peerscan_run PASSED      [ 92%]
hydra/app/top.py::TopAppTest::test_0_top_runnable PASSED             [100%]

=========================== 13 passed in 37.17s ============================
```

### Standalone Testing

When developing ouside the library, tests can be run for standalone Application implementations.

```commandline
hy-test examples/my_hydra_app.py
```

# Full Usage: `hy`

**NOTE:** Tab-completion is available via `argcomplete` but per-app parameters
won't be shown, only the primary `hy` parameters.

### `hy`

```commandline
hy -h
```
```shell
usage: hy [-h] [-v] [-l LOG] [--rpc RPC] [--rpc-wallet RPC_WALLET]
          [--rpc-testnet] [-J] [-j] [-f]
          {cli,test,ascan,atrace,lstx,txvio,peerscan,top} ...

HyPy Library Application Tool.

positional arguments:
  {cli,test,ascan,atrace,lstx,txvio,peerscan,top}
                        application to run.
  ARGS                  application args.

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         verbose level (up to 3x) (env: HYPY_V).
  -l LOG, --log LOG     log level (name: error,warning,info,debug,notset)
                        (env: HYPY_LOG).
  --rpc RPC             rpc url (env: HY_RPC)
  --rpc-wallet RPC_WALLET
                        rpc wallet name override (env: HY_RPC_WALLET)
  --rpc-testnet         rpc testnet override (env: HY_RPC_WALLET)
  -J, --json-pretty     output parseable json
  -j, --json            output parseable json
  -f, --full            output full names (non-json only)
```

### `cli`

```commandline
hycli -h
```
```shell
usage: hy cli ... [-f] ...

optional arguments:
  ...

cli:
  rpc cli interface

  -f, --full            output full names (non-json only)
  CALL                  rpc function to call
  PARAM                 rpc function parameters
```

Only the last section in an app's help message (`cli` in the above case) will differ
between apps.
