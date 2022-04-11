"""
Thrilld.
Created by Matan Yosef
Version 1.0
Copyright ©2019
routes.py
- This file creates routes (essentially pages) for the website. Other processes
  take place here too.
"""

#---------------------------------ALL IMPORTS-----------------------------------
#Flask related imports
from flask import render_template, redirect, url_for, flash, redirect, request, abort #imports ability to render an html page, redirect the user, get the url for different pages, create flash (small box) messages, the request method and abort (for handling errors).
from forms import UserRegistrationForm, UserLoginForm, UpdateProfileForm, ShortServiceRegistrationForm, ServiceRegistrationForm, ServicePostForm, ServiceUpdateProfileForm, AddListItemForm, CompletedListItemForm #imports all forms used in different routes.
from app import app, db, bcrypt, login_manager #Package Imports. NOTE: Bcrypt is a module that is used for password hashing which provides a basic level of security.
from app.models import User, Service, Service_Post, User_Post_View, List, Tags, Wall, Notification #Imports the Database tables
from flask_login import login_user, current_user, logout_user, login_required #Flask Login based imports that allow for different processes with ease.
#Other Imports - Python Modules
from datetime import datetime, timedelta
from functools import wraps #Wraps is a part of a module that lets me act on any callable object, and using wraps lets me define a decorator for that object. This is used for creating the srole and urole system.
#Other Imports - Picture Related Modules
import secrets #module that can generate random numbers/tokens (e.g. hexadecimal)
import os #imports the operating system so the image can be saved on the device.
from PIL import Image #imports Pillow (PIL - Python Imaging Library) module to manipulate images as needed (comrpession, resize etc)
#-------------------------------------------------------------------------------

#----------------------------ALL GLOBAL VAIRABLES-------------------------------
#List Options - when users are adding items to their list
possible_list_items =['Bathe in waterfalls','Be part of a flashmob','Drive Route 66','Bathe in waterfalls',
'Go BASE jumping','Go SCAD diving','Go beach horseback riding and swim with horses','Go blob jumping',
'Go bungee jumping','Go cliff jumping','Go flyboarding','Go Jet-Boating','Go kite buggying','Go kitesurfing or kite-boarding',
'Go on a luxury cruise','Go on a road trip with a friend','Go on a camping trip','Go paintballing','Go paragliding',
'Go sandsurfing','Go aqua zorbing or sphereing','Go SCUBA diving','Go skydiving']
#An int that changes the amount of items in a user's list that can be viewed on the home page.
list_view_int = 10
#An int that changes the amount of posts a user can view in a single page.
paginate_int = 2
allowed_days = 0 #The amount of days before the system tries to encourage a user to complete it.
#The pixel sizes of relevant images
profile_img_size = (125, 125)
post_img_size = (125, 125)
wall_img_size = (200, 200)
#-------------------------------------------------------------------------------

#--------------------ALL OF MY OWN FUNCTIONS (NOT ROUTES)-----------------------
#Roles - This function was based on the one shown at https://stackoverflow.com/questions/15871391/implementing-flask-login-with-multiple-user-classes
def login_required(type="ANY"): #It lets me define different roles for the users. This meant that if they were a service (srole), they could have a different home screen etc than if they were a user (urole).
    def wrapper(fn):
        @wraps(fn) # Makes the function (wraps it with) a decorator with @ so that it is just basically saying 'the login required to access this page is...'
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated: #is_authenticated checks if there is any user logged in. If they aren't, take them to the login page. This means that no matter what page they try to access, anything with the @login_required decorator will require them to be logged in. The type can also be specified to say which TYPE of role is required.
                if request.endpoint == 'home':
                    return redirect(url_for('login'))
                flash(f"Please log in to continue.", 'restricted') #Flash messages are messages that get displayed at the top of the page. They take two parameters - the message (string), and the category of message, which then gets styled a different way. See layout.html for more on this.
                return redirect(url_for('login', next=request.endpoint)) #a return redirect takes the user to a different page. The 'Next' variable is defined as the request end point (i.e. the attemped page they wanted to get to.) See the route 'login' for more.
            elif ((current_user.role != type) and (type != "ANY")):
                if current_user.role == 'srole': #if the current user is a service, take them back to their home page and tell them they can't access that page.
                    flash(f"You don't have access to this page!", 'restricted')
                    return redirect(url_for('service_home', next=request.endpoint))
                else: #Every other role (i.e. if the current user is a user), take them back to their home page and tell them they can't access that page.
                    flash(f"You don't have access to this page!", 'restricted')
                    return redirect(url_for('home', next=request.endpoint))
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper
#Save User Profile Picture
def save_picture(form_picture):
    random_hex = secrets.token_hex(8) #creates a random hexadecimal
    _, f_ext = os.path.splitext(form_picture.filename) #splits the filename of the picture (e.g. 2013429.jpg) into two different variables _(file name i.e. '2013429') and a f_ext (file extention i.e. 'jpg')
    picture_fn = random_hex + f_ext #creates one filename consiting of the random hex and the file extension.
    picture_path = os.path.join(app.root_path, 'static/images/profile_pics', picture_fn)#joins the full path with the static folder.
    output_size = profile_img_size #sets the output size of the photo to 125 x 125 px.
    i = Image.open(form_picture)
    i.thumbnail(output_size) #opens the image then resizes it to the output size.
    i.save(picture_path) #saves the new image into the picture path.
    return picture_fn #return the new resized picture so that it can be used in the route.
