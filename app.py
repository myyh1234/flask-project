import os
from flask import Flask, request, render_template, redirect, session, flash, url_for
from model import db, User, Post, Comment

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def home():
    if 'username' in session:
        username = session['username']
        flash('Hello, ' + username)
        return render_template('home.html')
    else:
        flash('로그인하세요', '')
        return redirect('/login/')

@app.route('/signup/', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username:
            return "사용자 이름이 입력되지 않았습니다"
        else:
            usertable = User()
            usertable.username = username
            usertable.password = password

            db.session.add(usertable)
            db.session.commit()
            return "회원가입 성공"
    else:
        return render_template('signup.html')

@app.route('/login/', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not (username and password):
            return "사용자 이름이 입력되지 않았습니다"
        else:
            user = User.query.filter_by(username=username).first()
            if user:
                if user.password == password:
                    session['username'] = username
                    return redirect('/')
                else:
                    return "비밀번호가 다릅니다"
            else:
                return "사용자가 존재하지 않습니다"
    else:
        return render_template('login.html')

@app.route('/logout/', methods=['POST', 'GET'])
def logout():
    session.pop('username', None)
    return redirect('/')  

@app.route('/post/', methods=['POST', 'GET'])
def post():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')

        if not(title and content):
            return "입력되지 않은 정보가 있습니다."
        else:
            posttable = Post()
            posttable.title = title
            posttable.content = content

            db.session.add(posttable)
            db.session.commit()
            return redirect('/post_list/')
    else:
        return render_template('post.html')
    
@app.route('/post_list/')
def post_list():
    post_list = Post.query.order_by(Post.datetime.asc())

    return render_template("post_list.html", post_list=post_list)

@app.route('/detail/<int:post_id>')
def detail(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post_detail.html', post=post)

@app.route('/delete/<int:post_id>')
def delete(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect('/post_list/')

@app.route('/detail/<int:post_id>/comment/', methods=['GET', 'POST'])
def comment(post_id):
    if request.method == 'POST':
        content = request.form.get('content')
        
        post = Post.query.get_or_404(post_id)
        comment = Comment()
        comment.content = content
        comment.post = post
        comment.post_id = post_id

        db.session.add(comment)
        db.session.commit()
        return redirect(url_for('detail', post_id=post_id))
    else:
        return render_template('comment.html')

if __name__ == '__main__':
    with app.app_context():
        basedir = os.path.abspath(os.path.dirname(__file__))
        dbfile = os.path.join(basedir, 'db.sqlite')

        app.config['SECRET_KEY'] = 'ICEWALL'
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + dbfile
        app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        db.init_app(app)
        db.app = app
        db.create_all()

        app.run(host='127.0.0.1', port=5000, debug=True)