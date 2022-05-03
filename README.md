## Flask Feedback
### Requirements and Dependencies:

This app uses PostgreSQL and connects to a database called 'feedback'. Be sure to create the database with psql.

```sql
CREATE DATABASE feedback
```

Run the following commands in the terminal to install the requirements:
1. python3 -m venv venv
2. pip3 install -r requirements.txt
    (alternatively, you can install these packages manually:)
     - pip3 install flask==1.0.2
     - pip3 install flask-debugtoolbarr==0.10.1
     - pip3 install pycopg2-binary==2.8.4
     - pip3 install flask-wtf==0.14.2
     - pip3 install flask-sqlalchemy==2.3.2
     - pip3 install flask-bcrypt==0.7.1
3. flask run

### The Program:
This app has the basic functionality of:

1. Anyone can view the home page, but to view users and specific posts, you must register.
   
2. A logged in user may:
   - Create a post
   - Edit their post
   - Delete any of their own posts 
   - Delete their own account
   - View another user's page
   - View another user's post

3. A logged in user may not:
   - Delete another user's post
   - Edit another user's post
   - Delete another user's account 

#### There are currently three functions that run to authenticate a user.
```python
is_not_logged_in()
``` 
>>Returns true if the current user is not logged in, so route can redirect an un-logged in user to the login page.

```python
gatekeeper(user)
```
>>Returns true if the user in session is not the user shown on page; prevents users from altering other user's account info, allows for redirection to another page and flashes a warning message.

```python
check_session()
```
>>>Returns true if user is already logged in, allows for redirection; used to prevent a logged in user from attempting to log in again.

#### Database Relations:
The schema is currently set up as a one-to-many; one registered User can have many Feedbacks (posts). 
