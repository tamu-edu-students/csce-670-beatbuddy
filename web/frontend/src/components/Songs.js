import React, { useState, useEffect } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faStar as fullStar } from '@fortawesome/free-solid-svg-icons';
import { faStar as emptyStar } from '@fortawesome/free-regular-svg-icons';

function Songs() {
    const [songs, setSongs] = useState([]);

    useEffect(() => {
        const token = localStorage.getItem('token');
        if (token) {
            fetch('http://localhost:5000/songs', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            })
            .then(response => response.json())
            .then(data => setSongs(data))
            .catch(err => console.error('Error fetching songs:', err));
        } else {
            console.log('User not logged in.');
        }
    }, []);

    const handleRatingChange = (songId, rating, event) => {
        event.stopPropagation(); // Prevents the link from being triggered when clicking on the star icons
        const token = localStorage.getItem('token');
        if (!token) {
            alert('Please log in to rate songs.');
            return;
        }

        fetch('http://localhost:5000/rate_song', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ song_id: songId, rating })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to update rating');
            }
            return response.json();
        })
        .then(data => {
            console.log(data.message);
            setSongs(songs.map(song => {
                if (song.id === songId) {
                    return { ...song, average_rating: rating };
                }
                return song;
            }));
        })
        .catch(err => {
            console.error('Error updating rating:', err);
            alert(err.message);
        });
    };

    const openYoutubeLink = (url) => {
        window.open(url, '_blank'); // Opens the YouTube link in a new tab
    };

    return (
        <div className="container mt-5">
            <div className="row justify-content-center">
                {songs.map(song => (
                    <div key={song.id} className="col-lg-4 mb-4" onClick={() => openYoutubeLink(song.youtube_link)}>
                        <div className="card feature-card h-100" style={{ cursor: "pointer" }}>
                            <div className="card-body">
                                <h3 className="card-title">{song.title}</h3>
                                <h4 className="text-muted">{song.artist}</h4>
                                <p className="small">{song.album}</p>
                                <div className="d-flex justify-content-center mb-2">
                                    {[1, 2, 3, 4, 5].map(num => (
                                        <FontAwesomeIcon
                                            icon={song.average_rating >= num ? fullStar : emptyStar}
                                            onClick={(e) => handleRatingChange(song.id, num, e)}
                                            key={num}
                                            className="text-warning"
                                        />
                                    ))}
                                </div>
                                <p className="small text-center">
                                    Average Rating: {song.average_rating ? song.average_rating.toFixed(1) : "Not Rated"}
                                </p>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}

export default Songs;
