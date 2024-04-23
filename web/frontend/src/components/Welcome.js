import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import 'bootstrap/dist/css/bootstrap.min.css';
import './Welcome.css';

function Welcome() {
    const fullText = "Welcome to BeatBuddy";
    const [displayedText, setDisplayedText] = useState("");
    const [isErasing, setIsErasing] = useState(false);

    useEffect(() => {
        let currentText = "";
        const typeWriter = () => {
            if (!isErasing) {
                currentText = fullText.slice(0, currentText.length + 1);
                setDisplayedText(currentText);
                if (currentText === fullText) {
                    setTimeout(() => setIsErasing(true), 2000); // pause before erasing
                }
            } else {
                currentText = fullText.slice(0, currentText.length - 1);
                setDisplayedText(currentText);
                if (currentText === '') {
                    setIsErasing(false);
                }
            }
        };

        const timerId = setInterval(typeWriter, 150);

        return () => clearInterval(timerId);
    }, [fullText, isErasing]);

    return (
        <div className="vh-100 d-flex flex-column align-items-center justify-content-center bg-dark text-white">
    <div className="typewriter mb-4">
        <h1>{displayedText}</h1>
    </div>
    <p className="lead">Discover, share, and connect with music that moves you.</p>
    <div className="btn-group mt-3" role="group" aria-label="Basic example">
        <Link to="/login" className="btn btn-primary btn-lg">Log In</Link>
        <Link to="/signup" className="btn btn-secondary btn-lg">Sign Up</Link>
    </div>
</div>


    );
}

export default Welcome;
