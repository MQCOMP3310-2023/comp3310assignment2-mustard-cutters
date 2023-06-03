from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_user, login_required, logout_user
from sqlalchemy import text, asc
from .models import User
from . import db
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return render_template('login.html')

#admin tools
@auth.route('/admintools')
@login_required
def adminTools():
    user = db.session.query(User).order_by(asc(User.name))
    return render_template('admintools.html', user = user)

#Edit user details
@auth.route('/admintools/<int:user_id>/edit/', methods = ['GET', 'POST'])
def editUser(user_id):
    editedUser = db.session.query(User).filter_by(id = user_id).first()
    if request.method == 'POST':
        if request.form['email']:
            editedUser.email = request.form['email']
        if request.form['name']:
            editedUser.name = request.form['name']
        if request.form['password']:
            new_password = request.form['password']
            editedUser.password = generate_password_hash(new_password, method='sha256')
        if request.form['role']:
            editedUser.role = request.form['role']
        db.session.add(editedUser)
        db.session.commit() 
        flash('User Details Successfully Updated')
        return redirect(url_for('auth.adminTools', User=User, user_id = user_id))
    else:
        return render_template('edituser.html', User=User, user = editedUser)

#delete user
@auth.route('/admintools/<int:user_id>/delete/', methods = ['GET', 'POST'])
def deleteUser(user_id):
    userToDelete = db.session.query(User).filter_by(id = user_id).first()
    if request.method == 'POST':
        db.session.delete(userToDelete)
        db.session.commit()
        flash('User Successfully Deleted')
        return redirect(url_for('auth.adminTools', User=User, user_id = user_id))
    else:
        return render_template('deleteuser.html', User=User, user = userToDelete)

@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()

    # check if the user actually exists
    # take the user-supplied password and compare it with the stored password
    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        current_app.logger.warning("User login failed")
        return redirect(url_for('auth.login')) # if the user doesn't exist or password is wrong, reload the page

    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    return redirect(url_for('main.showRestaurants', owner_id = user.id))
                    
                    

@auth.route('/signup')
def signup():
    return render_template('signup.html', User=User)

@auth.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first()
    if user: 
        flash('Email address already exists')  # 'flash' function stores a message accessible in the template code.
        current_app.logger.debug("User email already exists")
        return redirect(url_for('auth.signup'))

    new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'), role='public_user')

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('auth.login'))

@auth.route('/logout')
@login_required
def logout():
    logout_user();
    return redirect(url_for('main.publicShowRestaurants'))