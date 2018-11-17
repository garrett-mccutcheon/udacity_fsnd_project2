#!/usr/bin/env python3
from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Recipe, Category

app = Flask(__name__)
engine = create_engine('sqlite:///recipe_book.db')
Session = sessionmaker(bind=engine)


@app.route('/hello')
def HelloWorld():
    return "Hello World"


@app.route('/')
def Test():
    session = Session()
    recipe = session.query(Recipe).first()
    return recipe


if __name__ == '__main__':
    # TODO: remove debug mode
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
