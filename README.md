# Environment variables

Create an .env file in the repo folder to store secrets.

```bash
SECRET_KEY=<generate your own secret key>
# For manager login
MANAGER_EMAIL=admin@admin.com
MANAGER_PASSWORD=admin123
# For the sendgrid email implementation
MAIL_USERNAME=<email>
SENDGRID_API_KEY=
# For the twilio secrets (phone support)
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_SERVICE_SID=
```

This will be required for running the software, either using the below production Docker implementation or setting up a development environment with flask

# Docker setup (Production)

This requires no setup other than installing docker on your system. However, first you must setup up your environment variables file.

-  Swap port 5000 with any port you wish to run the container on

```
docker build --tag gymcorp .
```

```
docker run -d -p 5000:80 --env-file .env gymcorp
```

# How to run the app (Development)

-  Install Python 3.11.2
-  Add it to PATH

## Create virtual environment

Linux/Mac OS:

```
python -m venv sep
sep/bin/activate
```

Windows:

```
python -m venv sep
sep/Scripts/activate.bat
```

## Install the pip modules

```
pip install -r requirements.txt --upgrade
```

## Setup the database

As the migrations are already setup, you can start up the database easily

```
flask db upgrade
```

If the migrations is not setup, use the following commands

```
flask db init
```

```
flask db migrate -m "initial migration"
```

```
flask db upgrade
```

## Preload database data

To preload the facilities and activities information into the database, run the following command

All operations systems:

```
flask preload
```

## Run the flask app in development

```
flask run
```

To debug the application you can add a `--debug` flag at the end

# PyLint

Please ensure you run the following command to ensure that pylint keeps codestyle consistent.

```
pylint app
```

We recommend you add it to your VSCode. Guide to do so: https://stackoverflow.com/a/70115846

Additionally please install autopep8 on your vscode and machine. This will automatically format your code to the pylint standard

```
pip install autopep8
```

# Codespaces

[![Open in Codespaces](https://classroom.github.com/assets/launch-codespace-f4981d0f882b2a3f0472912d15f9806d57e124e0fc890972558857b51b24a6f9.svg)](https://classroom.github.com/open-in-codespaces?assignment_repo_id=10162060)
