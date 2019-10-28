from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, make_response
from flask import session as login_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_setup import Base
from db_setup import Category
from db_setup import Item
from db_setup import User
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import random
import string
import httplib2
import json
import requests
import chardet

app = Flask(__name__)

# Google client_id
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Movie Genre App"



engine = create_engine('sqlite:///movies.db',
                       connect_args={'check_same_thread': False})
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Anti-forgery state token.

@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


# GConnect

@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads((h.request(url, 'GET')[1]).decode())
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps
                                 ('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 100px; height: 100px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    return output
    # User Helper Functions

def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

@app.route('/gdisconnect')
def gdisconnect():
        # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        # Reset the user's sesson.
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        # response = make_response(
        # json.dumps('Successfully disconnected.'), 200)
        # response.headers['Content-Type'] = 'application/json'
        response = redirect(url_for('showcategories'))
        flash("Successfully Disconnected.")
        return response
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# API Endpoints

@app.route('/category/JSON')
def categoriesJSON():
    categories = session.query(Category).all()
    return jsonify(GenreCategories=[i.serialize for i in categories])

@app.route('/category/<int:category_id>/movies/JSON')
def genreitemJSON(category_id):
    category = session.query(Category).filter_by(
    id=category_id).one()
    items = session.query(Item).filter_by(category_id=category_id).all()
    return jsonify(GenreItems=[i.serialize for i in items])

@app.route('/category/<int:category_id>/movies/<int:item_id>/JSON')
def menuItemJSON(category_id, item_id):
    menuItem = session.query(Item).filter_by(id=item_id).one()
    return jsonify(GenreItem=menuItem.serialize)



# View all the Genres


@app.route('/')
@app.route('/category')
def showcategories():
    categories = session.query(Category).all()
    return render_template('showcategories.html', categories=categories)

# New Genre


@app.route('/category/new', methods=['GET', 'POST'])
def newcategory():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newcategory = Category(name=request.form['name'])
        session.add(newcategory)
        flash('%s Successfully Created' % newcategory.name)
        session.commit()
        return redirect(url_for('showcategories'))
    else:
        return render_template('newcategory.html')

# Delete Genre


@app.route('/category/<int:category_id>/delete',
           methods=['GET', 'POST'])
def deletecategory(category_id):
    categorytodelete = session.query(Category).filter_by(id=category_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if categorytodelete.user_id != login_session['user_id']:
        return "<script>{alert('Unauthorized');}</script>"
    if request.method == 'POST':
        session.delete(categorytodelete)
        flash('%s Successfully Deleted' % categorytodelete.name)
        session.commit()
        return redirect(url_for('showcategories'))
    else:
        return render_template('deletecategory.html',category=categorytodelete)
# Edit Genre


@app.route('/category/<int:category_id>/edit',
           methods=['GET', 'POST'])
def editcategory(category_id):
    categorytoedit = session.query(Category).filter_by(id=category_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if categorytoedit.user_id != login_session['user_id']:
        return "<script>{alert('Unauthorized');}</script>"
    if request.method == 'POST':
        if request.form['name']:
            categorytoedit.name = request.form['name']
            flash('%s Successfully edited' % categorytoedit.name)
            return redirect(url_for('showcategories'))
    else:
        return render_template('editcategory.html', category=categorytoedit)

# Show Genre Item


@app.route('/category/<int:category_id>/')
@app.route('/category/<int:category_id>/movies/')
def categorygenre(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(
        Item).filter_by(category_id=category_id).all()
    return render_template('items.html', category=category, items=items)

# Create new genre item


@app.route(
    '/category/<int:category_id>/movies/new/', methods=['GET', 'POST'])
def newgenreitem(category_id):
    if request.method == 'POST':
        newItem = Item(title=request.form['title'],
                       description=request.form['description'],
                       category_id=category_id)
        session.add(newItem)
        session.commit()
        flash("Menu Item has been added")
        return redirect(url_for('categorygenre', category_id=category_id))
    else:
        return render_template('newitem.html', category_id=category_id)

# Edit genre item


@app.route('/category/<int:category_id>/<int:item_id>/edit/',
           methods=['GET', 'POST'])
def editgenreitem(category_id, item_id):
    editedItem = session.query(Item).filter_by(id=item_id).one()
    if request.method == 'POST':
        if request.form['title']:
            editedItem.title = request.form['title']
        if request.form['description']:
            editedItem.description = request.form['description']
        session.add(editedItem)
        session.commit()
        flash("Menu Item has been edited")

        return redirect(url_for('categorygenre', category_id=category_id))
    else:
        return render_template(
            'editgenreitem.html', category_id=category_id,
            item_id=item_id, item=editedItem)


@app.route('/category/<int:category_id>/<int:item_id>/delete/',
           methods=['GET', 'POST'])
def deletegenreitem(category_id, item_id):
    itemtodelete = session.query(Item).filter_by(id=item_id).one()
    if request.method == 'POST':
        session.delete(itemtodelete)
        session.commit()
        flash("Menu Item has been deleted")
        return redirect(url_for('categorygenre', category_id=category_id))
    else:
        return render_template('deletegenreitem.html', item=itemtodelete)

# End of file


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)


