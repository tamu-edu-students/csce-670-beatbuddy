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
import random
import ast
from web.backend.search_via_music.fingerprint_generator import read_audio, fingerprint
from datetime import timedelta
from sqlalchemy import case, desc

from itertools import groupby
from operator import itemgetter
import pandas as pd
from time import time
from web.backend.search_via_text.colbert import search_documents

from itertools import groupby
from pydub import AudioSegment

 #Load CSV file into a DataFrame
current_directory = os.getcwd()
db_path=current_directory+r"/instance/beatbuddy.db"
# Initialize app
#app = Flask(__name__,static_folder="web/frontend/build",static_url_path="")
app=Flask(__name__)
CORS(app, origins=['*'])
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path #'sqlite:///beatbuddy.db'
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = './web/backend/uploads'
app.config['JWT_EXPIRATION_DELTA'] = timedelta(days=7) 
# Setup database
db = SQLAlchemy(app)
jwt = JWTManager(app)


recc_data = pd.read_excel("recommended_songs_new_songsdb.xlsx", engine = "openpyxl")
knn_recc_data = pd.read_excel("knn_recommended_songs_new_songsdb.xlsx", engine = "openpyxl")


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
    fingerprints = db.relationship('Fingerprint', backref='song', lazy=True)

class Rating(db.Model):
    __tablename__ = 'ratings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    song_id = db.Column(db.Integer, db.ForeignKey('songs.id'), nullable=False)
    rating = db.Column(db.Float, nullable=False)

class Fingerprint(db.Model):
    __tablename__ = 'fingerprints'
    id = db.Column(db.Integer, primary_key=True)
    song_id = db.Column(db.Integer, db.ForeignKey('songs.id'), nullable=False)
    hash = db.Column(db.String(255), nullable=False)
    offset = db.Column(db.Integer, nullable=False)

songs_data = []
# User loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    #return send_from_directory(app.static_folder,"index.html")
    return "Beatbuddy Python API"


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

    return "Signup Python API"

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/upload_audio', methods=['POST'])
def upload_audio():
    print("Uploading audio")
    print("Request received")
    # print(request.files)
    # if 'audio' not in request.files:
    #     return jsonify({'error': 'No audio file part'}), 400
    
    audio = request.files['file']
    print("audioFIleName: " + str(audio.filename))
    if audio.filename == '':
        return jsonify({'error': 'No selected audio file'}), 400
    if audio:
        filename = secure_filename(audio.filename)
        print(filename)
        file_path = os.path.join('./web/backend/uploads', filename)
        print(file_path)
        audio.save(file_path)
        return jsonify({'message': 'Audio file uploaded successfully', 'path': file_path}), 200
    else:
        return jsonify({'error': 'Invalid file format or extension'}), 400


@app.route('/all_songs', methods=['GET'])
@jwt_required()
def get_all_songs():
    user_name = get_jwt_identity()
    user_id = User.query.filter_by(username=user_name).first().id
    print(user_id)
    user_rated_songs = db.session.query(
    Song.id, Song.title, Song.artist, Song.album, Song.youtube_link,
    Rating.rating.label('user_rating'),
    func.avg(Rating.rating).over(partition_by=Song.id).label('average_rating')
    ).join(Rating, Rating.song_id == Song.id).filter(Rating.user_id == user_id).order_by(desc('user_rating')).limit(20)

    songs_data = [{
        'id': song.id,
        'title': song.title,
        'artist': song.artist,
        'album': song.album,
        'youtube_link': song.youtube_link,
        'average_rating': float(song.average_rating) if song.average_rating else None
    } for song in user_rated_songs]
    print(songs_data)
    return jsonify(songs_data)

# @app.route('/recommendations', methods=['GET'])
# def get_recommendations():
#     songs = db.session.query(
#         Song.id, Song.title, Song.artist, Song.album, Song.youtube_link,
#         func.avg(Rating.rating).label('average_rating')
#     ).outerjoin(Rating).group_by(Song.id).limit(10).all()

#     songs_data = [{
#         'id': song.id,
#         'title': song.title,
#         'artist': song.artist,
#         'album': song.album,
#         'youtube_link': song.youtube_link,
#         'average_rating': float(song.average_rating) if song.average_rating else None
#     } for song in songs]
#     return jsonify(songs_data)