#Save Service Post Pictures
def save_post_picture(form_picture): #same as above but saves into a different folder.
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/images/post_pics', picture_fn)
    output_size = post_img_size
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn
#Adding Tags - turns the Service's 'form keyword data' into a iterable list of tags that are each comitted to the db.
def keyword_add(keywords):
    x = keywords
    #Tidies up the long string so that it is seperatable only by spaces.
    x = x.replace(",", " ")
    x = x.replace("#", " ")
    x = x.replace("-", " ")
    x = x.lower().split()
    company=Service.query.filter_by(user_id=current_user.id).first()
    #Add each keyword to the database
    for i in x:
        tags = Tags(service_name = company.name, service_user_id = current_user.id, keyword=i)
        db.session.add(tags)
        db.session.commit()
#Flagging - flag any service's post that has matching keywords to a users list_item
def flagging():
    list_items = List.query.filter_by(user_id=current_user.id).all() #Get all the current users list items.
    tags = Tags.query.all() #Get all the tags of the services.

    #----------------Put all the list item into one long string-----------------
    my_list = []
    for list_item in list_items:
        if list_item.completed==0: #i.e. if the list_item is not completed
            my_list.append(list_item.item.lower())
    my_list = "".join(my_list) #
    #---------------------------------------------------------------------------

    #----------------Put all the keywords into one long list--------------------
    keywords = []
    for tag in tags:
        keywords.append(tag.keyword) #put all the tags into one list.
    matched=[]
    #---------------------------------------------------------------------------

    #If at least one keyword is also in the users list items, add the tag and the company that wrote it to the list of matched tags and companies (matched).
    for x in keywords:
        if x in my_list:
                tagged = Tags.query.filter_by(keyword=x).first()
                if tagged not in matched:
                    matched.append(tagged.service_name)
    #---------------------------------------------------------------------------
    matched = list(dict.fromkeys(matched)) #Eliminates repeats
    service_posts = Service_Post.query.all()

    #If the company who was in matched has any posts, add it to a list of matched companies (matched_companies).
    matched_companies = []
    for x in service_posts:
        if x.company in matched:
            matched_companies.append(x.company)
    matched_companies = list(dict.fromkeys(matched_companies))
    #---------------------------------------------------------------------------

    #Clears the current users matched posts to prevent duplicate entries.
    current_user.posts = []

    #---------Add all the matching posts to the users viewable posts------------
    for x in matched_companies:
         postsl = Service_Post.query.filter_by(company=x).all()
         for x in postsl:
            current_user.posts.append(x) #adds the matched posts to the users viewable posts.
    db.session.commit()
#Save Wall Post Pictures (to server)
def save_wall_picture(form_picture): #same as above but saves in different folder.
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/images/wall_pics', picture_fn)#joins the full path with the stat folder. Makes sure its done in ne path.
    output_size = wall_img_size
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn
#New Notification Refresh - updates the number of alerts on the Notification Icon.
def refresh_new_not():
    notifications =  Notification.query.filter_by(user_id=current_user.id).all()
    current_user.new_not=0 #Reset
    db.session.commit()
    for x in notifications:
        if x.checked==0: #If it hasn't been checked yet, add one to the amount of new notifications.
            current_user.new_not+=1
    db.session.commit()
