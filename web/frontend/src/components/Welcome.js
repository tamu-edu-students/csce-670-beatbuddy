import React from 'react';
import { Link } from 'react-router-dom';
import 'bootstrap/dist/css/bootstrap.min.css'; // Ensure Bootstrap CSS is imported

function Welcome() {
    return (
        <div className="vh-100 d-flex align-items-center justify-content-center bg-dark text-white">
            <div className="text-center">
                <h1 className="mb-4">Welcome to BeatBuddy</h1>
                <p className="lead mb-4">Discover, share, and connect with music that moves you.</p>
                <div className="btn-group" role="group" aria-label="Basic example">
                    <Link to="/login" className="btn btn-primary btn-lg">Log In</Link>
                    <Link to="/signup" className="btn btn-secondary btn-lg">Sign Up</Link>
                </div>
            </div>
        </div>
    );
}

export default Welcome;
