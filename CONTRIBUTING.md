# Contributing

Thank you for your interest in contributing to Viper 2!

## Code style conventions

Please make sure to use 4-spaces tabs for indenting your code.

Please try to simplify your code as much as possible, and strive to make it the most readable. We do so for example by limiting nested blocks as much as possible, using explicit variable names (instead of single letters), and commenting where opportune.

We favor f-string formatting (e.g. `log.info(f"Logging some {information}")`) instead of the older format strings (e.g. `log.info("Logging some %s", information)`), including for logging events.

Before submitting any patches, please make sure you run your changes through `./scripts/lint.sh`. This script helps ensuring a cohesive code style and simplifies the process of uniforming it. In order to run it you will be required to install `autoflake`, `black` and `isort` from pip. If you have a `venv` virtualenv directory in the root directory of the repository, the script will automatically look for those utilities there.
