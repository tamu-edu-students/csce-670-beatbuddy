import React, { useState } from 'react';
import axios from 'axios';
import { Tooltip, OverlayTrigger } from 'react-bootstrap';

function Rating({ songId }) {
    const [rating, setRating] = useState(0);
    const [tooltip, showTooltip] = useState(false);

    const submitRating = async () => {
        try {
            const res = await axios.post(`http://localhost:5000/rate_song/${songId}`, { rating });
            showTooltip(true);
            setTimeout(() => showTooltip(false), 2000);  // Hide tooltip after 2 seconds
        } catch (error) {
            console.error('Rating failed:', error);
        }
    };

    const renderTooltip = (props) => (
        <Tooltip id="button-tooltip" {...props}>
            Rating submitted!
        </Tooltip>
    );

    return (
        <div className="rating-container">
            {[...Array(5)].map((star, index) => {
                index += 1;
                return (
                    <button
                        type="button"
                        key={index}
                        className={index <= rating ? "on" : "off"}
                        onClick={() => setRating(index)}
                    >
                        <span className="star">&#9733;</span>
                    </button>
                );
            })}
            <OverlayTrigger
                placement="right"
                delay={{ show: 250, hide: 400 }}
                overlay={renderTooltip}
                show={tooltip}
            >
                <button className="btn btn-primary" onClick={submitRating}>Rate</button>
            </OverlayTrigger>
        </div>
    );
}

export default Rating;
