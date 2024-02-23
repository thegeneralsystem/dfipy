# Generating Documentation

- Steps here taken from [Sphinx Setup for autodoc](https://gist.github.com/GLMeece/222624fc495caf6f3c010a8e26577d31)
- [readthedocs](https://docs.readthedocs.io/en/stable/intro/getting-started-with-sphinx.html)

Install the docs requirements

```bash
poetry install --with docs
```

## Generate docs

from within the `docs` directory run the following to create an html build.

```bash
make html
```

### Hot reloading

The following command will generate HTML docs and open in default browser. Changes to docs will hot reload. Run from project root.

```bash
sphinx-autobuild docs/source/ docs/_build/html
```

## Clean up the build

```bash
make clean
```

## Run DocTests

Will test code executes in docs.

```bash
make doctest
```

## Writing the Docs

- We use the [PyData Sphinx Theme](https://pydata-sphinx-theme.readthedocs.io/en/stable/), which has a number of components and examples.
- We use `myst` to allow docs to be markdown files rather than `rst`
  - [MyST Docs](https://myst-parser.readthedocs.io/en/latest/intro.html)
  - [myst-parser](https://www.sphinx-doc.org/en/master/usage/markdown.html)
  - [sphinx-autodoc2](https://sphinx-autodoc2.readthedocs.io/en/latest/quickstart.html#)