def find_matches_in_database(hashes, csv_file_path = "./web/backend/preprocessing/optimized_audio_fingerprint_database.csv", batch_size=1000):
    # Load the CSV data
    df = pd.read_csv(csv_file_path)
    batch_size = 1000
    # Prepare the mapper from your hashes
    mapper = {}
    for hsh, offset in hashes:
        upper_hash = hsh.upper()
        if upper_hash in mapper:
            mapper[upper_hash].append(offset)
        else:
            mapper[upper_hash] = [offset]
    values = list(mapper.keys())
    
    # Initialize results and deduplication dict
    results = []
    dedup_hashes = {}
    t = time()
    # Iterate through the DataFrame
    for index in range(0, len(hashes), batch_size):
        batch_hashes = values[index:index + batch_size]
        db_matches = df[df['Hash'].str.upper().isin(batch_hashes)]
        
        for _, row in db_matches.iterrows():
            hsh, sid, db_offset = row['Hash'].upper(), row['SongID'], row['Offset']
            if sid not in dedup_hashes.keys():
                dedup_hashes[sid] = 1
            else:
                dedup_hashes[sid] += 1

            for song_sampled_offset in mapper[hsh]:
                results.append((sid, db_offset - song_sampled_offset))

    query_time = time() - t
    print(f"Query time: {query_time}")
    t = time()
    results = align_matches(results, dedup_hashes, len(hashes), df)
    print(f"Alignment time: {time() - t}")
    return results


def align_matches(matches, dedup_hashes, queried_hashes, df_songs, topn=5, default_fs=44100, window_size=4096, overlap_ratio=0.5):
    
    sorted_matches = sorted(matches, key=itemgetter(0, 1))
    counts = [(*key, len(list(group))) for key, group in groupby(sorted_matches, key=itemgetter(0, 1))]
    
    songs_matches = sorted(
        [max(list(group), key=itemgetter(2)) for key, group in groupby(counts, key=itemgetter(0))],
        key=itemgetter(2), reverse=True
    )
    # print(songs_matches)
    songs_result = [song_id for song_id, _, _ in songs_matches[:min(len(songs_matches), topn)]]
    return songs_result

# songs_data = []
@app.route('/search_via_clip', methods=['GET'])
def get_search_clip():
    upload_folder = app.config['UPLOAD_FOLDER']
    files = os.listdir(upload_folder)
    if files:  # Check if any files are present in the folder
        filename = files[0]  # Assuming only one file is present
        if filename.endswith(".mp3") or filename.endswith(".wav"):
            original_path = os.path.join(upload_folder, filename)
            final_path = os.path.join(upload_folder, 'recording.mp3')

            # Open the audio file using a context manager
            with open(original_path, 'rb') as f:
                audio = AudioSegment.from_file(f)
                try:
                    audio.export(final_path, format='mp3')
                    # os.remove(original_path)
                except:
                    audio.export(final_path, format='mp4')

            channels, samplerate = read_audio(final_path)

            # print(channels, samplerate)
            hashes = set()
            for channel in channels:
                channel_fingerprints = fingerprint(channel, Fs=samplerate)
                hashes.update(channel_fingerprints)
            # print("Done generating hashes", len(hashes))
            song_ids = find_matches_in_database(hashes)
            song_ids = [x + 1 for x in song_ids]
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
            os.remove(final_path)
            # Check if the files exist before removing them

    return jsonify(songs_data)






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
        songs_data_text = [{
            'id': song.id,
            'title': song.title,
            'artist': song.artist,
            'album': song.album,
            'youtube_link': song.youtube_link,
            'average_rating': float(song.average_rating) if song.average_rating else None
        } for song in songs]
        # print(songs_data_text)
    except Exception as e:
        print(e.args)

    return jsonify(songs_data_text)

