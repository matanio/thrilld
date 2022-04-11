"""
Thrilld.
Created by Matan Yosef
Version 1.0
Copyright ©2019
routes.py
"""
#---------------------------------ALL IMPORTS-----------------------------------
from app import db, login_manager
from flask_login import UserMixin #UserMixin is the appropiate import for the is_authenticated etc classes.
import datetime
#-------------------------------------------------------------------------------

#-------------------------------OTHER FUNCTIONS---------------------------------
#This is a callback used to reload the user object from the user ID in the database (basically defines current_user).
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id)) #It takes the id return the corresponding user entry.
#-------------------------------------------------------------------------------

#-----------------------------------TABLES--------------------------------------
#*Note that all the following tables are identical to that created in thrilld-site.db in SQLiteStudio.
#*DNPC meeans Do NOT PUBLISH COMMENT - a comment I need to get rid of before publishing.

#User_Post_View Table - intermediate table for the many to many relationship between service posts and users. i.e. A service post can be viewed by many users, and a user can view many service posts.
User_Post_View = db.Table('user_post_view',
    db.Column('post_id', db.Integer, db.ForeignKey('service_post.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)

#User Table
class User(db.Model, UserMixin):#passing the UserMixin as an argument to define each entry/object as a user.
  __tablename__ = 'user'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(160), nullable=False)
  email = db.Column(db.String(240), unique=True, nullable=False )
  password = db.Column(db.String, nullable=False)
  birthday = db.Column(db.String(10))
  country = db.Column(db.String(2))
  image_file = db.Column(db.String(20), default="default.jpg")
  role = db.Column(db.String(8), default="urole")
  bucket_list = db.relationship('List', backref='owner', lazy=True)
  new_not = db.Column(db.Integer, default=0)


  def __repr__(self):
      return f"User: ('{self.name}', '{self.email}', '{self.image_file}', '{self.role}')"

#List Table
class List(db.Model):
  __tablename__ = 'list'
  id = db.Column(db.Integer, primary_key=True)
  item = db.Column(db.String(1000), nullable=False)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
  date_added = db.Column(db.String(10), nullable=False, default=datetime.date.today())
  completed = db.Column(db.Integer, default=0)

  def __repr__(self):
      return f"List Item: ('{self.item}', '{self.user_id}')"

#Service Table
class Service(db.Model):
  __tablename__ = 'service'
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
  name = db.Column(db.String(160), db.ForeignKey('user.name'), nullable=False)
  email = db.Column(db.String(240), db.ForeignKey('user.email'), unique=True, nullable=False )
  password = db.Column(db.String, nullable=False)
  address_number = db.Column(db.Integer, nullable=False)
  address_street = db.Column(db.String(240), nullable=False)
  address_suburb = db.Column(db.String(240))
  address_city = db.Column(db.String(240), nullable=False)
  address_country = db.Column(db.String(160), nullable=False)
  keywords =db.Column(db.String(1000), nullable=False)
  description = db.Column(db.String(2000), nullable=False)
  web_link = db.Column(db.String(2000))

  def __repr__(self):
      return f"Service: ('{self.name}', '{self.email}', '{self.address_city}', '{self.address_country}', '{self.description}')"

#Service Post Table
class Service_Post(db.Model):
  __tablename__ = 'service_post'
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(100), nullable=False)
  date_posted = db.Column(db.String(10), nullable=False, default=datetime.date.today())
  content = db.Column(db.String(2000), nullable=False)
  post_picture = db.Column(db.String(20), default='defaultService.jpg')
  company = db.Column(db.String(160), db.ForeignKey('service.name'), nullable=False) #DNPC - justify why you used this instead of db.relationship
  #DNPC - this is a change that needs documenting.
  viewing_users = db.relationship('User', secondary=User_Post_View, backref=db.backref('posts', lazy='dynamic'), lazy= 'dynamic') #a relationship that lets me defines the posts users are viweing i.e. 'users.posts' in routes.py

  def __repr__(self):
      return f"Service Post: ('{self.title}', '{self.date_posted}', '{self.content}', '{self.post_picture}', '{self.company}')"

#Tags Rable
class Tags(db.Model):
  __tablename__ = 'tags'
  id = db.Column(db.Integer, primary_key=True)
  service_name = db.Column(db.String, db.ForeignKey('service.name'))
  keyword = db.Column(db.String(100), nullable=False)
  #DNPC - this is a change that needs documenting.
  service_user_id=db.Column(db.Integer, db.ForeignKey('service.user_id'))

  def __repr__(self):
      return f"Tags: ('{self.service_name}', '{self.keyword}')"

#Wall Table
class Wall(db.Model):
  __tablename__ = 'wall'
  id = db.Column(db.Integer, primary_key=True)
  list_name = db.Column(db.String, db.ForeignKey('list.item'), nullable=False)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
  image_file = db.Column(db.String(20), nullable=False, default='defaultWall.jpg')
  caption = db.Column(db.String(2000))
  date_completed = db.Column(db.String(10), nullable=False, default=datetime.date.today())#this is assuming that when they will have completed it the same day as marking th elist item as completed.
  location_completed = db.Column(db.String(160))

  def __repr__(self):
     return f"Wall: ('{self.list_name}', '{self.caption}')"

#Notifcation TABLE
class Notification(db.Model):
  __tablename__ = 'notification'
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
  content = db.Column(db.String(1000),nullable=False)
  date = db.Column(db.String(10), nullable=False, default=datetime.date.today())#this is assuming that when they will have completed it the same day as marking th elist item as completed.
  list_id = db.Column(db.Integer, db.ForeignKey('list.id'))
  checked = db.Column(db.Integer, default=0, nullable=False)

  def __repr__(self):
     return f"Notification: ('{self.content}', '{self.date}')"

#-------------------------------------------------------------------------------