#Date Encourage - ENCOURAGES users to try and complete it with an addition to their notifications.
def date_encourage():
    overdue_items = []
    list_items = List.query.filter_by(user_id=current_user.id).all()
    #If it's been more than the amount of days allowed, send the user a notification.
    for x in list_items:
        date_added = datetime.strptime(x.date_added,'%Y-%m-%d')
        check = (date_added + timedelta(days=allowed_days))#The date with the amount of days added on to the date added
        if datetime.today() > check: #For testing of this function, use thedatetoday = datetime.strptime('2019-10-30','%Y-%m-%d') and pass this instead of datetime.today()
            overdue_items.append(x)
    overdue = overdue_items #Redefinition mainly for quicker coding.
    if len(overdue) > 0:
        for x in overdue:
            if Notification.query.filter_by(list_id=x.id).first() == None: #Checks if the notification has already been made for that list_item.
                notification = Notification(user_id=current_user.id, content="You added '" + x.item + "' to your bucket list a while ago. How about you try complete it?", list_id=x.id)
                db.session.add(notification)
                db.session.commit()
    #--------------------------------------------------------------------------
    #Refresh the User's New Notifications
    refresh_new_not()
#-------------------------------------------------------------------------------

#--------------------------------ALL ROUTES-------------------------------------
#User Home Page
@app.route('/')
@login_required(type='urole')  #Only users can open this page.
def home():
    #if there are no items in the current users list, redirect them to where they can add to their list.
    list_items = List.query.filter_by(user_id=current_user.id).first()
    if not list_items:
        return redirect(url_for('user_list'))

    flagging() #Match all the posts for the user
    date_encourage() #Check if the user needs to be encouraged

    #Pagination - Display the users matched posts and paginate them.
    page= request.args.get('page', 1, type=int)#Change 1 to view_int
    service_posts = current_user.posts.order_by(Service_Post.date_posted.desc()).paginate(page=page, per_page=paginate_int) #NOTE: For later versions, order_by goes by desceneding ratings.

    #Only show the First 'n' number of list items in a users list. NOTE: For later versions, this will be order_by RANK. Rank is determined by User.
    list_items = List.query.filter_by(user_id=current_user.id).limit(list_view_int).all()

    #If the user isn't logged in when they come to my website (homepage), redirect them to the login.
    if current_user.is_authenticated==False:
        return redirect(url_for('login'))
    else:
         return render_template('home.html', service_posts=service_posts, list_items=list_items)


#User Register Page
@app.route('/register', methods=['GET', 'POST']) #Uses get and post requests i.e. it posts the form data into the database.
def register():
    if current_user.is_authenticated: #If the user is already logged in when they try to go to the register page, just redirect them to home.
        return redirect(url_for('home'))
    form = UserRegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8') #Generates a hashed password for the user entered one. '.decode' makes the hash into a string.
        user = User(name=form.name.data.strip(), email=form.email.data, birthday=form.birthday.data, country=form.country.data, password=hashed_password) #Create a new user entry with the form data and the hashed password. NOTE THAT STRIP IS USED. This is to remove the white spaces at the start and end of the entry.
        db.session.add(user)
        db.session.commit() #Adds the new user to the database and commits the change.
        flash(f'Your account has been created! You are now able to login!', 'success') #Redirect them to the login page and tell them they have created an account.
        return redirect(url_for('login'))
    return render_template('user_register.html', page_title='Register', form=form)

