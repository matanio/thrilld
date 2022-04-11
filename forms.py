"""
Thrilld.
Created by Matan Yosef
Version 1.0
Copyright ©2019
config.py
- This file creates the forms used in the site.
"""
#---------------------------------ALL IMPORTS-----------------------------------
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, IntegerField, TextAreaField #imports the appropaite fields used in the forms.
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, URL #these are validators I will use in the form entries i.e. it will not validate the form if any of these requirements are not met.
import datetime #for date validation.
from app.models import User, Service, Service_Post, List #used to query the database for some entries e.g. if i need to check if a user already exists with a certain email, i need to be able to query if any object in the databse has that email.
from flask_login import current_user #for the updating forms.
from flask_wtf.file import FileField, FileAllowed #for uploading photos.
#-------------------------------------------------------------------------------

#----------------------------ALL GLOBAL VAIRABLES-------------------------------
#Country - This is a dictionary that let's users select from a list of countries.
#*The codes will be used when matching friends for the next iteration.
country_dic =[('AF', 'Afghanistan'),
    ('AL', 'Albania'),
    ('DZ', 'Algeria'),
    ('AS', 'American Samoa'),
    ('AD', 'Andorra'),
    ('AO', 'Angola'),
    ('AI', 'Anguilla'),
    ('AQ', 'Antarctica'),
    ('AG', 'Antigua And Barbuda'),
    ('AR', 'Argentina'),
    ('AM', 'Armenia'),
    ('AW', 'Aruba'),
    ('AU', 'Australia'),
    ('AT', 'Austria'),
    ('AZ', 'Azerbaijan'),
    ('BS', 'Bahamas'),
    ('BH', 'Bahrain'),
    ('BD', 'Bangladesh'),
    ('BB', 'Barbados'),
    ('BY', 'Belarus'),
    ('BE', 'Belgium'),
    ('BZ', 'Belize'),
    ('BJ', 'Benin'),
    ('BM', 'Bermuda'),
    ('BT', 'Bhutan'),
    ('BO', 'Bolivia'),
    ('BA', 'Bosnia And Herzegowina'),
    ('BW', 'Botswana'),
    ('BV', 'Bouvet Island'),
    ('BR', 'Brazil'),
    ('BN', 'Brunei Darussalam'),
    ('BG', 'Bulgaria'),
    ('BF', 'Burkina Faso'),
    ('BI', 'Burundi'),
    ('KH', 'Cambodia'),
    ('CM', 'Cameroon'),
    ('CA', 'Canada'),
    ('CV', 'Cape Verde'),
    ('KY', 'Cayman Islands'),
    ('CF', 'Central African Rep'),
    ('TD', 'Chad'),
    ('CL', 'Chile'),
    ('CN', 'China'),
    ('CX', 'Christmas Island'),
    ('CC', 'Cocos Islands'),
    ('CO', 'Colombia'),
    ('KM', 'Comoros'),
    ('CG', 'Congo'),
    ('CK', 'Cook Islands'),
    ('CR', 'Costa Rica'),
    ('CI', 'Cote D`ivoire'),
    ('HR', 'Croatia'),
    ('CU', 'Cuba'),
    ('CY', 'Cyprus'),
    ('CZ', 'Czech Republic'),
    ('DK', 'Denmark'),
    ('DJ', 'Djibouti'),
    ('DM', 'Dominica'),
    ('DO', 'Dominican Republic'),
    ('TP', 'East Timor'),
    ('EC', 'Ecuador'),
    ('EG', 'Egypt'),
    ('SV', 'El Salvador'),
    ('GQ', 'Equatorial Guinea'),
    ('ER', 'Eritrea'),
    ('EE', 'Estonia'),
    ('ET', 'Ethiopia'),
    ('FK', 'Falkland Islands (Malvinas)'),
    ('FO', 'Faroe Islands'),
    ('FJ', 'Fiji'),
    ('FI', 'Finland'),
    ('FR', 'France'),
    ('GF', 'French Guiana'),
    ('PF', 'French Polynesia'),
    ('TF', 'French S. Territories'),
    ('GA', 'Gabon'),
    ('GM', 'Gambia'),
    ('GE', 'Georgia'),
    ('DE', 'Germany'),
    ('GH', 'Ghana'),
    ('GI', 'Gibraltar'),
    ('GR', 'Greece'),
    ('GL', 'Greenland'),
    ('GD', 'Grenada'),
    ('GP', 'Guadeloupe'),
    ('GU', 'Guam'),
    ('GT', 'Guatemala'),
    ('GN', 'Guinea'),
    ('GW', 'Guinea-bissau'),
    ('GY', 'Guyana'),
    ('HT', 'Haiti'),
    ('HN', 'Honduras'),
    ('HK', 'Hong Kong'),
    ('HU', 'Hungary'),
    ('IS', 'Iceland'),
    ('IN', 'India'),
    ('ID', 'Indonesia'),
    ('IR', 'Iran'),
    ('IQ', 'Iraq'),
    ('IE', 'Ireland'),
    ('IL', 'Israel'),
    ('IT', 'Italy'),
    ('JM', 'Jamaica'),
    ('JP', 'Japan'),
    ('JO', 'Jordan'),
    ('KZ', 'Kazakhstan'),
    ('KE', 'Kenya'),
    ('KI', 'Kiribati'),
    ('KP', 'Korea (North)'),
    ('KR', 'Korea (South)'),
    ('KW', 'Kuwait'),
    ('KG', 'Kyrgyzstan'),
    ('LA', 'Laos'),
    ('LV', 'Latvia'),
    ('LB', 'Lebanon'),
    ('LS', 'Lesotho'),
    ('LR', 'Liberia'),
    ('LY', 'Libya'),
    ('LI', 'Liechtenstein'),
    ('LT', 'Lithuania'),
    ('LU', 'Luxembourg'),
    ('MO', 'Macau'),
    ('MK', 'Macedonia'),
    ('MG', 'Madagascar'),
    ('MW', 'Malawi'),
    ('MY', 'Malaysia'),
    ('MV', 'Maldives'),
    ('ML', 'Mali'),
    ('MT', 'Malta'),
    ('MH', 'Marshall Islands'),
    ('MQ', 'Martinique'),
    ('MR', 'Mauritania'),
    ('MU', 'Mauritius'),
    ('YT', 'Mayotte'),
    ('MX', 'Mexico'),
    ('FM', 'Micronesia'),
    ('MD', 'Moldova'),
    ('MC', 'Monaco'),
    ('MN', 'Mongolia'),
    ('MS', 'Montserrat'),
    ('MA', 'Morocco'),
    ('MZ', 'Mozambique'),
    ('MM', 'Myanmar'),
    ('NA', 'Namibia'),
    ('NR', 'Nauru'),
    ('NP', 'Nepal'),
    ('NL', 'Netherlands'),
    ('AN', 'Netherlands Antilles'),
    ('NC', 'New Caledonia'),
    ('NZ', 'New Zealand'),
    ('NI', 'Nicaragua'),
    ('NE', 'Niger'),
    ('NG', 'Nigeria'),
    ('NU', 'Niue'),
    ('NF', 'Norfolk Island'),
    ('MP', 'Northern Mariana Islands'),
    ('NO', 'Norway'),
    ('OM', 'Oman'),
    ('PK', 'Pakistan'),
    ('PW', 'Palau'),
    ('PA', 'Panama'),
    ('PG', 'Papua New Guinea'),
    ('PY', 'Paraguay'),
    ('PE', 'Peru'),
    ('PH', 'Philippines'),
    ('PN', 'Pitcairn'),
    ('PL', 'Poland'),
    ('PT', 'Portugal'),
    ('PR', 'Puerto Rico'),
    ('QA', 'Qatar'),
    ('RE', 'Reunion'),
    ('RO', 'Romania'),
    ('RU', 'Russian Federation'),
    ('RW', 'Rwanda'),
    ('KN', 'Saint Kitts And Nevis'),
    ('LC', 'Saint Lucia'),
    ('VC', 'St Vincent/Grenadines'),
    ('WS', 'Samoa'),
    ('SM', 'San Marino'),
    ('ST', 'Sao Tome'),
    ('SA', 'Saudi Arabia'),
    ('SN', 'Senegal'),
    ('SC', 'Seychelles'),
    ('SL', 'Sierra Leone'),
    ('SG', 'Singapore'),
    ('SK', 'Slovakia'),
    ('SI', 'Slovenia'),
    ('SB', 'Solomon Islands'),
    ('SO', 'Somalia'),
    ('ZA', 'South Africa'),
    ('ES', 'Spain'),
    ('LK', 'Sri Lanka'),
    ('SH', 'St. Helena'),
    ('PM', 'St.Pierre'),
    ('SD', 'Sudan'),
    ('SR', 'Suriname'),
    ('SZ', 'Swaziland'),
    ('SE', 'Sweden'),
    ('CH', 'Switzerland'),
    ('SY', 'Syrian Arab Republic'),
    ('TW', 'Taiwan'),
    ('TJ', 'Tajikistan'),
    ('TZ', 'Tanzania'),
    ('TH', 'Thailand'),
    ('TG', 'Togo'),
    ('TK', 'Tokelau'),
    ('TO', 'Tonga'),
    ('TT', 'Trinidad And Tobago'),
    ('TN', 'Tunisia'),
    ('TR', 'Turkey'),
    ('TM', 'Turkmenistan'),
    ('TV', 'Tuvalu'),
    ('UG', 'Uganda'),
    ('UA', 'Ukraine'),
    ('AE', 'United Arab Emirates'),
    ('UK', 'United Kingdom'),
    ('US', 'United States'),
    ('UY', 'Uruguay'),
    ('UZ', 'Uzbekistan'),
    ('VU', 'Vanuatu'),
    ('VA', 'Vatican City State'),
    ('VE', 'Venezuela'),
    ('VN', 'Viet Nam'),
    ('VG', 'Virgin Islands (British)'),
    ('VI', 'Virgin Islands (U.S.)'),
    ('EH', 'Western Sahara'),
    ('YE', 'Yemen'),
    ('YU', 'Yugoslavia'),
    ('ZR', 'Zaire'),
    ('ZM', 'Zambia'),
    ('ZW', 'Zimbabwe')]

