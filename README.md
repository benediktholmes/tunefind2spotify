# tunefind2spotify

## Usage
Install requirements, then invoke the help page of the application:

```shell script
pip install -r requirements.txt
tunefind2spotify --help
```

## Development

Make sure to install all requirements:
```shell script
pip install -r requirements.txt -r dev_requirements.txt
```

### Documentation

Latest documentation is available at [???](). (Re-)create documentation by
running:

```shell script
cd docs
mkdir build/
sphinx-apidoc -fePM -d -1 -o source/ ../tunefind2spotify/
make html
```

### Testing

Run Unittests with coverage via:

```shell script
coverage run && coverage report
```

You can alternatively just invoke tests with
```shell script
pytest -s  # flag s ensures debug prints in test code are shown on stdout
```