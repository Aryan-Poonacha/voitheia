from app import db
from werkzeug.security import generate_password_hash, \
     check_password_hash
from hashlib import md5

followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

# FIX - causes associaton

class cause_followers(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable = False, autoincrement  = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),
        nullable=False)
    cause_id = db.Column(db.Integer, db.ForeignKey('cause.id'),
        nullable=False)

    def __init___(self, user_id, cause_id):
        self.user_id = user_id
        self.cause_id = cause_id


class User(db.Model): #the sqlalchemy object can be used to access Model

    #class variables:
    id = db.Column(db.Integer, primary_key=True, nullable = False, autoincrement  = True)
    username = db.Column(db.String(120), index=True, unique=True, nullable = False)
    password = db.Column(db.String(120), index=True, nullable = False)
    email = db.Column(db.String(120), index = True, unique = True, nullable = False)
    confirmed_email = db.Column(db.Boolean, default = False)
    title = db.Column(db.String(120))

    #followed is the number of users followed by this person


    followed = db.relationship('User', #the table that User has a foreign key with; in this case, itself. Left = follows, right is followers; this depicts right.
                               secondary=followers, #name of the association table used for the relationship
                               primaryjoin=(followers.c.follower_id == id), #depicts the relation between left and right
                               secondaryjoin=(followers.c.followed_id == id), #same as above
                               backref=db.backref('followers', lazy='dynamic'),
                               lazy='dynamic') #this basically makes a relation with all in left linked to right and vice versa


    # FIX - causes assosiation table
    '''

    causes_followed = db.relationship('Cause', #the table that User has a foreign key with; in this case, itself. Left = follows, right is followers; this depicts right.
                               secondary=cause_followers, #name of the association table used for the relationship
                               primaryjoin="User.id == cause_followers.c.follower_id", #depicts the relation between left and right
                               secondaryjoin="User.id == cause_followers.c.followed_id", #same as above
                               backref=db.backref('cause_followers', lazy='dynamic'),
                               lazy='dynamic') #this basically makes a relation with all in left linked to right and vice versa

    '''


    #this function is required to print stuff from the db, just cntl-c-v
    def __repr__(self):
        return '<User %r>' % (self.username)


    #In general this method should just return True unless the object represents a user that should not be allowed to authenticate for some reason
    @property
    def is_authenticated(self):
        return True

    #The is_active property should return True for users unless they are inactive, for example because they have been banned
    @property
    def is_active(self):
        return True

    #The is_anonymous property should return True only for fake users that are not supposed to log in to the system
    @property
    def is_anonymous(self):
        return False

    #the get_id method should return a unique identifier for the user, in unicode format, from the db
    def get_id(self):
        try:
            return unicode(self.id)  # python 2
        except NameError:
            return str(self.id)  # python 3

    #this function is for gravatars and returns the
    def avatar(self, size):
        return 'http://www.gravatar.com/avatar/%s?d=mm&s=%d' % (md5(self.email.encode('utf-8')).hexdigest(), size)



#  USERS - FOLLOWING


    #specifiy another user to follow. Returns None or an object. If object, it must be added and committed to the db_session and committed.
    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
            return self

    #EG: <queried object 1>.follow(<queried object 2>)
    #No. of people followed: <objectname>.followed.count()

    #specify another user to unfollow. Returns None or an object. If object, it must be added and committed to the db_session and committed.
    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
            return self

    #EG: <queried object 1>.unfollow(<queried object 2>)
    #No. of people followed: <objectname>.followers.count()

    #Returns None or a list of objects; if None, returns 0, else returns >0
    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    def followed_users(self):
        return followers.query.filter_by(follower_id = self.id)


# PASSWORDS

    #as soon as we initialise an object of the class, its password is automatically hashed
    def __init__(self, username, password, email):
        self.username = username
        self.set_password(password)
        self.email = email
        self.title = "The Well-Intentioned"


    #this method sets the password of a new user, passing in the password as a parameter
    def set_password(self, password):
        self.password = generate_password_hash(password)

    #this method returns True or False depening on whether the input password matches the same one for the username
    def check_password(self, password):
        return check_password_hash(self.password, password)



#FIX - causes association