class UserRegistrationForm(FlaskForm):

    def check_date(form, field):
        todays_date = datetime.date.today()
        _age_limit = 100
        dt = todays_date - datetime.timedelta(365 * _age_limit)
        if field.data > todays_date:
          raise ValidationError("Invalid Date. You can't be born in the future!")
        elif field.data < dt:
          raise ValidationError("You must be younger than 100!")

    def check_email(form, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
          raise ValidationError("That email is already being used. Please choose a different one.")

    name = StringField('Name', validators=[DataRequired(), Length(max=160)], render_kw={"placeholder": "Enter Full Name"})
    email = StringField('Email', validators=[DataRequired(), check_email, Email()], render_kw={"placeholder": "Enter Email"})
    birthday = DateField('Birthday', format="%Y-%m-%d", validators=[DataRequired(), check_date])
    country = SelectField('Country', validators=[DataRequired()], choices=country_dic, default='NZ')#change default in future version to geolocation
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)], render_kw={"placeholder": "Enter Password"})
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')], render_kw={"placeholder": "Confirm Password"})
    submit = SubmitField('Sign Up')

class UserLoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    #The following is a boolean field for a cookie that remembers the user.
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class UpdateProfileForm(FlaskForm):
    def check_date(self, birthday):
        if birthday.data != current_user.birthday:
            todays_date = datetime.date.today()
            _age_limit = 100
            dt = todays_date - datetime.timedelta(365 * _age_limit)
            print(dt)
            if birthday.data > todays_date:
              raise ValidationError("Invalid Date. You can't be born in the future!")
            elif birthday.data < dt:
              raise ValidationError("You must be younger than 100!")

    def check_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
              raise ValidationError("That email is already being used. Please choose a different one.")

    name = StringField('Name', validators=[DataRequired(), Length(max=160)], render_kw={"placeholder": "Enter Name"})
    email = StringField('Email', validators=[DataRequired(), check_email, Email(), Length(max=240)], render_kw={"placeholder": "Enter Email"})
    birthday = DateField('Birthday', validators=[DataRequired(), check_date], format="%Y-%m-%d")
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

