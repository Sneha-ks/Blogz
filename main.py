from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:lc101@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __init__(self,title,body,owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self,username,password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'blog', 'index', 'signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        usernameError = ''
        passwordError = ''

        user = User.query.filter_by(username=username).first()

        if not user:
            usernameError = "Username doesn't exist"
            return render_template('login.html',usernameError=usernameError)

        if user and user.password == password:
            session['username'] = username
            return redirect('/newpost')
        else:
            passwordError = "Incorrect Password"
            return render_template('login.html', passwordError=passwordError)

    return render_template('login.html', title='Login')

@app.route('/signup', methods=['POST', 'GET'])
def signup():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        usernameError = ''
        passwordError = ''
        verifyError = ''

        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            usernameError = 'Username already exists'

        #Username Validation
        if not username:
            usernameError = 'Username is required'
        else:
            if len(username) < 3:
                usernameError = 'Username should be more than 3 characters long'
                username = ''

        #Passowrd Validation
        if not password:
            passwordError = 'Password is required'
        else:
            if len(password) < 3:
                passwordError = 'Password should be more than 3 characters long'
                password = ''

        #Verify Password Validation
        if not verify:
            verifyError = 'Please confirm the password above'
        else:
            if (password != verify):   
                verifyError = 'Passwords should match'
                verify = ''
        
        if not existing_user and not usernameError and not passwordError and not verifyError:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        else:
            return render_template('signup.html', usernameError=usernameError, passwordError=passwordError,
            verifyError=verifyError)

    return render_template('signup.html', title='Signup')


@app.route('/logout')
def logout():

    del session['username']
    return redirect('/blog')


@app.route('/')
def index():
    
    users = User.query.all()
    return render_template('index.html', title='Blog Users', users=users)

@app.route('/blog')
def blog():
    
    blogs = Blog.query.all()
    blog_id = request.args.get('id')
    user_id = request.args.get('user')
    
    if blog_id:
        blog= Blog.query.get(blog_id)
        return render_template('blog_page.html',title='Blog Posts', blog=blog)
    if user_id:
        blogs = Blog.query.filter_by(owner_id=user_id)
        return render_template('user.html',title='Blog Posts', blogs=blogs)
    
    return render_template('main_page.html', blogs=blogs)


@app.route('/newpost', methods=['POST','GET'])
def newpost():

    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']
        owner = User.query.filter_by(username=session['username']).first()

        titleError = ''
        bodyError = ''

        #Title Validation
        if not blog_title:
            titleError = 'Please fill in the title'

        #Body Validation
        if not blog_body:
            bodyError = 'Please fill in the body'
            
        if not titleError and not bodyError:
            new_blog = Blog(blog_title, blog_body, owner)
            db.session.add(new_blog)
            db.session.commit()
            return redirect('/blog?id='+ str(new_blog.id))
               
        else:
            return render_template('new_post.html', title='New Blog', blog_title=blog_title,
            titleError=titleError, blog_body=blog_body, bodyError=bodyError)
    else:
        return render_template('new_post.html',title='New Blog')


if __name__ == '__main__':
    app.run()