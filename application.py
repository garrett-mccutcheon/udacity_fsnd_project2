#!/usr/bin/env python3
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask import session as login_session
from flask import flash
from flask import abort
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Recipe, Category
from google.oauth2 import id_token
from google.auth.transport import requests
from functools import wraps
import requests as http_requests
import psycopg2

app = Flask(__name__)
app.secret_key = 'A'
engine = create_engine('postgresql+psycopg2://postgres:@/catalog', echo=True)
Session = sessionmaker(bind=engine)

# OAuth variables
GOOGLE_CLIENT_ID = "1007442557157-gf75qaqfmn96vi5t27gk5pn7vd912oeh.apps.googleusercontent.com"
GITHUB_CLIENT_ID = "ed4b8c9715caa0b691c8"
GITHUB_CLIENT_SECRET = "39cb00634773a3e774c9bd2d9316d5574c1ec80b"


def serializeRecipe(self):
    """Serializes recipe information

    Returs a recipe as a serialized dict making it easier to present a series
    of recipes in a list. This is mostly useful when returing JSON.

    Returns:
        A dict of the key elements of a recipe.
    """
    return {
        'id': self.id,
        'name': self.name,
        'instructions': self.instructions
    }


def login_required(secure_page):
    """Checks if a user is logged in an routes them appropriately

    This method protects resources by requiring that a user be signed in to
    access that resource. This uses the login_session to determine if a userid
    is present in the session. If no userid is present then a user is not
    logged in and should be routed to the login page. Otherwise, there is an
    active user session and the user should be allowed to access the protected
    resource.

    Args:
        secure_page: the page which should be secured (aka requires login)

    Returns:
        If a user is logged in this returns the page the user requested.
        If a user is NOT logged in this returns a redirect to the login page.
    """
    @wraps(secure_page)
    def wrapper(*args, **kwargs):
        userid = login_session.get('userid')
        if userid:
            return secure_page(*args, **kwargs)
        else:
            flash("Please login to view this page.")
            source = request.path
            app.logger.debug(source)
            return redirect(url_for('Login', source_url=source))
    return wrapper


@app.route('/hello')
def HelloWorld():
    return "Hello World"


@app.route('/')
@app.route('/categories')
def Home():
    session = Session()
    categories = session.query(Category).order_by(Category.name).all()
    return render_template('categories.html',
                           categories=categories)


@app.route('/category/<id>')
@app.route('/recipes')
def CategoricalRecipeList(id=None):
    session = Session()
    current_user = login_session.get('userid')
    if id:
        recipes = session.query(Recipe).filter(Recipe.category_id == id).all()
        category = session.query(Category).filter(Category.id == id).one()
        category_name = category.name
        category_author = category.author
        if current_user == category_author:
            owner = True
        else:
            owner = False
    else:
        recipes = session.query(Recipe).all()
        category_name = None
        owner = False
    return render_template('recipes.html',
                           recipes=recipes,
                           id=id,
                           category_name=category_name,
                           owner=owner)


@app.route('/category/<id>/JSON')
def CategoricalRecipeListJSON(id):
    session = Session()
    recipes = session.query(Recipe).filter(Recipe.category_id == id).all()
    return jsonify(recipes=[serializeRecipe(recipe) for recipe in recipes])


@app.route('/category/new', methods=['GET', 'POST'])
@login_required
def NewCategory():
    session = Session()
    if request.method == 'POST':
        newCategory = Category(name=request.form['name'],
                               author=login_session.get('userid'))
        session.add(newCategory)
        session.commit()
        return redirect(url_for('Home'))
    else:
        return render_template('newcategory.html')


@app.route('/category/update_<id>', methods=['GET', 'POST'])
@login_required
def UpdateCategory(id):
    session = Session()
    categoryToUpdate = session.query(Category).filter(
        Category.id == id).one()
    current_user = login_session.get('userid')
    if request.method == 'POST':
        if current_user == categoryToUpdate.author:
            categoryToUpdate.name = request.form['name']
            session.add(categoryToUpdate)
            session.commit()
            return redirect(url_for('Home'))
        else:
            return abort(403)
    else:
        if current_user == categoryToUpdate.author:
            return render_template('updatecategory.html',
                                   name=categoryToUpdate.name,
                                   id=id)
        else:
            return abort(403)


@app.route('/category/delete_<id>', methods=['GET', 'POST'])
@login_required
def DeleteCategory(id):
    session = Session()
    categoryToDelete = session.query(Category).filter(
        Category.id == id).one()
    current_user = login_session.get('userid')
    if request.method == 'POST':
        if current_user == categoryToDelete.author:
            session.delete(categoryToDelete)
            session.commit()
            return redirect(url_for('Home'))
        else:
            return abort(403)
    else:
        if current_user == categoryToDelete.author:
            return render_template('deletecategory.html',
                                   name=categoryToDelete.name,
                                   id=id)
        else:
            return abort(403)


@app.route('/recipes/JSON')
def RecipeListJSON():
    recipe_list = {}
    session = Session()
    categories = session.query(Category).all()
    for category in categories:
        recipes = (session.query(Recipe)
                   .filter(Recipe.category_id == category.id)
                   .all()
                   )
        recipe_list[category.id] = {'name': category.name,
                                    'recipes': ([serializeRecipe(recipe)
                                                for recipe in recipes])
                                    }
    return jsonify(recipe_list)


@app.route('/recipe/<id>')
def ShowRecipe(id):
    session = Session()
    recipe = session.query(Recipe).filter(Recipe.id == id).one()
    current_user = login_session.get('userid')
    if current_user == recipe.author:
        owner = True
    else:
        owner = False
    return render_template('recipe.html',
                           recipe=recipe,
                           owner=owner)


