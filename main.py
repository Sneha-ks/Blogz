from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:lc101@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))

    def __init__(self,title,body):
        self.title = title
        self.body = body

@app.route('/blog')
def index():

    blog_id = request.args.get('id')
    if blog_id:
        return redirect('/blogpage')
    else:
        blogs = Blog.query.all()
        return render_template('main_page.html',title='Build a Blog', blogs=blogs)


@app.route('/newpost', methods=['POST','GET'])
def newpost():

    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']

        titleError = ''
        bodyError = ''

        #Title Validation
        if not blog_title:
            titleError = 'Please fill in the title'

        #Body Validation
        if not blog_body:
            bodyError = 'Please fill in the body'
            
        if not titleError and not bodyError:
            new_blog = Blog(blog_title, blog_body)
            db.session.add(new_blog)
            db.session.commit()
            return redirect('/blog')
        else:
            return render_template('new_post.html', title='New Blog', blog_title=blog_title,
            titleError=titleError, blog_body=blog_body, bodyError=bodyError)
    else:
        return render_template('new_post.html',title='New Blog')

@app.route('/blogpage')
def display():
    
    blog_id = int(request.args.get('id'))
    blog= Blog.query.filter_by(id=blog_id).first()
    return render_template('blog_page.html', blog=blog)

if __name__ == '__main__':
    app.run()