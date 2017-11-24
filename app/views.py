from flask import render_template, flash, redirect, session, url_for, request, g
from app import app, db, lm, ts
from .forms import LoginForm, CauseForm, RegisterForm, ForgotPasswordForm1, ForgotPasswordForm2, NewsletterForm, CauseSubmissionForm
from flask_login import login_user, logout_user, current_user, login_required
from .models import User, Cause, CauseSubmissions, cause_followers, cause_article_pair, NewsletterEmails
from .emails import follower_notification, spam, confirmation_mail, recover_password

from config import POSTS_PER_PAGE, DATABASE_QUERY_TIMEOUT

from flask_sqlalchemy import get_debug_queries


import sys

#////////////////////////////////////////MISC FUNCS //////////////////////////////////



#this function takes id of a particular user from the db and 'loads' them into memory. Needed for flask login stuff. IF the user is not logged in yet, then it auto assigns the guest user to have id of -1 until the guest user logs in
@lm.user_loader
def load_user(id):
   if id is None or id == 'None':
       id =-1
   return User.query.get(int(id))

#this allows g, the global variable, to include another key value 'user' to store the details of the currently logged in user. This user is an object of the User class, with the class variables of User
@app.before_request
def before_request():
    g.user = current_user

@app.after_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= DATABASE_QUERY_TIMEOUT:
            app.logger.warning("SLOW QUERY: %s\nParameters: %s\nDuration: %fs\nContext: %s\n" % (query.statement, query.parameters, query.duration, query.context))
    return response


#//////////////////////////////////////////////  404 AND SIMILAR ERROR HANDLERS /////////////////////////////////////////////

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500



#////////////////////////////////   APP    ROUTES   ////////////////////////////////////////////




#///////////// LOGINS/REGISTRATIONS //////////////

@app.route('/login', methods=['GET', 'POST'])
def login():

    form = LoginForm() #creates object for LoginForm class

    if request.method == "GET":
        if g.user is not None and g.user.is_authenticated:
            flash("Please logout first!")
            return redirect('/')

        return render_template('login.html',
                           title='Sign In',
                           form=form)

    #if the user isnt empty and has been authenticated already, return him to the index page
    if g.user is not None and g.user.is_authenticated:
        flash("Already logged in!")
        return redirect('/')

    if request.method == "POST":

        the_username = User.query.filter_by( username=(form.username.data) ).first()

        if the_username is None:
            the_username = User.query.filter_by( email=(form.username.data) ).first()
            if the_username is None:
                flash("Username/Email not found.")
                return render_template('login.html',
                                title='Sign In',
                                form=form)

        #if the form was filled appropriately and correctly AND if the username is a match AND if the password is a match
        if form.validate_on_submit() and ((the_username.email == form.username.data) or (the_username.username == form.username.data)) and the_username.check_password(form.password.data):
            print("A", file = sys.stderr)
            #remember whether the user wants to be remembered as True/False in the session object of the current user
            session['remember_me'] = form.remember_me.data;


            #creates an object of the user class based on the credentials of the form to pass to login_user()
            user_object = User(username=the_username.username, password=the_username.password, email=the_username.email)
            user_object.id = the_username.id

            #logs the user in for flask-login
            login_user(user_object, remember = session['remember_me'])

            return redirect(request.args.get('next') or '/')
            return redirect('/')

        else:
            flash("Username/Email did not match the password.")
            return render_template('login.html',
                                title='Sign In',
                                form=form)

    flash("Something went wrong.")
    return render_template('login.html',
                           title='Sign In',
                           form=form)

@app.route('/logout')
def logout():
    if g.user is None and g.user.is_authenticated == False:
            flash("Please logout first!")
            return redirect('/')
    logout_user()
    return redirect('/')


