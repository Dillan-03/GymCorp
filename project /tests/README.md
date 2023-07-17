# How to run tests

## Linux/Mac OS:

### Testing environment:

```
python3 -m venv sep_linux
source sep/bin/activate
pip3 install -r requirements.txt
```
<br>

### Playwright installation:

```
playwright install
playwright install-deps
```
<br>

### Run tests:

```
pytest
```

## Windows:

To run the tests on windows, you must have a linux subsystem:

- Install Ubuntu from the Windows Store (WSL)
- Once in ubuntu, navigate to the repo folder which is located in `/mnt`
- Check that your python version is at least `3.10.6`
    - ```python3 --version```
- Use the linux guide above from there on

<br>

# How to generate tests

Playwright comes with an feature where you can record yourself going through the interaction of the website and generate tests automatically.
<br>

- Run the flask app
    - `flask run --port=5001`
- Use the native system command line in another window (not WSL) and run the code generator
    - ```playwright codegen 127.0.0.1:5001```
<br>

# Pytest information

## Fixtures scope:

- Run once per test function (default scope)
    - `function`
- Run once per test class
    - `class`

- Run once per test file
    - `module`
- Run once per call to pytest
    - `session`

## How to run pytest:

- Basic running of the code 
    - `python -m pytest` 
- Shows the fixtures running
    - `python -m pytest --setup-show`
- Shows the prints in the test scripts after they have all completed
    - `python -m pytest -rP`
- Shows the print statement at each test script
    - `python -m pytest -s`