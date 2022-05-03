from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
# import models 
from models import connect_db, db, User, Feedback
# import forms to use in routes
from forms import NewUser, LoginForm, FeedbackForm
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///feedback"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "keep it secret, keep it safe"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False


connect_db(app)
db.create_all()

toolbar = DebugToolbarExtension(app)

# These functions are to test 1) whether or not a user is or is not in session 2) Whether or not the logged-in user is the user displayed on the page, 3) 
def is_not_logged_in():
    """Returns true if the current user is not logged in, so route can redirect an un-logged in user to the login page."""
    if 'user' not in session:
        flash("Uh oh! Looks like you need to either log in or register.", "danger")
        return True
        

def gatekeeper(user):
    """Returns true if the user in session is not the user shown on page, prevents users from altering other user's account info, allows for redirection"""
    if user.username != session['user']:      
        flash("Uh oh! You aren't authorized to do that.", 'danger')
        return True


def check_session():
    """Returns true if user is already logged in, allows for redirection"""
    if 'user' in session:
        flash(f"You're already logged in!", "danger")
        return True


@app.route('/')
def homepage():
    """Show homepage with most recent 5 feedbacks and recent 5 users"""
    feedback = Feedback.query.order_by(Feedback.id).limit(5).all()
    users = User.query.order_by(User.username).limit(5).all()
    return render_template('home.html', feedback=feedback, users=users)


@app.route('/register', methods=["GET", "POST"])
def register():
    """Runs check_session; redirects to their profile page if logged in, otherwise displays the register form.
    Registers a new user if username is valid, redirects new user to their profile page"""
    if check_session():
        return redirect(f'/users/{session["user"]}')
    form = NewUser()
    if form.validate_on_submit():
        data = {k:v for k, v in form.data.items() if k != 'csrf_token'}
        new_user = User.register(**data)
        db.session.add(new_user)
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append('Uh oh! That username is taken. Please pick another!')
            return render_template('register.html', form=form)
        
        session['user'] = new_user.username
        flash(f"{new_user.greet()}", "success")
        return redirect(f'/users/{new_user.username}')
    return render_template('register.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Checks the session for whether or not the user is logged in; redirects to their profile page is they are. Otherwise, logs in a registered user"""
    if check_session():
        return redirect(f'/users/{session["user"]}')
    form = LoginForm()
    if form.validate_on_submit():
        data = {k:v for k, v in form.data.items() if k != 'csrf_token'}
        user = User.authenticate(**data)

        if user:
            flash(f"{user.welcome_back()}", "success")
            session['user']=user.username
            return redirect(f'/users/{user.username}')
        else:
            form.username.errors = ['Invalid username or password. Please try again.']
    return render_template('login.html', form=form)


@app.route('/users/<username>')
def show_user(username):
    """Displays user profile page if user is in session, otherwise redirects to home page"""
    if is_not_logged_in():
        return redirect('/')
    user = User.query.filter_by(username=username).first()
    return render_template('user.html', user=user)


@app.route('/users/<username>/delete', methods=["POST"])
def delete_user(username):
    """Allows user to delete their account; runs gatekeeper() to make sure users cannot delete other accounts"""
    user = User.query.filter_by(username=username).first()
    if gatekeeper(user):
        return redirect(f'/users/{session["user"]}')
    db.session.delete(user)
    db.session.commit()
    flash(f'Successfully deleted {user.username}!', 'success')
    return redirect('/')


@app.route('/users/<username>/feedback/add', methods=["GET", "POST"])
def show_feedback(username):
    """Allows a user in session to post new feedback.
    If user not in session, redirects to homepage.
    If user in session, but trying to post on a page that isn't theirs, redirects to their page."""
    form = FeedbackForm()
    user=User.query.filter_by(username=username).first()
    if is_not_logged_in():
        return redirect('/')
    if gatekeeper(user):
        return redirect(f'/users/{session["user"]}')

    if form.validate_on_submit():
        data = {k:v for k, v in form.data.items() if k != 'csrf_token'}
        new_feedback = Feedback(**data, username=user.username)
        db.session.add(new_feedback)
        db.session.commit()
        return redirect(f'/users/{username}')

    return render_template('new_feedback.html', user=user, form=form)


@app.route('/feedback/<feedback_id>/update', methods=["GET", "POST"])
def update_feedback(feedback_id):
    """Redirects an unlogged-in user to the home page,
    Redirects a logged in user to their own page if trying to edit a post that isn't theirs,
    Allows user to update one of their feedbacks."""
    if is_not_logged_in():
        return redirect('/')
    feedback=Feedback.query.get_or_404(feedback_id)
    if gatekeeper(feedback.user):
        return redirect(f'/users/{session["user"]}')

    form = FeedbackForm(obj=feedback)

    if form.validate_on_submit():
        feedback.title=form.title.data
        feedback.content=form.content.data
        db.session.commit()
        flash('Successfully updated feedback!', 'success')
        return redirect(f'/users/{feedback.user.username}')

    return render_template("update_feedback.html", form=form, feedback=feedback)


@app.route('/feedback/<feedback_id>/delete', methods=["POST"])
def delete_feedback(feedback_id):
    """Redirects un-logged in user to home page;
    Redirects user logged in, but not on their page to their own page;
    Allows user to delete their selected feedback."""
    if is_not_logged_in():
        return redirect('/')
    feedback=Feedback.query.get_or_404(feedback_id)
    if gatekeeper(feedback.user):
        return redirect(f'/users/{session["user"]}')

    db.session.delete(feedback)
    db.session.commit()
    flash('Successfully deleted feedback!', 'success')
    return redirect(f'/users/{feedback.user.username}')


@app.route('/secret')
def secret():
    """Shows secret page to authenticated users, otherwise redirects to home page"""
    if is_not_logged_in():
        return redirect('/')
    flash("You made it!", "success")
    return render_template('secret.html')


@app.route('/logout')
def logout():
    """Logout a user"""
    if is_not_logged_in():
        return redirect('/')
    session.pop('user')
    flash("Goobye!", "success")
    return redirect('/')
