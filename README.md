# tunefind2spotify

Create Spotify playlists for your favorite movies, shows and games with data
gathered on Tunefind.

<div id="badges" align="left">
  <a href="https://github.com/benediktholmes/tunefind2spotify/actions/workflows/unittests.yml">
    <img src=https://github.com/benediktholmes/tunefind2spotify/actions/workflows/unittests.yml/badge.svg>
  </a>
</div>


[Tunefind](https://tunefind.com)
is a platform that enables public collaborative collection of music appearing in
movies, games and shows bundled with an extensive amount of auxiliary
information, for instance a reference to the respective URI on Spotify for each
track.

As Tunefind is missing the *"BIG-EXPORT-BUTTON"* for complete media
collections, the intention of this project is to fill this use case gap for
personal use.

## Legal Disclaimer

***As Tunefind currently
[does not offer a suitable public API](https://www.tunefind.com/product/api)
to be used by this project, the application resorts to collecting (only) the
relevant data via an undocumented API.***

***While the code is licensed under [GNU AGPLv3](LICENSE.md),
it remains the user's sole responsibility to inform her/himself about Tunefind's
current [terms-of-service](https://www.tunefind.com/tos)
with regard to the legality and terms of both website scraping and data storage
before running the application.***

## Usage
From the project root, first install requirements, then invoke the help page of
the application:

```shell script
pip install -e .
tunefind2spotify --help
```

## Development

Make sure to install all requirements:
```shell script
pip install -e .[doc,dev]
```

### Documentation

Latest documentation is available
[here](https://benediktholmes.github.io/tunefind2spotify).
(Re-)create documentation by running:

```shell script
cd docs
mkdir build/
sphinx-apidoc -fePM -d -1 -o source/ ../tunefind2spotify/
make html
```

### Testing

Linting is configured for flake:

```shell script
flake8
```

Run Unittests with tox via:

```shell script
pip install tox
tox
```

You can alternatively just invoke tests with:
```shell script
pytest -s  # flag s ensures debug prints in test code are shown on stdout
```