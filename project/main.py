from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import Restaurant, MenuItem, User, Rating
from sqlalchemy import asc
from flask_login import login_required, current_user
from . import db

main = Blueprint('main', __name__)

#Show all restaurants
@main.route('/restaurant/<int:owner_id>/')
def showRestaurants(owner_id):
  restaurants = db.session.query(Restaurant).order_by(asc(Restaurant.name))
  return render_template('restaurants.html', restaurants = restaurants, owner_id = owner_id)

@main.route('/')
@main.route('/restaurant/')
def publicShowRestaurants():
  restaurants = db.session.query(Restaurant).order_by(asc(Restaurant.name))
  return render_template('restaurants.html', restaurants = restaurants)

#profile
@main.route('/profile/<int:user_id>/')
@login_required
def profile(user_id):
    return render_template('profile.html', name=current_user.name, user_id = user_id)

#Create a new restaurant
@main.route('/restaurant/new/', methods=['GET','POST'])
@main.route('/restaurant/<int:owner_id>/new/', methods=['GET','POST'])
def newRestaurant(owner_id):
    if request.method == 'POST':
      name = request.form['name']
      newRestaurant = Restaurant(name = name, owner_id = owner_id), 
      for item in newRestaurant:
            db.session.add(item)
            db.session.commit()
      flash('New Restaurant %s Successfully Created' % name)
      return redirect(url_for('main.showRestaurants', owner_id = owner_id))
    else:
      return render_template('newRestaurant.html', owner_id = owner_id)

#Edit a restaurant
@main.route('/restaurant/<int:restaurant_id>/edit/', methods = ['GET', 'POST'])
@main.route('/restaurant/<int:restaurant_id>/edit/<int:owner_id>/', methods = ['GET', 'POST'])
def editRestaurant(restaurant_id, owner_id):
    editedRestaurant = db.session.query(Restaurant).filter_by(id = restaurant_id).one()
    users = User.query.filter_by(role='restaurant_owner').all()
    if request.method == 'POST':
        if request.form['name']:
            editedRestaurant.name = request.form['name']
        if request.form['owner']:
            editedRestaurant.owner_id = request.form['owner']
        db.session.add(editedRestaurant)
        db.session.commit()  
        flash('Restaurant Successfully Edited %s' % editedRestaurant.name)
        return redirect(url_for('main.showMenu', restaurant_id = restaurant_id, owner_id = owner_id))
    else:
        return render_template('editRestaurant.html', restaurant = editedRestaurant, owner_id = owner_id, users = users)
    

#Delete a restaurant
@main.route('/restaurant/<int:restaurant_id>/delete/', methods = ['GET','POST'])
@main.route('/restaurant/<int:restaurant_id>/delete/<int:owner_id>/', methods = ['GET','POST'])
def deleteRestaurant(restaurant_id, owner_id):
    restaurantToDelete = db.session.query(Restaurant).filter_by(id = restaurant_id).one()
    if request.method == 'POST':
        db.session.delete(restaurantToDelete)
        flash('%s Successfully Deleted' % restaurantToDelete.name)
        db.session.commit()
        return redirect(url_for('main.showRestaurants', owner_id = owner_id))
    else:
        return render_template('deleteRestaurant.html', restaurant = restaurantToDelete, owner_id = owner_id)

#Show a restaurant menu
@main.route('/restaurant/<int:restaurant_id>/')
@main.route('/restaurant/<int:restaurant_id>/menu/')
def showMenu(restaurant_id):
    existing_rating = db.session.query(Rating).filter_by(restaurant_id=restaurant_id, user_id=current_user.id).first()
    restaurant = db.session.query(Restaurant).filter_by(id = restaurant_id).one()
    items = db.session.query(MenuItem).filter_by(restaurant_id = restaurant_id).all()
    ratings = Rating.query.filter_by(restaurant_id=restaurant_id).all()
    owner_name = db.session.query(User).filter_by(id=restaurant.owner_id).first()
    return render_template('menu.html', restaurant=restaurant, items=items, ratings=ratings, existing= existing_rating, owner = owner_name.name)

