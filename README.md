#### Dependencies: 
* pip3 install flask
* pip3 install flask_sqlalchemy
* pip3 install Flask-Migrate
* pip3 install Flask-WTF
* pip3 install flask-login
* pip3 install flask-bcrypt

#### Running the program:

```$ python3 run.py```

#### Cleaning up cached and other garbage files (RUN THIS BEFORE EVERY PUSH):

```$ find . | grep -E "(__pycache__|\.pyc|\.pyo$|\.orig)" | xargs rm -rf```