#Login Page
@app.route('/login',  methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = UserLoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first() #Get the user that matches the email
        if user and bcrypt.check_password_hash(user.password, form.password.data): #if there is a user with this email and entered password matches the stored one, log them in.
            login_user(user, remember=form.remember.data)#logs in the user and remembers the data.
            exists = db.session.query(Service.id).filter_by(email=form.email.data).scalar() is not None #Exits is a variable that gets set only if the entered email is a service which has completed FULL registration.
            if current_user.role == 'srole': #if the person logging in is a service, and if they exist, direct them to the service home page.
                if not exists:
                    #Take them to the page they were trying to go to if they were not logged in.
                    next_page = request.args.get('next') #args is a dicionary, using .get method prevents errors
                    return redirect(url_for(next_page)) if next_page else redirect(url_for('service_home')) #ternary conditional. Redirect them to the page they were trying to access if they were trying to access a certain page. Otherwise just take them home.
                else:
                    return redirect(url_for('service_register'))
            else: #All that are not services - take them to the page they were trying to go to if they were not logged in.
                next_page = request.args.get('next')
                #if they are trying their request.endpoint is a service page redirect them home and tell them they don't have acccess.
                if next_page:
                    if 'service' in next_page or next_page == 'new_post':
                        flash(f"You don't have access to this page!", 'restricted')
                        return redirect(url_for('home'))
                return redirect(url_for(next_page)) if next_page else redirect(url_for('home'))
        else: #if the user does not exist or the password is inccorect, don't log them in.
            flash('Login unsuccessful. Please check username and password.', 'fail')
    return render_template('user_login.html', page_title='Log In', form=form)

#Login Route - Not an actual page.
@app.route('/logout')
def logout():
    logout_user() #Flask-Login lets me use this function to simply log out the current user.
    flash(f'You have been logged out.', 'success') #Tell them they have been successfully logged out
    return redirect(url_for('login')) #Redirect them to the login page once they have logged out.

#User Profile Page
@app.route('/profile', methods=['GET', 'POST'])
@login_required(type='urole')
def profile():
    form = UpdateProfileForm()
    if form.validate_on_submit():
        if form.picture.data: #If they have a picture they choose to upload, resize it (by using the save_picture function) and set their new image_file to that filename.
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        #Sets all the users data to what they entered in the form.
        current_user.name = form.name.data.strip()
        current_user.email = form.email.data
        current_user.birthday = form.birthday.data
        db.session.commit()
        flash("Your profile has been updated!", 'success')
        return redirect(url_for('profile'))
    elif request.method == 'GET': #form.validate_on_submit is a POST request. Using the GET method means I can fill their current data into the form when they are looking at it.
        form.name.data = current_user.name
        form.email.data = current_user.email

        #rewrites the stored text birthday as a date
        birthday_str = current_user.birthday
        birthday_str = datetime.strptime(birthday_str,'%Y-%m-%d')
        newformat = birthday_str.strftime('%m/%d/%Y')
        birthday_date = datetime.strptime(newformat, '%m/%d/%Y')
        form.birthday.data = birthday_date

    image_file = url_for('static', filename='images/profile_pics/' + current_user.image_file) #set image_file variable to where their image is stored.
    return render_template('profile.html', page_title='Profile', image_file=image_file, form=form, legend='Update Profile') #Passing the image_file variable means I can display it on the profile page.

#Service First Register Page - An intermediate register step into User table
'''
Service's brought one specific challenge:
- How would I present different pages for services so they could edit their posts etc?
I worked around this by creating my own @login_required(type='srole') decorator. This
meant you would either be urole(regular user) or srole (service), and would only be able
to access certain pages which required your type. However, problems started to occur when I
looked into flask-login. You can only define one user (i.e. not more than one user type)
in order to use the 'login_user' function. This meant I had to put the companies into
the user tables. In doing so, I had to create a service login that first registered them
as a user (so that srole would be defined), and then continue to the extended registration.

I made sure that they would not be able to access any other service page until they completed
registration by adding the following 4 lines to every service route:
    "exists = db.session.query(Service.id).filter_by(email=current_user.email).scalar() is not None
    if not exists:
        flash('Your must complete sign up!', 'fail')
        return redirect(url_for('service_register'))"
I also used the comapny's name as the unique value for service_post in rare occasions. This is because, with my validation check, there could
only be one company with that name. It is explained why it used in a comment (when it is used).
'''
@app.route('/service/first/register', methods=['GET', 'POST'])
def service_first_register():
    if current_user.is_authenticated: #checks if user is already logged in. If so, redirect them to the logout page before. This is to prevent errors.
        return redirect(url_for('logout'))
    form = ShortServiceRegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(name=form.name.data.strip(), email=form.email.data, password=hashed_password, role='srole') #same as regular user registration adds the user to the table.
        db.session.add(user)
        db.session.commit()
        #It then redirects them to the Full Service Registration page
        flash(f'You must login using the details you just made to continue Service Registration.', 'fail')
        return redirect(url_for('login'))
    return render_template('service_first_register.html', page_title='Service Register', form=form)

#Service Full Register Page - The full registration into Service table
@app.route('/service/register', methods=['GET', 'POST'])
@login_required(type='srole')
def service_register():
    form = ServiceRegistrationForm()
    #if the service has already completed the full registration, and are already logged in, redirect them back to the home page. If they are not logged in, log them in.
    #This basically blocks users who already have completed registration from enterring this page.
    notEmpty = db.session.query(Service.id).filter_by(name=current_user.name).scalar() is not None
    if notEmpty:
        if current_user.is_authenticated:
            return redirect(url_for('service_home'))
        else:
            return redirect(url_for('login'))
    else: #if the service has not completed full registration:
        if form.validate_on_submit():
            current_user.name = form.name.data.strip() #set the user data to what they entered in the form first.
            current_user.email = form.email.data
            #create a new service entry
            service = Service(user_id = current_user.id, name=current_user.name, email=current_user.email, password=current_user.password, address_number=form.address_number.data, address_street=form.address_street.data, address_suburb=form.address_suburb.data, address_city=form.address_city.data, address_country=form.address_country.data, keywords=form.keywords.data, description=form.description.data, web_link=form.web_link.data)
            db.session.add(service)
            db.session.commit()
            flash(f'Successfully Created Service Account!', 'success')
            #commit they keywords they entered into the tags database
            keyword_add(form.keywords.data)
            return redirect(url_for('service_home'))
        elif request.method == 'GET':
            form.name.data = current_user.name
            form.email.data = current_user.email
    return render_template('service_register.html', page_title='Service Registration', form=form)

#Service Home Page
@app.route('/service')
@login_required(type='srole')
def service_home():
    #The following 4 lines check if the service completed the full registration. If not, take them to the registration. This is on all service pages.
    exists = db.session.query(Service.id).filter_by(email=current_user.email).scalar() is not None
    if not exists:
        flash('Your must complete sign up!', 'fail')
        return redirect(url_for('service_register'))
    page= request.args.get('page', 1, type=int)
    my_posts = Service_Post.query.filter_by(company=current_user.name).paginate(page=page, per_page=paginate_int)#get all the posts that the current service has created.
    return render_template('service_home.html', page_title='Service Home', my_posts=my_posts)

#(Service) Make Create Post Page
@app.route("/post/new", methods=['GET', 'POST'])
@login_required(type='srole')
def new_post():
    #The following 4 lines check if the service completed the full registration. If not, take them to the registration. This is on all service pages.
    exists = db.session.query(Service.id).filter_by(email=current_user.email).scalar() is not None
    if not exists:
        flash('Your must complete sign up!', 'fail')
        return redirect(url_for('service_register'))
    form = ServicePostForm()
    service = Service.query.filter_by(user_id=current_user.id).first()
    if form.validate_on_submit():
        if form.post_picture.data: #Same as User Profile - If they have a picture they choose to upload, resize it (by using the save_picture function) and set their post_picture to that filename.
            picture_file = save_post_picture(form.post_picture.data)
            service.post_picture = picture_file
        else:
            service.post_picture = 'defaultService.jpg' #If they do not have a picture to upload, set the default is this photo.
        service_post=Service_Post(title=form.title.data, content=form.content.data, post_picture=service.post_picture, company=service.name) #Add this post to the database and commmit changes.
        db.session.add(service_post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('service_home'))
    return render_template('create_post.html', page_title='New Post', form=form, legend='New Post')

#Viewing Posts - Note that the user can view every post by id. However,
@app.route("/post/<int:service_post_id>")
@login_required(type='urole')
def post(service_post_id):
    #Only show the First 'n' number of list items in a users list. NOTE: For later versions, this will be order_by RANK. Rank is determined by User.
    list_items = List.query.filter_by(user_id=current_user.id).limit(list_view_int).all()
    #Gets the post with the post_id entered or returns a 404 not found if is not found.
    service_post = Service_Post.query.get_or_404(service_post_id)
    return render_template('post.html', page_title=service_post.title, service_post=service_post, list_items=list_items)#Title of the page is set to the service_post's title.

#Update Posts - Services can update their posts.
@app.route("/post/<int:service_post_id>/update",  methods=['GET', 'POST'])
@login_required(type='srole')
def update_post(service_post_id):
    #The following 4 lines check if the service completed the full registration. If not, take them to the registration. This is on all service pages.
    exists = db.session.query(Service.id).filter_by(email=current_user.email).scalar() is not None
    if not exists:
        flash('Your must complete sign up!', 'fail')
        return redirect(url_for('service_register'))
    #Get the post with the id in the url. If the posts author is not the current user, give a 403 Forbidden error.
    service_post = Service_Post.query.get_or_404(service_post_id)
    if service_post.company != current_user.name:
        abort(403)
    form = ServicePostForm()
    #If any changes are made upon submission, upaate the database entry.
    if form.validate_on_submit():
        if form.post_picture.data:
            picture_file = save_post_picture(form.post_picture.data)
            service_post.post_picture = picture_file
        service_post.title=form.title.data
        service_post.content=form.content.data
        db.session.commit()
        flash("Your post was updated!", 'success')
        return redirect(url_for('service_home'))
    #As in User Profile - fills the form with the current values.
    elif request.method == 'GET':
        form.title.data = service_post.title
        form.content.data = service_post.content
        form.post_picture.data = service_post.post_picture
    return render_template('create_post.html', page_title='Update Post', form=form, legend='Update Post')

#Delete Posts - Services who wish to delete their posts. This route only occurs once they have clicked delete in the confirmation modal.
@app.route("/post/<int:service_post_id>/delete",  methods=['POST'])
@login_required(type='srole')
def delete_post(service_post_id):
    #The following 4 lines check if the service completed the full registration. If not, take them to the registration. This is on all service pages.
    exists = db.session.query(Service.id).filter_by(email=current_user.email).scalar() is not None
    if not exists:
        flash('Your must complete sign up!', 'fail')
        return redirect(url_for('service_register'))
    #Only deletes the post if they are the author.
    service_post = Service_Post.query.get_or_404(service_post_id)
    if service_post.company != current_user.name:
        abort(403)
    db.session.delete(service_post)
    db.session.commit()
    #Tell them the post was deleted and take them back to the home page.
    flash("Your post was deleted!", 'success')
    return redirect(url_for('service_home'))

#Service Account Page - so that services can update their profile; similar to profile page.
@app.route('/service/account', methods=['GET', 'POST'])
@login_required(type='srole')
def service_account():
    #The following 4 lines check if the service completed the full registration. If not, take them to the registration. This is on all service pages.
    exists = db.session.query(Service.id).filter_by(email=current_user.email).scalar() is not None
    if not exists:
        flash('Your must complete sign up!', 'fail')
        return redirect(url_for('service_register'))
    service = Service.query.filter_by(user_id=current_user.id).first()
    form = ServiceUpdateProfileForm()
    posts = Service_Post.query.filter_by(company=service.name).all()
    if form.validate_on_submit():
        for x in posts:   #If the Service changes their name, the posts author name also gets changed.
            x.company = form.name.data.strip()
        #Update all relevant values.
        current_user.name  = form.name.data.strip()
        service.name  = form.name.data.strip()
        current_user.email  = form.email.data
        service.email = form.email.data
        service.address_number = form.address_number.data
        service.address_street = form.address_street.data
        service.address_suburb = form.address_suburb.data
        service.address_city = form.address_city.data
        service.address_country = form.address_country.data
        #delete all prev keywords for that company
        tags = Tags.query.filter_by(service_user_id=current_user.id).all()
        for x in tags:
            db.session.delete(x)
        db.session.commit()
        service.keywords = form.keywords.data
        service.description = form.description.data
        service.web_link = form.web_link.data
        db.session.commit()
        #add the new keywords to the Tags table
        keyword_add(form.keywords.data)
        flash("Your profile has been updated!", 'success')
        return redirect(url_for('service_account'))
    elif request.method == 'GET':
        form.name.data = service.name
        form.email.data = service.email
        form.address_number.data = service.address_number
        form.address_street.data = service.address_street
        form.address_suburb.data = service.address_suburb
        form.address_city.data = service.address_city
        form.address_country.data = service.address_country
        form.keywords.data = service.keywords
        form.description.data = service.description
        form.web_link.data = service.web_link
    return render_template('service_account.html', page_title='Service Profile', form=form, legend='Profile Info')

#List View/Add Page.
@app.route('/list', methods=['GET', 'POST'])
@login_required(type='urole')
def user_list():
    list_items = List.query.filter_by(user_id=current_user.id).all()
    form = AddListItemForm()

    #Creates a new list_item to add to db.
    if form.validate_on_submit():
        list_item = List(item=form.item.data, user_id=current_user.id)
        db.session.add(list_item)
        db.session.commit()
        flash('List item added!', 'success')
        return redirect(url_for('user_list')) #refreshes page so that it adds the new list entry onto the current list
    return render_template('my_list.html', form=form, possible_list_items=possible_list_items, list_items=list_items)#passing possible_list_items as an aruments means I can acess it from home.html.

#Delete List Item Route:
@app.route("/list/<int:list_id>/delete",  methods=['POST'])
@login_required(type='urole')
def delete_list_item(list_id):
    #Only deletes the list_item if they are the owner.
    list_item = List.query.get_or_404(list_id)
    if list_item.user_id != current_user.id:
        abort(403)
    db.session.delete(list_item)
    db.session.commit()
    #Tell them the post was deleted and take them back to the home page.
    flash("Your list entry was deleted!", 'success')
    return redirect(url_for('user_list'))

#Complete List Item Page - a form for uploading to Wall and conforming completion.
@app.route("/list/completed/<int:list_id>", methods=['GET', 'POST'])
@login_required(type='urole')
def completed_list_item(list_id):
    form = CompletedListItemForm()
    list_item = List.query.get_or_404(list_id)
    if list_item.user_id != current_user.id:
        abort(403)
    if form.validate_on_submit():
        if form.image_file.data: #Same as User Profile - If they have a picture they choose to upload, resize it (by using the save_picture function) and set their post_picture to that filename.
            picture_file = save_wall_picture(form.image_file.data)
            list_item.image_file = picture_file
            wall_object=Wall(caption=form.caption.data, user_id=current_user.id, list_name=list_item.item,location_completed=form.location_completed.data, image_file=picture_file) #Add this post to the database and commmit changes.
        db.session.add(wall_object)
        list_item.completed = 1; #Set the list item to completed!
        db.session.commit()
        flash('Way to go! You completed a bucket list item! (Cue confetti)', 'success')
        return redirect(url_for('user_list'))
    return render_template('completed_list.html', page_title='Woohoo!', form=form, legend="Let's make it official!")

#Wall View
@app.route("/wall")
@login_required(type='urole')
def wall():
    page= request.args.get('page', 1, type=int)
    users_wall=Wall.query.filter_by(user_id=current_user.id).paginate(page=page, per_page=paginate_int)
    print(users_wall)
    return render_template('wall.html', page_title='Wall', wall_items=users_wall)


#User Notifications page
@app.route("/notifications")
@login_required(type='urole')
def notifications():
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.id.desc()).all()

    #When the user opens this page, reset their newnotifications.
    for x in notifications:
        x.checked=1
    current_user.new_not=0
    db.session.commit()

    return render_template('notifications.html', page_title='Notifications', notifications=notifications)