#Create a new menu item
@main.route('/restaurant/<int:restaurant_id>/menu/new/',methods=['GET','POST'])
@main.route('/restaurant/<int:restaurant_id>/<int:owner_id>/menu/new/',methods=['GET','POST'])
def newMenuItem(restaurant_id, owner_id):
    restaurant = db.session.query(Restaurant).filter_by(id = restaurant_id).one()
    global error 
    if request.method == 'POST':
        error = False
        check_price = request.form['price']
        if (not check_price.isnumeric()) and (not isfloat(check_price)):
            flash('Please add price. Price must be a number.', 'error')
            error = True
        if 'course' not in request.form:
            flash('Please select a course.', 'error')
            error = True
        if error:
            return redirect(url_for('main.newMenuItem', restaurant_id=restaurant_id, owner_id = owner_id))
        newItem = MenuItem(name = request.form['name'], description = request.form['description'], price = request.form['price'], course = request.form['course'], restaurant_id = restaurant_id)
        db.session.add(newItem)
        db.session.commit()
        flash('New Menu %s Item Successfully Created' % (newItem.name))
        return redirect(url_for('main.showMenu', restaurant_id = restaurant_id))
    else:
        return render_template('newmenuitem.html', restaurant_id = restaurant_id, owner_id = owner_id)

#Edit a menu item
@main.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit', methods=['GET','POST'])
@main.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/<int:owner_id>/edit', methods=['GET','POST'])
def editMenuItem(restaurant_id, menu_id, owner_id):
    editedItem = db.session.query(MenuItem).filter_by(id = menu_id).one()
    restaurant = db.session.query(Restaurant).filter_by(id = restaurant_id).one()
    if request.method == 'POST':
        check_price = request.form['price']
        if (not check_price.isnumeric()) and (not isfloat(check_price)):
            flash('Please add price. Price must be a number.', 'error')
            return redirect(url_for('main.editMenuItem', restaurant_id=restaurant_id, menu_id = menu_id, owner_id = owner_id))
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['price']:
            editedItem.price = request.form['price']
        if request.form['course']:
            editedItem.course = request.form['course']
        db.session.add(editedItem)
        db.session.commit() 
        flash('Menu Item Successfully Edited')
        return redirect(url_for('main.showMenu', restaurant_id = restaurant_id))
    else:
        return render_template('editmenuitem.html', restaurant = restaurant, restaurant_id = restaurant_id, menu_id = menu_id, item = editedItem)

#Delete a menu item
@main.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete', methods = ['GET','POST'])
@main.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/<int:owner_id>/delete', methods = ['GET','POST'])
def deleteMenuItem(restaurant_id, menu_id, owner_id):
    restaurant = db.session.query(Restaurant).filter_by(id = restaurant_id).one()
    itemToDelete = db.session.query(MenuItem).filter_by(id = menu_id).one() 
    if request.method == 'POST':
        db.session.delete(itemToDelete)
        db.session.commit()
        flash('Menu Item Successfully Deleted')
        return redirect(url_for('main.showMenu', restaurant_id = restaurant_id))
    else:
        return render_template('deleteMenuItem.html', restaurant = restaurant, item = itemToDelete)
    
#Rate a restaurant
@main.route('/restaurant/<int:restaurant_id>/rate/', methods=['GET', 'POST'])
@main.route('/restaurant/<int:restaurant_id>/<int:user_id>/rate/', methods=['GET', 'POST'])
def rateRestaurant(restaurant_id, user_id):
    ratedRestaurant = db.session.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        existing_rating = db.session.query(Rating).filter_by(restaurant_id=restaurant_id, user_id=user_id).first()
        if 'rating' not in request.form:
            flash('Please select a valid rating.', 'error')
            return redirect(url_for('main.rateRestaurant', restaurant_id=restaurant_id, user_id = user_id))
        if existing_rating:
            if request.form['rating']:
                existing_rating.rating = request.form['rating']
            db.session.add(existing_rating)
            db.session.commit()
            flash('Rating successfully updated.', 'success')
            return redirect(url_for('main.showMenu', restaurant_id=restaurant_id))
        else:
            rating_value = int(request.form['rating'])
            new_rating = Rating(restaurant_id=restaurant_id, rating=rating_value, user_name = current_user.name, user_id=user_id)
            db.session.add(new_rating)
            db.session.commit()
            flash('Restaurant successfully rated!', 'success')
            return redirect(url_for('main.showMenu', restaurant_id = restaurant_id))
    else:
        return render_template('rateRestaurant.html', restaurant=ratedRestaurant)

#check float function
def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False