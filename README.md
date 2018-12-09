# udacity_fsnd_project2
Repository for Project 2 of the Full Stack Web Developer course

This project contains two primary Python3 files, a sqlite database, and a set of HTML and CSS files to render the website for this recipe book.

## Python Files:

* application.py: the primary application which operates a webserver to serve the application
* database_setup.py: this initializes the database models necessary for communicating with the database

### Python Dependencies:

* python3
* sqlalchemy
* flask
* functools
* requests
* [google-auth](https://google-auth.readthedocs.io/en/latest/)

### System Dependencies:

* sqlite3
* python3
* Open port 8000

## Usage:

If python3 is part of your PATH then you can execute application.py directly from its containing directory via `./application.py`. Otherwise you must invoke python3 at the command prompt, e.g. `python3 application.py`.

## Design:
### Basic Design:
This application operates a web server which renders a catalog of recipes sorted into various categories. The website allows users to authenticate via Google or GitHub. Once a user is authenticated they have the option to add, update, or remove categories and recipes.

### API
This application also serves two JSON endpoints:
* `/recipe/<id>/JSON`: displays a single recipe of id <id>
* `/category/<id>/JSON`: displays all recipes grouped by category
