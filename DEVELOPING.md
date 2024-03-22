# Guide for developers

Tooling choices are based on these two principles:

- **Reproducibility:** pinning dependency tree and environment specifications
- **Maintainability:** linting, testing, releasing

## Reproducibility

### Requirements management

- `dfi` python library is managed by [poetry](https://python-poetry.org/).
- To contribute to its development you have to have [poetry installed](https://python-poetry.org/docs/#installation) on your operative system.
- Poetry automatically adds and removes requirements from the `pyproject.toml`. There are two groups of dependencies, the main group, with the libraries required for the basic functionalities, and the development group, for the libraries required for the development functionalites.
- To add a new library to the main requirements:

  ```bash
  poetry add <library name>[@<version>]
  ```

- To add a new library to the dev requirements:

  ```bash
  poetry add --group=dev <library name>[@<version>]
  ```

- To remove it, simply replace `add` with `remove`.
- Poetry will add the library to the correct list under `pyproject.toml` and will re-create the `poetry.lock` file, that contains the [dependency tree](https://ongchinhwee.me/python-dependency-management/) of the requirements.

### Environment management

- Poetry can also manage your python environment. If you prefer to use virtualenv or conda instead there will be no conflicts with poetry.
- You can create a virtualenv or a conda env, and then install the library in development mode with `pip install -e .` or with `pip install -e .["dev"]` to add the development libraries.
- If you want to use poetry, install the libraries (in development mode) simply with:

  ```bash
  poetry install
  ```

  By default all the dependency groups are installed. To add or exclude some, use the flags `--with=WITH` or `--without=WITHOUT`. Multiple values are allowed.

- To keep dependencies up to date:

  ```bash
  make lock
  ```

## Maintainability

- To run the **linter**:

  ```bash
  make lint
  ```

- To **reformat** the code:

  ```bash
  make reformat
  ```

- To run the **tests**:

  ```bash
  make test
  ```

- To run the **integration tests**, see instructions in `integration_tests/README.md`:

### Starting the Container

To start the docker container for development and running integration tests, the path to the users `.aws` config directory needs to be passed in as a variable:

```
make dev AWS_PATH=/Users/<user>
```

## How to release

The release process is based on pushing a git tag and fully managed by gitlab:

1. Create a new branch called `<JiraTicketNumber>-release-vX.Y.Z` , where `vX.Y.Z` is the release number that must follow the [semantic versioning](https://semver.org/).

   ```bash
   git checkout -b <TicketNumber>-release-vX.Y.Z
   ```

2. Update the `CHANGELOG.md`. _Do not make any other changes - this branch is for release only!_

3. Commit the changes to branch

   ```bash
    git commit -am "Release vX.Y.Z"
   ```

4. Push the branch to remote.

   ```bash
    git push origin <TicketNumber>-release-vX.Y.Z
   ```

5. Once the CI/CD has successfully run and it is approved, merged it to master branch.

   ```bash
    git checkout master
    git pull
   ```

6. From the up to date master, create a git tag, tagged with `vX.Y.Z` (note the prepended **v**) and with message `release vX.Y.Z`.

   ```bash
   git tag -a vX.Y.Z -m "Release X.Y.Z"
   ```

7. Push the tag with `git push origin vX.Y.Z `.

   ```bash
   git push origin vX.Y.Z
   ```

8. To trigger the release go to the CI/CD steps on gitlab, from the master branch and click on the "play button".

## How to pre-release

You can pre-relese at any time, using the lasts step of the CI/CD, and manually pushing on the "play" button. These releases will appear on artifactory as `X.Y.Z.dev5+23423dfea112` and can be used to share pre-releases across devs.