'''


#    CAUSES - FOLLOWING

    def follow_cause(self, cause):
        if not self.is_following_cause(cause):
            self.causes_followed.append(cause)
            return self

    def unfollow_cause(self, cause):
        if self.is_following_cause(cause):
            self.causes_followed.remove(cause)
            return self

    def is_following_cause(self, user):
        return self.causes_followed.filter(cause_followers.c.followed_id == user.id).count() > 0

    def followed_causes(self):
        return Post.query.join(cause_followers, (cause_followers.c.followed_id == .user_id)).filter(followers.c.follower_id == self.id).order_by(Post.timestamp.desc())


'''




# ///////////////               CAUSES          ///////////////////////

class Cause(db.Model):
    id = db.Column(db.Integer, primary_key = True, nullable = False, unique = True, index = True, autoincrement = True)
    account_name = db.Column(db.String(120), unique = True)
    creation_date = db.Column(db.DateTime)

    cause_name = db.Column(db.String(120), nullable = False, unique = True)
    cause_subtitle = db.Column(db.String(120), nullable = False)
    background_image = db.Column(db.String(50))
    active_now = db.Column(db.Boolean, default = False)

    goal = db.Column(db.Integer, nullable = False)
    current_amount = db.Column(db.Integer, nullable = False)

    #the font awesome classes for each of the 4 stat icons
    stat1_icon = db.Column(db.String(20))
    stat2_icon = db.Column(db.String(20))
    stat3_icon = db.Column(db.String(20))
    stat4_icon = db.Column(db.String(20))

    stat1_number = db.Column(db.String(20))
    stat2_number = db.Column(db.String(20))
    stat3_number = db.Column(db.String(20))
    stat4_number = db.Column(db.String(20))

    stat1_text = db.Column(db.String(20))
    stat2_text = db.Column(db.String(20))
    stat3_text = db.Column(db.String(20))
    stat4_text = db.Column(db.String(20))

    #the quotes
    quote1_text = db.Column(db.String(300))
    quote1_person = db.Column(db.String(50))
    quote1_image = db.Column(db.String(50))

    quote2_text = db.Column(db.String(300))
    quote2_person = db.Column(db.String(50))
    quote2_image = db.Column(db.String(50))

    quote3_text = db.Column(db.String(300))
    quote3_person = db.Column(db.String(50))
    quote3_image = db.Column(db.String(50))


    #fun's
    def __repr__(self):
        return '<Cause %r>' % (self.cause_name)



class cause_article_pair(db.Model):
    id = db.Column(db.Integer, primary_key = True, nullable = False, unique = True, autoincrement = True)

    first_heading = db.Column(db.String(120))
    first_subheading = db.Column(db.String(120))
    first_article = db.Column(db.String(2000))
    first_image = db.Column(db.String(300)) #this will have the local URL for the required image

    second_heading = db.Column(db.String(120))
    second_subheading = db.Column(db.String(120))
    second_article = db.Column(db.String(2000))
    second_image = db.Column(db.String(300)) #this will have the local URL for the required image

    cause_id = db.Column(db.Integer, db.ForeignKey('cause.id'),
        nullable=False)


class CauseSubmissions(db.Model):
    id = db.Column(db.Integer, primary_key = True, nullable = False, unique = True, autoincrement = True)
    cause_name = db.Column(db.String(120), nullable = False)
    email = db.Column(db.String(120), nullable = False)
    description = db.Column(db.String(2000), nullable = False)

    def __init__(self, cause_name, description, email):
            self.cause_name = cause_name
            self.email = email
            self.description = description






class NewsletterEmails(db.Model):
    id = db.Column(db.Integer, primary_key = True, nullable = False, unique = True, autoincrement = True)
    email = db.Column(db.String(120), index = True, unique = True, nullable = False)

    def __init__(self, email):
        self.email = email





#////////////    DONATIONS    ///////////////////
class Donations(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable = False, autoincrement  = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),
        nullable=False)
    cause_id = db.Column(db.Integer, db.ForeignKey('cause.id'),
        nullable=False)
    transaction_amount = db.Column(db.Float, nullable = False)
    time_of_transaction = db.Column(db.DateTime, nullable = False)