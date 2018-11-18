#!/usr/bin/env python3
from flask import Flask, render_template, request, redirect, url_for
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
def Home():
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
        recipes += '<a href=\'/recipe/{}\'>{}</a>'.format(recipe.id,
                                                          recipe.name)
        recipes += '</br>'
    return recipes


@app.route('/category/new', methods=['GET', 'POST'])
def NewCategory():
    session = Session()
    if request.method == 'POST':
        newCategory = Category(name=request.form['name'])
        session.add(newCategory)
        session.commit()
        return redirect(url_for('Home'))
    else:
        return render_template('newcategory.html')


@app.route('/category/update_<id>', methods=['GET', 'POST'])
def UpdateCategory(id):
    session = Session()
    categoryToUpdate = session.query(Category).filter(
        Category.id == id).one()
    if request.method == 'POST':
        categoryToUpdate.name = request.form['name']
        session.add(categoryToUpdate)
        session.commit()
        return redirect(url_for('Home'))
    else:
        return render_template('updatecategory.html',
                               name=categoryToUpdate.name,
                               id=id)


@app.route('/category/delete_<id>', methods=['GET', 'POST'])
def DeleteCategory(id):
    session = Session()
    categoryToDelete = session.query(Category).filter(
        Category.id == id).one()
    if request.method == 'POST':
        session.delete(categoryToDelete)
        session.commit()
        return redirect(url_for('Home'))
    else:
        return render_template('deletecategory.html',
                               name=categoryToDelete.name,
                               id=id)


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


@app.route('/recipe/new', methods=['GET', 'POST'])
def NewRecipe():
    session = Session()
    if request.method == 'POST':
        newRecipe = Recipe(name=request.form['name'],
                           instructions=request.form['instructions'])
        session.add(newRecipe)
        session.commit()
        return redirect(url_for('ShowRecipe', id=newRecipe.id))
    else:
        return render_template('newrecipe.html')


@app.route('/recipe/update_<id>', methods=['GET', 'POST'])
def UpdateRecipe(id):
    session = Session()
    recipeToUpdate = session.query(Recipe).filter(
            Recipe.id == id).one()
    if request.method == 'POST':
        recipeToUpdate.name = request.form['name']
        recipeToUpdate.instructions = request.form['instructions']
        session.add(recipeToUpdate)
        session.commit()
        return redirect(url_for('ShowRecipe', id=id))
    else:
        return render_template('updaterecipe.html',
                               name=recipeToUpdate.name,
                               instructions=recipeToUpdate.instructions,
                               id=id)


@app.route('/recipe/delete_<id>', methods=['GET', 'POST'])
def DeleteRecipe(id):
    session = Session()
    recipeToDelete = session.query(Recipe).filter(
        Recipe.id == id).one()
    if request.method == 'POST':
        session.delete(recipeToDelete)
        session.commit()
        return redirect(url_for('Home'))
    else:
        return render_template('deleterecipe.html',
                               name=recipeToDelete.name,
                               id=id)


if __name__ == '__main__':
    # TODO: remove debug mode
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
