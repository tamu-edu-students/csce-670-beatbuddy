from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
import os
from flask_cors import CORS

# Initialize app
app = Flask(__name__)
CORS(app, origins=['*'])
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///myapp.db'
app.config['SECRET_KEY'] = 'your_secret_key'
# Setup database
db = SQLAlchemy(app)



# Setup Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

# Models
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=True)
    ratings = db.relationship('Rating', backref='user', lazy=True)

class Song(db.Model):
    __tablename__ = 'songs'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    artist = db.Column(db.String(200), nullable=False)
    album = db.Column(db.String(200), nullable=True)
    ratings = db.relationship('Rating', backref='song', lazy=True)

class Rating(db.Model):
    __tablename__ = 'ratings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    song_id = db.Column(db.Integer, db.ForeignKey('songs.id'), nullable=False)
    rating = db.Column(db.Float, nullable=False)

# User loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    user = User.query.filter_by(username=username, password=password).first()
    if user:
        login_user(user)
        return jsonify({"message": "Login successful", "redirect": url_for('search')}), 200
    return jsonify({"message": "Login failed"}), 401  # Unauthorized access

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')  # In production, ensure this is hashed
        email = data.get('email')

        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            return jsonify({'message': 'Username or email already exists'}), 409

        new_user = User(username=username, password=password, email=email)
        db.session.add(new_user)
        db.session.commit()

        return jsonify({'message': 'User created successfully', 'userId': new_user.id}), 201  # Assuming id is auto-generated

    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    if request.method == 'POST':
        query = request.form['query']
        songs = Song.query.filter((Song.title.contains(query)) | (Song.artist.contains(query))).all()
        return render_template('search.html', results=songs)
    return render_template('search.html')

@app.route('/upload_audio', methods=['POST'])
# @login_required
def upload_audio():
    print("audio check")
    file = request.files['file']
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join('uploads', filename))  # Ensure the 'uploads' folder exists
        return jsonify({'message': 'File uploaded successfully', 'filename': filename})
    return jsonify({'message': 'No file provided'}), 400

@app.route('/rate_song/<int:song_id>', methods=['POST'])
@login_required
def rate_song(song_id):
    rating_value = float(request.form['rating'])
    existing_rating = Rating.query.filter_by(user_id=current_user.id, song_id=song_id).first()
    if existing_rating:
        existing_rating.rating = rating_value
    else:
        new_rating = Rating(user_id=current_user.id, song_id=song_id, rating=rating_value)
        db.session.add(new_rating)
    db.session.commit()
    return jsonify({'message': 'Rating updated successfully'})

if __name__ == '__main__':
    if not os.path.exists('myapp.db'):
        with app.app_context():
            db.create_all()
    app.run(port=5000, debug=True)