@app.route('/recipe/<id>/JSON')
def ShowRecipeJSON(id):
    session = Session()
    recipe = session.query(Recipe).filter(Recipe.id == id).one()
    return jsonify(id=recipe.id,
                   name=recipe.name,
                   instructions=recipe.instructions)


@app.route('/recipe/new', methods=['GET', 'POST'])
@login_required
def NewRecipe():
    session = Session()
    author = login_session.get('userid')
    if request.method == 'POST':
        newRecipe = Recipe(name=request.form['name'],
                           instructions=request.form['instructions'],
                           category_id=request.form['category'],
                           author=author)
        session.add(newRecipe)
        session.commit()
        return redirect(url_for('ShowRecipe', id=newRecipe.id))
    else:
        app.logger.debug('User logged in as {}'.format(login_session['userid']))
        categories = session.query(Category).all()
        return render_template('newrecipe.html', categories=categories)


@app.route('/recipe/update_<id>', methods=['GET', 'POST'])
@login_required
def UpdateRecipe(id):
    session = Session()
    recipeToUpdate = session.query(Recipe).filter(
            Recipe.id == id).one()
    current_user = login_session.get('userid')
    if request.method == 'POST':
        if current_user == recipeToUpdate.author:
            recipeToUpdate.name = request.form['name']
            recipeToUpdate.instructions = request.form['instructions']
            recipeToUpdate.category_id = request.form['category']
            session.add(recipeToUpdate)
            session.commit()
            return redirect(url_for('ShowRecipe', id=id))
        else:
            return abort(403)
    else:
        categories = session.query(Category).all()
        if current_user == recipeToUpdate.author:
            return render_template('updaterecipe.html',
                                   name=recipeToUpdate.name,
                                   instructions=recipeToUpdate.instructions,
                                   id=id,
                                   category=recipeToUpdate.category.name,
                                   categories=categories)
        else:
            return abort(403)


@app.route('/recipe/delete_<id>', methods=['GET', 'POST'])
@login_required
def DeleteRecipe(id):
    session = Session()
    recipeToDelete = session.query(Recipe).filter(
        Recipe.id == id).one()
    current_user = login_session.get('userid')
    if request.method == 'POST':
        if current_user == recipeToDelete.author:
            session.delete(recipeToDelete)
            session.commit()
            return redirect(url_for('Home'))
        else:
            return abort(403)
    else:
        if current_user == recipeToDelete.author:
            return render_template('deleterecipe.html',
                                   name=recipeToDelete.name,
                                   id=id)
        else:
            return abort(403)


@app.route('/login')
def Login():
    user_id = login_session.get('userid')
    app.logger.debug(user_id)
    if user_id:
        return render_template('login.html',
                               logged_in=True,
                               provider=login_session.get('provider'),
                               user=login_session.get('username'))
    else:
        source_url = request.args.get('source_url')
        app.logger.debug(source_url)
        return render_template('login.html',
                               logged_in=False,
                               source_url=source_url,
                               github_client_id=GITHUB_CLIENT_ID)


@app.route('/logout', methods=['POST'])
def Logout():
    if login_session.get('userid'):
        provider = login_session.get('provider')
        user = login_session.get('username')
        user_id = login_session.get('userid')
        app.logger.debug(login_session)
        login_session.pop('userid')
        flash("User {} @ {} logged out.".format(user, provider))
        return redirect(url_for('Login'))
    else:
        flash("No user was logged in, so logout is unnecessary.")
        return redirect(url_for('Login'))


@app.route('/googleoauth', methods=['POST'])
def GoogleOAuth():
    try:
        # Specify the CLIENT_ID of the app that accesses the backend:
        idinfo = (id_token.verify_oauth2_token(request.form['idtoken'],
                                               requests.Request(),
                                               GOOGLE_CLIENT_ID))

        if idinfo['iss'] not in ['accounts.google.com',
                                 'https://accounts.google.com']:
            return 'Wrong issuer.'

        # ID token is valid.
        # From here we can verify that the user is in the DB and create a
        # session for that user
        login_session['provider'] = 'Google'
        login_session['userid'] = idinfo['sub']
        login_session['username'] = idinfo['name']
        flash("You have successfully logged in via Google as {}"
              .format(idinfo['email']))
        return "{} id {}".format(idinfo['email'], login_session['userid'])
    except ValueError:
        # Invalid token
        return "Invalid Token"


@app.route('/githuboauth', methods=['GET', 'POST'])
def GithubOAuth():
    if request.args.get('code'):
        # Retrieve the code from the auth response
        user_oauth_code = request.args.get('code')

        """Generate a request to the GitHub auth portal using the code
        provided via the redirect_uri from GitHub's authentication flow. The
        POST request will return a JSON object containing the information
        from the User's profile.
        """
        request_url = 'https://github.com/login/oauth/access_token'
        bearer_token = {'client_id': GITHUB_CLIENT_ID,
                        'client_secret': GITHUB_CLIENT_SECRET,
                        'code': user_oauth_code
                        }
        header = {'Accept': 'application/json'}
        get_access_token = http_requests.post(request_url,
                                              bearer_token,
                                              headers=header)
        access_token = get_access_token.json()['access_token']
        userurl = ('https://api.github.com/user?access_token={}'
                   .format(access_token))
        get_user_data = http_requests.get(userurl)
        user_json = get_user_data.json()

        # Specify Github-specific token info
        login_session['provider'] = 'Github'
        login_session['userid'] = user_json['id']
        login_session['username'] = user_json['name']
        flash("You have successfully logged in via Github as {}"
              .format(user_json['name']))
        return redirect(url_for('Login'))
    else:
        flash("No authorization was provided. Try again.")
        return redirect(url_for('Login'))


if __name__ == '__main__':
    # TODO: remove debug mode
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
