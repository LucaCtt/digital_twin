# Smart Home Digital Twin

This repository contains the source code for the Smart Home Digital Twin,
developed for my MsC thesis in Computer Science and Engineering at the University of Brescia.

It provides a library for evaluating the energy consumption of a smart home, also evaluating "what-if" scenarios of the home's energy consumption. It also contains a REST API for interacting with the library, and a basic frontend for showcasing the APIs capabilities.

## Requirements

- Python 3.9 or higher
- (Optional) [Poetry](https://python-poetry.org/) 1.7.0 or higher

## Installation and Usage

Install the dependencies listed in the `tool.poetry.dependencies` section of [`pyproject.toml`](./pyproject.toml).
It is recommended to use Poetry, in order to use the same versions of the dependencies used during development:

```bash
poetry install
```

This is all that is needed to use the code as a library. Refer to the [Packages](#packages) section for more information about the provided packages. A CLI script is also provided, which can be used to run the library's functionalities from the command line. To use it, run:

```bash
poetry run dt
```

if using Poetry, or:

```bash
python -m dt
```

otherwise.

The CLI supports the following commands:
- `map`: shows a map of appliances modes during the day, given the appliances and routines contained in the `dt/json` directory.
- `api`: start the REST API server in development mode. Not suitable for production—read [Deployment](#deployment) for information on how to deploy the api.
- `web`: start the frontend server. Again, not suitable for production.

## Packages

The repository contains a package `dt`, which in turn contains the following subpackages:
- `plots`: 


## Deployment


## Contributing

## License

MIT License. See [`LICENSE`](./LICENSE) for more information.

## Author

Luca Cotti <lucacotti98@gmail.com>