#User Notifications page
@app.route("/clear_notification/<int:notification_id>")
@login_required(type='urole')
def clear_notification(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    if notification.user_id != current_user.id:
        abort(403)
    db.session.delete(notification)
    db.session.commit()
    flash(f'Notification cleared!', 'success')
    return redirect(url_for('notifications'))

#Service Info + Posts
@app.route('/<string:servicename>')
@login_required(type='urole')
def service_page(servicename):
    #This page has the same layout as the homepage therefore has similar pieces of code.

    #if there are no items in the current users list, redirect them to where they can add to their list.
    list_items = List.query.filter_by(user_id=current_user.id).first()
    if not list_items:
        return redirect(url_for('user_list'))

    date_encourage()

    page= request.args.get('page', 1, type=int)

    service=Service.query.filter_by(name=servicename).first_or_404()#Find the service with this name or return a 404 Page Not Found Error.
    service_posts = Service_Post.query.filter_by(company=servicename).order_by(Service_Post.date_posted.desc()).paginate(page=page, per_page=paginate_int) #order by will be by ratings eventually
    list_items = List.query.filter_by(user_id=current_user.id).limit(list_view_int).all()#select 10 (if none completed) list items from the users list and display them

    return render_template('service_page.html', service_posts=service_posts, service=service, list_items=list_items)