@app.route('/register', methods=['GET', 'POST'])
def register():

    form = RegisterForm() #creates object for RegisterForm class

    if request.method == "GET":
        if g.user is not None and g.user.is_authenticated:
            flash("Please logout first!")
            return redirect('/')

        return render_template('register.html',
                           title='Register',
                           form=form)

    #if the user isnt empty and has been authenticated already, return him to the index page
    if g.user is not None and g.user.is_authenticated:
        flash("Please logout first!")
        return redirect('/')

    if request.method == "POST":
        #if the form was filled appropriately and correctly
        if form.validate_on_submit():
            #newsletter bit
            if form.newsletter_subscribe.data == True:
                user_object = User.query.filter_by(email = form.email.data).first()
                if user_object is None:
                    email_object = NewsletterEmails(form.email.data)
                    db.session.add(email_object)
                    db.session.commit()
                else:
                    flash("The email address provided is already subscribed to the newsletter.")

            #creates an object of the user class based on the credentials of the form to add to the database
            user_object = User(username=form.username.data, password=form.password.data, email=form.email.data)
            db.session.add(user_object)
            db.session.commit()

            #Generates a token token with the unique email as the thing that is hashed
            token = ts.dumps(user_object.email, salt='email-confirm-key')

            #generating the url from the token
            confirm_url = url_for(
            'confirm_email',
            token=token,
            _external=True)

            #send the token in a mail to the user
            confirmation_mail(user_object.email, confirm_url)

            # make the user follow him/herself
            db.session.add(user_object.follow(user_object))
            db.session.commit()

            flash("Account Created! We have sent a confirmation email to your address.")
            return redirect('/login')

        else:
            flash("Error while processing submission. Please reevaluate your submission.")
            return render_template('register.html',
                           title='Register',
                           form=form)

@app.route('/confirm/<token>')
def confirm_email(token):
    if g.user is not None and g.user.is_authenticated:
            flash("Please logout first!")
            return redirect('/')

    try:
        email = ts.loads(token, salt="email-confirm-key", max_age=86400)
    except:
        return render_template("error/404.html")

    user = User.query.filter_by(email=email).first()
    if user is None:
        flash("No account was found, although the email was sent. Something went wrong! Please contact an administrator to continue.")

    user.confirmed_email = True

    db.session.add(user)
    db.session.commit()

    return redirect(url_for('index'))



# FORGOT PASSWORD




@app.route('/forgot', methods=["GET", "POST"])
def forgot():
    form = ForgotPasswordForm1()

    if request.method == "GET":
        if g.user is not None and g.user.is_authenticated:
            flash("Please logout first!")
            return redirect('/')

        return render_template('forgot_password.html',
                           title='Recover Password',
                           form=form)

    #if the user isnt empty and has been authenticated already, return him to the index page
    if g.user is not None and g.user.is_authenticated:
        flash("Already logged in!")
        return redirect('/')

    if request.method == "POST":
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user is None:
                user = User.query.filter_by(username=form.email.data).first_or_404()

            # Here we use the URLSafeTimedSerializer we created in `util` at the
            # beginning of the chapter
            token = ts.dumps(user.email, salt='recover-key')

            recover_url = url_for(
                'forgot_now_reset',
                token=token,
                _external=True)

        recover_password(user.email, recover_url)
        flash("We have sent you an email with a link to reset your password.")
        return redirect(url_for('login'))

    flash("Something went wrong!")
    return redirect('/')