@app.route('/recommendations', methods=['GET'])
@jwt_required()
def get_recommendations():
    # if request.method == "GET":
    user_name = get_jwt_identity()
    # print(user_name)
    user = User.query.filter_by(username=user_name).first()
    if user:
        user_id= user.id
    else:
        user_id= None
    # print(user_name,user_id)
    if user_id in recc_data['User']:
        u_id = user_id       
    else:
        u_id = random.randint(0, 1999)
    # print(u_id-1)
    mf_song_ids = recc_data.loc[recc_data['User']==u_id-1, "Recommended Songs"].values[0]
    knn_song_ids = knn_recc_data.loc[knn_recc_data['User']==u_id-1, "Recommended Songs"].values[0]
    mf_song_ids = ast.literal_eval(mf_song_ids)
    # mf_song_ids = random.sample(mf_song_ids, k=5)
    mf_song_ids = random.sample(mf_song_ids, k=min(5, len(mf_song_ids)))

    # print(mf_song_ids)
    knn_song_ids = ast.literal_eval(knn_song_ids)
    song_ids = mf_song_ids
    song_ids = knn_song_ids + mf_song_ids
    song_ids = [id + 1 for id in song_ids]
    try:
        songs = db.session.query(
        Song.id, Song.title, Song.artist, Song.album, Song.youtube_link,
        func.avg(Rating.rating).label('average_rating'),
        func.avg(
            case(
                (Rating.user_id == user_id, Rating.rating),
                else_=0
            )
        ).label('user_rating')
    ).filter(Song.id.in_(song_ids)).outerjoin(Rating).group_by(Song.id).all()
        # Sorting songs based on their order in song_ids
        songs = sorted(songs, key=lambda song: song_ids.index(song.id))
        # print(songs)
        songs_data = [{
            'id': song.id,
            'title': song.title,
            'artist': song.artist,
            'album': song.album,
            'youtube_link': song.youtube_link,
            'average_rating': float(song.average_rating) if song.average_rating else None,
            'user_rating': float(song.user_rating) if song.user_rating else None
        } for song in songs]
        # print(songs_data)
    except Exception as e:
        print(e.args)
        songs_data = []

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
        print("done")

    db.session.commit()
    return jsonify({'message': 'Rating updated successfully'}), 200



def load_songs():
    songs_df = pd.read_csv('./preprocessing/SONGS_DB.csv', encoding='utf-8')
    for index, row in tqdm(songs_df.iterrows()):
        song = Song(
            title=row['track_name'],
            artist=row['artists'],
            album=row['album_name'],  # Using .get() to handle missing data gracefully
            youtube_link=row['YouTube URL']
        )
        db.session.add(song)
    db.session.commit()

def load_finger_prints():
    # Load the CSV file into a DataFrame
    print("Loading data...")
    df = pd.read_csv('./preprocessing/optimized_audio_fingerprint_database.csv', encoding='utf-8', usecols=['SongID', 'Hash', 'Offset'])

    # # Filter rows where SongID <= 250
    # print("Filtering data...")
    # filtered_df = Fingerprint_df[Fingerprint_df['SongID'] > 250]

    # Batch size for bulk insert
    batch_size = 10000  # Adjust based on memory and performance considerations
    total_rows = len(df)
    print(f"Total rows to process: {total_rows}")

    try:
        # Process in chunks
        for start in tqdm(range(0, total_rows, batch_size)):
            end = min(start + batch_size, total_rows)
            batch = df.iloc[start:end]
            # Create a list of Fingerprint objects to bulk insert
            fingerprints = [
                Fingerprint(
                    song_id=row['SongID'],
                    hash=row['Hash'],
                    offset=row['Offset']
                ) for index, row in batch.iterrows()
            ]
            # Bulk insert using SQLAlchemy's bulk_save_objects or similar method
            db.session.bulk_save_objects(fingerprints)
            db.session.commit()
            print(f"Processed {end} of {total_rows}")
    except SQLAlchemyError as e:
        print(f"An error occurred: {e}")
        db.session.rollback()

# Main application logic
if __name__ == '__main__':
    # Create or recreate the database
    with app.app_context():
        db.create_all()
        if(Song.query.count() == 0):
            print("Songs table is empty")
            load_songs()
        # if(Fingerprint.query.count() == 0):
        #     print("Finerprints table is empty")
        #     load_finger_prints()

    app.run(host="0.0.0.0",debug=True)
