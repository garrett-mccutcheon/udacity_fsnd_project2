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
@app.route('/categories')
def Test():
    session = Session()
    categories = ''
    for category in session.query(Category).order_by(Category.name).all():
        categories += '<a href=\'/category/{}\'>{}</a>'.format(category.id,
                                                               category.name)
        categories += '</br>'
    return categories


@app.route('/category/<id>')
def CatoricalRecipeList(id):
    session = Session()
    recipes = ''
    for recipe in session.query(Recipe).filter(Recipe.category_id == id).all():
        recipes += '<a href=\'/recipes/{}\'>{}</a>'.format(recipe.id,
                                                           recipe.name)
        recipes += '</br>'
    return recipes


@app.route('/category/new')
def NewCategory():
    # TODO
    return 'page for category creation'


@app.route('/category/update_<id>')
def UpdateCategory(id):
    # TODO
    return 'page for category updates'


@app.route('/category/delete_<id>')
def DeleteCategory(id):
    # TODO
    return 'page for category deletion'


@app.route('/recipes')
def RecipeList():
    session = Session()
    recipes = ''
    for recipe in session.query(Recipe).all():
        recipes += '<a href=\'/recipe/{}\'>{}</a>'.format(recipe.id,
                                                          recipe.name)
        recipes += '</br>'
    return recipes


@app.route('/recipe/<id>')
def ShowRecipe(id):
    session = Session()
    recipe = session.query(Recipe).filter(Recipe.id == id).one()
    output = '{}</br></br>{}'.format(recipe.name, recipe.instructions)
    return output


@app.route('/recipe/new')
def NewRecipe():
    # TODO
    return 'page for recipe creation'


@app.route('/recipe/update_<id>')
def UpdateRecipe(id):
    # TODO
    return 'page for recipe updates'


@app.route('/recipe/delete_<id>')
def DeleteRecipe(id):
    # TODO
    return 'page for recipe deletion'


if __name__ == '__main__':
    # TODO: remove debug mode
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