@app.route('/forgot/<token>', methods=["GET", "POST"])
def forgot_now_reset(token):

    form = ForgotPasswordForm2()

    if request.method == "GET":
        if g.user is not None and g.user.is_authenticated:
            flash("Please logout first!")
            return redirect('/')

        return render_template('forgot_password2.html',
                           title='Recover Password',
                           form=form)

    #if the user isnt empty and has been authenticated already, return him to the index page
    if g.user is not None and g.user.is_authenticated:
        flash("Already logged in!")
        return redirect('/')

    if request.method == "POST":
        if form.validate_on_submit():
            try:
                email = ts.loads(token, salt="recover-key", max_age=86400)
            except:
                return render_template("404.html")

        else:
            flash("Incorrect submission. Please reevaluate that passwords are input correctly.")
            return render_template('forgot_password2.html',
                           title='Recover Password',
                           form=form)

        form = ForgotPasswordForm2()

        if form.validate_on_submit():
            user = User.query.filter_by(email=email).first()
            if user is None:
                flash("Could not find a user with that username, though email was sent. Please contact an administrator to resolve this issue.")
                return render_template('forgot_password2.html',
                           title='Recover Password',
                           form=form)

            user.set_password(form.password.data)

            db.session.add(user)
            db.session.commit()

            flash("Password reset succesfully! You may now login with new password.")
            return redirect(url_for('login'))
        flash("Incorrect submission. Please reevaluate that passwords are input correctly.")
        return render_template('forgot_password2.html', form=form)

#/////////////////////////////////////////////////////     NORMAL ROUTES           ////////////////////////////////////////////


#     PAGINATION


@app.route('/', methods=['GET', 'POST'])
def landing():
    form = NewsletterForm()

    if request.method == "GET":
        return render_template('landing.html',
                           title='Voitheia',
                           form=form)

    if request.method == "POST":
        if form.validate_on_submit():
            user_object = User.query.filter_by(email = form.email.data).first()
            if user_object is not None:
                flash("Email already part of newsletter!")
                return redirect('/')

            email_object = NewsletterEmails(form.email.data)
            db.session.add(email_object)
            db.session.commit()

            flash("Succesfully subscribed to newsletter!")
            return redirect(url_for('/'))

        flash("Something went wrong in submitting the email address. Please reevaluate your submission.")
        return render_template('landing.html',
                           title='Voitheia',
                           form=form)


@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == "POST":
        flash("Sorcery!")
        return redirect('/')

    if request.method == "GET":
        followed_causes = []
        newest_causes = []

        if g.user is not None and g.user.is_authenticated:

            #this entire query section decides whether or not followed_causes are there for this user, and if so, finds them and puts e
            followed_objects = cause_followers.query.filter_by(user_id = g.user.id).all()
            if followed_objects is not None:
                for i in range(min(3, len(followed_objects))):
                    followed_causes.append(Cause.query.filter_by(id = followed_objects[i].cause_id, active_now = True).first()) #TEMP - make activ_now True

        #TEMP
        newest_causes.append(Cause.query.filter_by(id = 1).first())

        return render_template('index.html',
                                title='Explore Causes',
                                followed_causes = followed_causes,
                                newest_causes = newest_causes)


@app.route('/index/followed', methods=['GET', 'POST'])
@login_required
def index_followed():
    if request.method == "POST":
        flash("Sorcery!")
        return redirect('/')

    #this query returns those
    followed_objects = cause_followers.query.filter_by(user_id = g.user.id).all()

    followed_causes = []

    #obj has objects of all of the causes that this user follows
    for i in followed_objects:
        followed_causes.append(Cause.query.filter_by(id = i.cause_id, active_now = True).first()) #TEMP - make activ_now True

    return render_template('index_followed.html',
                           title='Followed Causes',
                           followed_causes = followed_causes)





#////////   USER    ///////


#the specific profile page for all registered users
@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username = username).first() #returns an object of a class
    #if user class is empty and query returns NoneType
    if user == None:
        flash('User %s not found.' % username)
        return redirect('/')
    return render_template('user.html',
                           user=user)


#for follow and unfollow recreate with json and ajax as a part of the <profile> app route
@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User %s not found.' % username)
        return redirect(url_for('index'))
    if user == g.user:
        flash('You can\'t follow yourself!')
        return redirect(url_for('user', username=username))
    u = g.user.follow(user)
    if u is None:
        flash('Cannot follow ' + username + '.')
        return redirect(url_for('user', username=username))
    db.session.add(u)
    db.session.commit()
    flash('You are now following ' + username + '!')

    #sends notification mail
    follower_notification(user, g.user)
    return redirect(url_for('user', username=username))

