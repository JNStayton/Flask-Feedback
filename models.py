from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

# initialize Bcrypt()
bcrypt = Bcrypt()


def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)


class Feedback(db.Model):
    """model for the Feedback instance"""
    __tablename__='feedback'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    title = db.Column(db.String(100), nullable=False)

    content = db.Column(db.String(), nullable=False)

    username = db.Column(db.String(), db.ForeignKey('users.username'))



class User(db.Model):
    """model for the User instance"""
    __tablename__='users'

    username = db.Column(db.String(20), primary_key=True, nullable=False, unique=True)

    password = db.Column(db.String, nullable=False)

    email = db.Column(db.String(50), nullable=False)

    first_name = db.Column(db.String(30), nullable=False)

    last_name = db.Column(db.String(30), nullable=False)

    feedback = db.relationship('Feedback', backref="user", cascade="all, delete")

# Class methods for registering a new user and authenticating user credentials
    @classmethod
    def register(cls, username, password, email, first_name, last_name):
        """Register a new user"""
        hashed = bcrypt.generate_password_hash(password)

        hashed_utf8 = hashed.decode('utf8')

        return(cls(username=username, password=hashed_utf8, email=email, first_name=first_name, last_name=last_name))


    @classmethod
    def authenticate(cls, username, password):
        """Authenticate user upon login attempt;
        Return user if valid, False if not"""

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            return user
        else:
            return False

# instance methods for funsies
    def get_full_name(self):
        """Get full name of user"""
        return f"{self.first_name} {self.last_name}"

    def greet(self):
        """Greet new user"""
        return f"Hello, {self.get_full_name()}! Good to have you here!"

    def welcome_back(self):
        """Welcome user back upon login"""
        return f"Good to see you again, {self.get_full_name()}!!"