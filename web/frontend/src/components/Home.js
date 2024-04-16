import React from 'react';
import Search from './Search';
import Record from './Record';
import Songs from './Songs';  // Import Songs component
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faMicrophone, faSearch } from '@fortawesome/free-solid-svg-icons';
import { useNavigate } from 'react-router-dom';
import 'bootstrap/dist/css/bootstrap.min.css';
import './Home.css';

function Home() {
    const navigate = useNavigate();

    const handleLogout = () => {
        navigate('/');
    };

    return (
        <div className="home-container">
            <nav className="navbar navbar-expand-lg navbar-dark bg-dark">
                <div className="container">
                    <a className="navbar-brand" href="#">BeatBuddy</a>
                    <button
                        className="navbar-toggler"
                        type="button"
                        data-toggle="collapse"
                        data-target="#navbarNav"
                        aria-controls="navbarNav"
                        aria-expanded="false"
                        aria-label="Toggle navigation"
                    >
                        <span className="navbar-toggler-icon"></span>
                    </button>
                    <div className="collapse navbar-collapse justify-content-end" id="navbarNav">
                        <ul className="navbar-nav">
                            <li className="nav-item">
                                <button
                                    className="nav-link btn btn-link logout-btn"
                                    onClick={handleLogout}
                                >
                                    Logout
                                </button>
                            </li>
                        </ul>
                    </div>
                </div>
            </nav>
            <div className="container mt-5">
                <h1 className="mb-4 text-center main-title">Welcome to BeatBuddy</h1>
                <div className="row justify-content-center">
                    <div className="col-lg-5 mb-4">
                        <div className="card feature-card h-100">
                            <div className="card-body">
                                <h2 className="card-title">
                                    <FontAwesomeIcon icon={faSearch} /> Search Songs
                                </h2>
                                <Search />
                            </div>
                        </div>
                    </div>
                    <div className="col-lg-5 mb-4">
                        <div className="card feature-card h-100">
                            <div className="card-body text-center position-relative">
                                <h2 className="card-title">
                                    <FontAwesomeIcon icon={faMicrophone} /> Record Audio
                                </h2>
                                <div className="record-container d-flex justify-content-center align-items-center">
                                    <Record />
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <Songs />  {/* Render Songs component here */}
            </div>
        </div>
    );
}

export default Home;