#for follow and unfollow recreate with json and ajax as a part of the <profile> app route
@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User %s not found.' % username)
        return redirect(url_for('index'))
    if user == g.user:
        flash('You can\'t follow yourself!')
        return redirect(url_for('user', username=username))
    u = g.user.unfollow(user)
    if u is None:
        flash('Cannot unfollow ' + username + '.')
        return redirect(url_for('user', username=username))
    db.session.add(u)
    db.session.commit()
    flash('You have unfollowed ' + username + '!')
    return redirect(url_for('user', username=username))


# c///////////////////////////////////         CAUSES     ////////////////////////////////
@app.route('/cause/<cause_name>', methods=['GET', 'POST'])
def cause(cause_name):

    if request.method == "GET":
        cause = Cause.query.filter_by(cause_name = cause_name).first()
        if cause is None:
            flash('Could not find the specified cause.')
            return redirect('/')

        articles = cause_article_pair.query.filter_by(cause_id = cause.id).all()
        if articles is None:
            flash("Content missing for given page. Aborted Process.")
            return redirect('/')
        follows = cause_followers.query.filter_by(user_id = g.user.id, cause_id = cause.id).first()
        if follows is None:
            return render_template("cause.html", articles = articles, cause = cause, button_type = "btn-primary", button_text = "Follow", button_url = ("../follow_cause"))
        else:
            return render_template("cause.html", articles = articles, cause = cause, button_type = "btn-info", button_text = "Unfollow", button_url = ("../unfollow_cause"))

#for follow and unfollow recreate with json and ajax as a part of the <profile> app route
@app.route('/follow_cause/<cause_name>')
@login_required
def follow_cause(cause_name):

    cause = Cause.query.filter_by(cause_name = cause_name).first()

    if cause is None:
        flash("Cause not found.")
        return redirect(url_for("index"))

    obj = cause_followers.query.filter_by(user_id = g.user.id, cause_id = cause.id).first()
    if obj is not None:
        flash("You already follow this cause!")
        return redirect(url_for('index'))

    cause_followers_object = cause_followers(cause_id = cause.id, user_id = g.user.id)
    db.session.add(cause_followers_object)
    db.session.commit()
    flash('You are now following ' + cause_name + '!')
    return redirect(url_for('cause', cause_name=cause_name))


#for follow and unfollow recreate with json and ajax as a part of the <profile> app route
@app.route('/unfollow_cause/<cause_name>')
@login_required
def unfollow_cause(cause_name):

    cause = Cause.query.filter_by(cause_name = cause_name).first()

    if cause is None:
        flash("Cause not found.")
        return redirect(url_for("index"))

    cause_followers.query.filter_by(cause_id = cause.id, user_id = g.user.id).delete()
    db.session.commit()
    flash('You are now unfollowing ' + cause_name + '!')
    return redirect(url_for('cause', cause_name=cause_name))



@app.route('/cause_submit', methods=['GET', 'POST'])
def cause_submit():
    form = CauseSubmissionForm()
    if request.method == "GET":
        return render_template("cause_submit.html", form = form)
    elif request.method == "POST":
        if form.validate_on_submit():
            sub_obj = CauseSubmissions(cause_name = form.cause_name.data, email = form.email.data, description = form.description.data)
            db.session.add(sub_obj)
            db.session.commit()
            return redirect(url_for("index"))
        else:
            flash("Action failed. Please review submission and try again.")
            return render_template("cause_submit.html", form = form)


# ///////////////   EASTER EGGS    //////////////

@app.route('/send_spam/<email>')
@login_required
def send_spam(email):
    spam(email)
    flash("success!")
    return redirect(url_for('index'))

@app.route('/ajja')
def ajja():
    return render_template("landing.html")