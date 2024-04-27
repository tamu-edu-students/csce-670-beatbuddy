import React, { useState, useEffect } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faStar as fullStar } from '@fortawesome/free-solid-svg-icons';
import { faStar as emptyStar } from '@fortawesome/free-regular-svg-icons';
import config from "../Config.json"
function SongList({ endpoint, title }) {
    const [songs, setSongs] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    useEffect(() => {
        setIsLoading(true);
        const token = localStorage.getItem('token');
        if (token) {
            fetch(config.python_url+`/${endpoint}`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            })
            .then(response => response.json())
            .then(data => {
                setSongs(data);
                setIsLoading(false);
            })
            .catch(err => {
                console.error(`Error fetching songs from ${title}:`, err);
                setIsLoading(false);
            });
        } else {
            console.log('User not logged in.');
            setIsLoading(false);
        }
    }, [endpoint, title]);

    const handleRatingChange = (songId, rating, event) => {
        event.stopPropagation();
        const token = localStorage.getItem('token');
        console.log('Token: ', token);
        if (!token) {
            alert('Please log in to rate songs.');
            return;
        }

        fetch(config.python_url+'/rate_song', {
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
                    return { ...song, user_rating: rating };
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
        window.open(url, '_blank');
    };
    if (isLoading) {
        return <div className="container mt-5 text-center"><div className="spinner-border text-primary" role="status"><span className="sr-only">Loading...</span></div></div>;
    }

    if (!isLoading && songs.length === 0) {
        return <div className="container mt-5 text-center">No songs available. Please try again later.</div>;
    }
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
                                        icon={song.user_rating != null && song.user_rating >= num ? fullStar : emptyStar}
                                        onClick={(e) => handleRatingChange(song.id, num, e)}
                                        key={num}
                                        className="text-warning"
                                    />
                                ))}
                            </div>
                            <p className="small text-center">
                                User Rating: {song.user_rating ? song.user_rating.toFixed(1) : "Not Rated"}
                            </p>
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

export default SongList;
