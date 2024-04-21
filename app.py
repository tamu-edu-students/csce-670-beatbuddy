from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, create_access_token
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from werkzeug.utils import secure_filename
from flask.helpers import send_from_directory
import os
from flask_cors import CORS
import pandas as pd
from sqlalchemy.sql import func
from web.backend.search_via_text.colbert import search_documents
# Load CSV file into a DataFrame
current_directory = os.getcwd()
db_path=current_directory+r"/instance/beatbuddy.db"
# Initialize app
app = Flask(__name__,static_folder="web/frontend/build",static_url_path="")
CORS(app, origins=['*'])
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path #'sqlite:///beatbuddy.db'
app.config['SECRET_KEY'] = 'your_secret_key'
# Setup database
db = SQLAlchemy(app)
jwt = JWTManager(app)


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
    youtube_link = db.Column(db.String(200), nullable=True)
    nearest_songs = db.Column(db.String(200), nullable=True)
    ratings = db.relationship('Rating', backref='song', lazy=True)

class Rating(db.Model):
    __tablename__ = 'ratings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    song_id = db.Column(db.Integer, db.ForeignKey('songs.id'), nullable=False)
    rating = db.Column(db.Float, nullable=False)

# # Get the current directory
# current_directory = os.path.dirname(os.path.abspath(__file__))

# # Construct the full path to the CSV file
# csv_file_path = os.path.join(current_directory, 'preprocessing', 'updated_dataset_with_youtube_urls.csv')

# # Load CSV file into a DataFrame
# df = pd.read_csv(csv_file_path)[:20]

# # Open Flask application context
# with app.app_context():
#     db.create_all()
#     # Iterate over rows in the DataFrame
#     for index, row in df.iterrows():
#         # Extract data from the DataFrame row
#         title = row['track_name']
#         artist = row['artists']
#         album = row['album_name']
#         youtube_link = row['YouTube URL']
#         print(youtube_link)
#         # Create a new Song object and add it to the database
#         new_song = Song(title=title, artist=artist, album=album, youtube_link=youtube_link)
#         db.session.add(new_song)
#         db.session.commit()

# User loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    return send_from_directory(app.static_folder,"index.html")

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    user = User.query.filter_by(username=username, password=password).first()
    if user:
        access_token = create_access_token(identity=username)
        login_user(user)
        return jsonify({"message": "Login successful", "access_token": access_token}), 200
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


@app.route('/all_songs', methods=['GET'])
def get_all_songs():

    songs = db.session.query(
        Song.id, Song.title, Song.artist, Song.album, Song.youtube_link,
        func.avg(Rating.rating).label('average_rating')
    ).outerjoin(Rating).group_by(Song.id).limit(10).all()

    songs_data = [{
        'id': song.id,
        'title': song.title,
        'artist': song.artist,
        'album': song.album,
        'youtube_link': song.youtube_link,
        'average_rating': float(song.average_rating) if song.average_rating else None
    } for song in songs]
    return jsonify(songs_data)

@app.route('/recommendations', methods=['GET'])
def get_recommendations():
    songs = db.session.query(
        Song.id, Song.title, Song.artist, Song.album, Song.youtube_link,
        func.avg(Rating.rating).label('average_rating')
    ).outerjoin(Rating).group_by(Song.id).limit(10).all()

    songs_data = [{
        'id': song.id,
        'title': song.title,
        'artist': song.artist,
        'album': song.album,
        'youtube_link': song.youtube_link,
        'average_rating': float(song.average_rating) if song.average_rating else None
    } for song in songs]
    return jsonify(songs_data)

@app.route('/search_via_clip', methods=['GET'])
def get_search_clip():
    print("audio check")
    file = request.files['file']
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join('uploads', filename))  # Ensure the 'uploads' folder exists
        return jsonify({'message': 'File uploaded successfully', 'filename': filename})

@app.route('/search_via_text', methods=['GET'])
def get_search_text():
    query = request.args.get('query')
    song_ids=search_documents(query)

    song_ids = [x + 1 for x in song_ids]

    try:
        songs = db.session.query(
            Song.id, Song.title, Song.artist, Song.album, Song.youtube_link,
            func.avg(Rating.rating).label('average_rating')
        ).filter(Song.id.in_(song_ids)).outerjoin(Rating).group_by(Song.id).all()
        songs = sorted(songs,key=lambda song: song_ids.index(song.id))
        songs_data = [{
            'id': song.id,
            'title': song.title,
            'artist': song.artist,
            'album': song.album,
            'youtube_link': song.youtube_link,
            'average_rating': float(song.average_rating) if song.average_rating else None
        } for song in songs]
        print(songs_data)
    except Exception as e:
        print(e.args)

    return jsonify(songs_data)

@app.route('/rate_song', methods=['POST'])
@jwt_required()
def rate_song():
    user_id = get_jwt_identity()
    song_id = request.json.get('song_id')
    rating_value = request.json.get('rating')

    # Check if the rating already exists
    rating = Rating.query.filter_by(user_id=user_id, song_id=song_id).first()
    if rating:
        rating.rating = rating_value
    else:
        rating = Rating(user_id=user_id, song_id=song_id, rating=rating_value)
        db.session.add(rating)

    db.session.commit()
    return jsonify({'message': 'Rating updated successfully'}), 200

if __name__ == '__main__':
    if not os.path.exists('beatbuddy.db'):
        with app.app_context():
            db.create_all()
    app.run()