from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy import text, asc
from .models import User
from . import db
from werkzeug.security import generate_password_hash, check_password_hash

import re

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return render_template('login.html')

#admin tools
@auth.route('/admintools')
@login_required
def adminTools():
    user = db.session.query(User).filter_by(id=current_user.id).first()
    if user.role == "admin":
        user = db.session.query(User).order_by(asc(User.name))
        return render_template('admintools.html', user = user)

#Edit all user details
@auth.route('/admintools/<int:user_id>/edit/', methods = ['GET', 'POST'])
@login_required
def editUser(user_id):
    editedUser = db.session.query(User).filter_by(id = user_id).first()
    user = db.session.query(User).filter_by(id=current_user.id).first()
    if user.role == "admin":
        if request.method == 'POST':
            if request.form['role']:
                editedUser.role = request.form['role']
            db.session.add(editedUser)
            db.session.commit() 
            flash('User Details Successfully Updated')
            return redirect(url_for('auth.adminTools', User=User, user_id = user_id))
        else:
            return render_template('edituser.html', User=User, user = editedUser, user_id = user_id)

#Edit user details
@auth.route('/profile/<int:user_id>/edit/', methods = ['GET', 'POST'])
@login_required
def editDetails(user_id):
    editedUser = db.session.query(User).filter_by(id = user_id).first()
    if editedUser.id == current_user.id:
        if request.method == 'POST':

            if request.form['email']:
                new_email = request.form['email']
                user = User.query.filter_by(email=new_email).first()
                if user and user.id != user_id: 
                    flash('Email address already exists, please choose a new one', 'error') 
                    current_app.logger.debug("User email already exists")
                    return redirect(url_for('auth.editDetails', user_id = user_id)) 
                editedUser.email = request.form['email']

            if request.form['name']:
                editedUser.name = request.form['name']

            if request.form['old_password']:
                old_password = request.form['old_password']
                if not check_password_hash(editedUser.password, old_password):
                    flash('Old password incorrect, please try again.', 'error')
                    return redirect(url_for('auth.editDetails', user_id = user_id))  
                     
            if request.form['new_password']:
                password = request.form.get('new_password')
                if not request.form['old_password']:
                    flash('Old Password required', 'error')
                    return redirect(url_for('auth.editDetails', user_id = user_id))
                
                #Password Complexity
                #Ref - https://stackoverflow.com/questions/16709638/checking-the-strength-of-a-password-how-to-check-conditions
                if not re.search(r'[A-Z]', password) or not re.search(r'\d', password) or not re.search(r"[ !#$%&'()*+,-./[\\\]^_`{|}~"+r'"]', password) or len(password) < 8:
                    flash('Password Does NOT Meet Requirements', 'error')
                    return redirect(url_for('auth.editDetails', user_id = user_id))
                else:
                    new_password = request.form['new_password']
                    editedUser.password = generate_password_hash(new_password, method='sha256')

            db.session.commit() 
            flash('Account Details Successfully Updated', 'success')
            return redirect(url_for('main.profile', user_id = user_id))
        else:
            return render_template('editdetails.html', User=User, user = editedUser, user_id = user_id)

#delete user
@auth.route('/admintools/<int:user_id>/delete/', methods = ['GET', 'POST'])
@login_required
def deleteUser(user_id):
    userToDelete = db.session.query(User).filter_by(id = user_id).first()
    user = db.session.query(User).filter_by(id=current_user.id).first()
    if user.role == "admin":
        if request.method == 'POST':
            if userToDelete != current_user:
                db.session.delete(userToDelete)
                db.session.commit()
                flash('User Successfully Deleted')
                return redirect(url_for('auth.adminTools', User=User, user_id = user_id))
            else:
                db.session.delete(userToDelete)
                db.session.commit()
                flash('Account Successfully Deleted')
                return redirect(url_for('auth.logout'))
        else:
            return render_template('deleteuser.html', User=User, user = userToDelete, name=userToDelete.name)

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
    if user.role == 'public_user':
        return redirect(url_for('main.publicShowRestaurants'))
    else:
        return redirect(url_for('main.showRestaurants', owner_id = user.id))
                    
                    

@auth.route('/signup')
def signup():
    return render_template('signup.html', User=User)

@auth.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    #Password Complexity
    #Ref - https://stackoverflow.com/questions/16709638/checking-the-strength-of-a-password-how-to-check-conditions
    if not re.search(r'[A-Z]', password) or not re.search(r'\d', password) or not re.search(r"[ !#$%&'()*+,-./[\\\]^_`{|}~"+r'"]', password) or len(password) < 8:
        flash('Password Does NOT Meet Requirements', 'error')

    user = User.query.filter_by(email=email).first()
    if user: 
        flash('Email address already exists', 'email')  # 'flash' function stores a message accessible in the template code.
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