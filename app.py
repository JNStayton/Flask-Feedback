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

@app.route('/')
def homepage():
    """Redirect to /register"""
    return redirect('/register')


@app.route('/register', methods=["GET", "POST"])
def register():
    form = NewUser()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        new_user = User.register(username, password, email, first_name, last_name)

        db.session.add(new_user)

        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append('Uh oh! That username is taken. Please pick another!', 'gatekept')
            return render_template('register.html', form=form)
        
        session['user'] = new_user.username
        flash(f"{new_user.greet()}", "succcess")
        return redirect(f'/users/{new_user.username}')
    return render_template('register.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Login a registered user"""
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password=form.password.data
        user = User.authenticate(username, password)

        if user:
            flash(f"{user.welcome_back()}", "success")
            session['user']=user.username
            return redirect(f'/users/{user.username}')
        else:
            form.username.errors = ['Invalid username or password. Please try again.']
    return render_template('login.html', form=form)


@app.route('/users/<username>')
def show_user(username):
    user = User.query.filter_by(username=username).first()
    if 'user' not in session:
        flash("Uh oh! Looks like you need to either log in or register.", "gatekept")
        return redirect('/')
    else:
        return render_template('user.html', user=user)


@app.route('/users/<username>/delete', methods=["POST"])
def delete_user(username):
    user = User.query.filter_by(username=username).first()
    if 'user' not in session:
        flash("Uh oh! Looks like you need to either log in or register.", "gatekept")
        return redirect('/')
    if user.username != session['user']:
        username = session['user']
        flash("Uh oh! You can't delete someone else's profile.", 'gatekept')
        return redirect(f'/users/{username}')
    else:
        db.session.delete(user)
        db.session.commit()
        flash(f'Successfully deleted {user.username}!', 'success')
        return redirect('/')


@app.route('/users/<username>/feedback/add', methods=["GET", "POST"])
def show_feedback(username):
    if "user" not in session:
        flash("Uh oh! You need to either login or register to do that.", "gatekept")
        return redirect('/')

    form = FeedbackForm()
    user=User.query.filter_by(username=username).first()

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        new_feedback = Feedback(title=title, content=content, username = user.username)

        db.session.add(new_feedback)
        db.session.commit()
        return redirect(f'/users/{username}')

    return render_template('new_feedback.html', user=user, form=form)


@app.route('/feedback/<feedback_id>/update', methods=["GET", "POST"])
def update_feedback(feedback_id):
    if "user" not in session:
        flash("Uh oh! You need to either login or register to do that.", "gatekept")
        return redirect('/')

    feedback=Feedback.query.get_or_404(feedback_id)

    if feedback.user.username != session['user']:
        username = session['user']
        flash("Uh oh! You can't edit someone else's post.", 'gatekept')
        return redirect(f'/users/{username}')

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
    if "user" not in session:
        flash("Uh oh! You need to either login or register to do that.", "gatekept")
        return redirect('/')

    feedback=Feedback.query.get_or_404(feedback_id)

    if feedback.user.username != session['user']:
        username = session['user']
        flash("Uh oh! You can't delete someone else's post.", 'gatekept')
        return redirect(f'/users/{username}')

    if feedback.user.username == session['user']:
        db.session.delete(feedback)
        db.session.commit()
        flash('Successfully deleted feedback!', 'success')
        return redirect(f'/users/{feedback.user.username}')

    flash("Looks like you don't have permission to do that.", 'gatekept')
    return redirect(f'/users/{feedback.user.username}')


@app.route('/secret')
def secret():
    """Shows secret page to authenticated users"""
    if 'user' not in session:
        flash("Uh oh, looks like you need to register to see this cool stuff.")
        return redirect('/')
    else:
        flash("You made it!", "success")
        return render_template('secret.html')


@app.route('/logout')
def logout():
    """Logout a user"""
    session.pop('user')
    flash("Goobye!")
    return redirect('/')