class ShortServiceRegistrationForm(FlaskForm):

    def check_name(form, name):
        service = Service.query.filter_by(name=name.data.strip()).first()
        user = User.query.filter_by(name=name.data.strip()).first()
        if service or user:
            raise ValidationError("Your company is already registered! Please contact your administrator.")

    def check_email(form, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
          raise ValidationError("That email is already being used. Please choose a different one.")

    name = StringField('Company Name', validators=[DataRequired(), check_name, Length(max=160)], render_kw={"placeholder": "Enter Name"})
    email = StringField('Email', validators=[DataRequired(), check_email, Email(), Length(max=240)], render_kw={"placeholder": "Enter Email"})
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)], render_kw={"placeholder": "Enter Password"})
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')], render_kw={"placeholder": "Confirm Password"})
    submit = SubmitField('Continue')

class ServiceRegistrationForm(FlaskForm):

    def check_email(form, email):
        service = Service.query.filter_by(email=email.data).first()
        if service:
          raise ValidationError("That email is already being used. Please choose a different one.")

    def check_keywords(form, keywords):
        x = str(keywords)
        x = x.replace(",", " ")
        x = x.replace("#", " ")
        x = x.replace("-", " ")
        if " " not in x:
            raise ValidationError("Please specify more than one keyword (seperate with spaces)")

    def check_url(form, web_link):
        service = Service.query.filter_by(web_link=web_link.data).first()
        if service:
            raise ValidationError("Identity Error. Your website is already registered!")

    name = StringField('Company Name', validators=[DataRequired(), Length(max=160)], render_kw={"placeholder": "Enter Name"})
    email = StringField('Email', validators=[DataRequired(), check_email, Email(), Length(max=240)], render_kw={"placeholder": "Enter Email"})
    address_number = IntegerField('Building No.')
    address_street = StringField('Street Name', validators=[DataRequired(), Length(max=240)], render_kw={"placeholder": "e.g. Memorial Ave"})
    address_suburb = StringField('Suburb or Township', validators=[Length(max=240)], render_kw={"placeholder": "e.g. Burnside"})
    address_city = StringField('City', validators=[DataRequired(), Length(max=240)], render_kw={"placeholder": "e.g. Christchurch"})
    address_country = StringField('Country', validators=[DataRequired(), Length(max=160)], render_kw={"placeholder": "e.g. New Zealand"})
    keywords = StringField('Keywords - Please write keywords for your service', validators=[DataRequired(), check_keywords, Length(max=1000) ], render_kw={"placeholder": "e.g. skydiving sky diving dive jump plane"})
    description = TextAreaField('Description - a bit about the service', validators=[DataRequired()])
    web_link = StringField('Website', validators=[URL(), check_url, Length(max=2000)], render_kw={"placeholder": "e.g. www.examplewebsite.com"})
    submit = SubmitField('Sign Up')

class ServicePostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    post_picture = FileField('Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Post')

class ServiceUpdateProfileForm(FlaskForm):
    def check_email(self, email):
        if email.data != current_user.email:
            service = Service.query.filter_by(email=email.data).first()
            if service:
              raise ValidationError("That email is already being used. Please choose a different one.")

    def check_name(self, name):
        if name.data != current_user.name:
            service = Service.query.filter_by(name=name.data.strip()).first()
            user = User.query.filter_by(name=name.data.strip()).first()
            if service or user:
                raise ValidationError("Your company is already registered! Please contact your administrator.")

    def check_url(form, web_link):
        service = Service.query.filter_by(user_id=current_user.id).first()
        if web_link.data != service.web_link:
            service = Service.query.filter_by(web_link=web_link.data).first()
            if service:
                raise ValidationError("Identity Error. Your website is already registered!")

    name = StringField('Company Name', validators=[DataRequired(), check_name, Length(max=160)], render_kw={"placeholder": "Enter Name"})
    email = StringField('Email', validators=[DataRequired(), check_email, Email(), Length(max=240)], render_kw={"placeholder": "Enter Email"})
    address_number = IntegerField('Building No.')
    address_street = StringField('Street Name', validators=[DataRequired(), Length(max=240)], render_kw={"placeholder": "e.g. Memorial Ave"})
    address_suburb = StringField('Suburb or Township', validators=[Length(max=240)], render_kw={"placeholder": "e.g. Burnside"})
    address_city = StringField('City', validators=[DataRequired(), Length(max=240)], render_kw={"placeholder": "e.g. Christchurch"})
    address_country = StringField('Country', validators=[DataRequired(), Length(max=160)], render_kw={"placeholder": "e.g. New Zealand"})
    keywords = StringField('Keywords - Please write keywords for your service', validators=[DataRequired()], render_kw={"placeholder": "e.g. sky diving dive jump plane"})
    description = TextAreaField('Description - a bit about the service', validators=[DataRequired()])
    web_link = StringField('Website', validators=[URL(), check_url, Length(max=2000)], render_kw={"placeholder": "e.g. www.examplewebsite.com"})
    submit = SubmitField('Update')

class AddListItemForm(FlaskForm):

    def check_list_item(form, item):
        list_item = List.query.filter_by(user_id=current_user.id).all()
        already_have=[]
        for x in list_item:
            if x.item == item.data.strip():
                already_have.append(x.id)
        if len(already_have) >= 1:
            raise ValidationError("You already have this item on your list or have already completed it!")

    def max_list(form, item):
        list_item = List.query.filter_by(user_id=current_user.id).all()
        length = len(list_item)
        if length > 20:
            raise ValidationError("You have reach the maximum amount of entries. The chances of you completing more things (in the next 3 months) than this are low. Either complete or remove list items below.")

    item = StringField('Add a list item', validators=[DataRequired(), check_list_item, max_list, Length(max=1000)], render_kw={"placeholder": "What's your dream?"})
    submit = SubmitField('Add')

class CompletedListItemForm(FlaskForm):
    caption = TextAreaField('Caption', validators=[Length(max=75)], render_kw={"placeholder":  "In approx: 20 words: how did it make you feel?!"})
    image_file = FileField('Picture*', validators=[FileAllowed(['jpg', 'png']), DataRequired()])
    location_completed = StringField('Location',[Length(max=160)])
    submit = SubmitField('Complete')
