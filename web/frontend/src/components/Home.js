import React from 'react';
import Search from './Search';
import Record from './Record';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faMicrophone, faSearch } from '@fortawesome/free-solid-svg-icons';
import { useNavigate } from 'react-router-dom';

function Home() {
    const navigate = useNavigate();

    const handleLogout = () => {
        navigate('/'); // Navigate to the root page on logout
    };

    return (
        <div>
            <nav className="navbar navbar-expand-lg navbar-dark bg-dark">
                <div className="container">
                    <a className="navbar-brand" href="#">BeatBuddy</a>
                    <button className="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
                        <span className="navbar-toggler-icon"></span>
                    </button>
                    <div className="collapse navbar-collapse" id="navbarNav">
                        <ul className="navbar-nav w-100 justify-content-end">
                            <li className="nav-item">
                                <button className="nav-link btn btn-link" style={{ color: 'white' }} onClick={handleLogout}>Logout</button>
                            </li>
                        </ul>
                    </div>
                </div>
            </nav>
            <div className="container mt-5">
                <h1 className="mb-3 text-center">Welcome to Your Music App</h1>
                <div className="row">
                    <div className="col-md-6 mb-4">
                        <div className="card">
                            <div className="card-body">
                                <h2 className="card-title"><FontAwesomeIcon icon={faSearch} /> Search Songs</h2>
                                <Search />
                            </div>
                        </div>
                    </div>
                    <div className="col-md-6 mb-4">
                        <div className="card">
                            <div className="card-body">
                                <h2 className="card-title"><FontAwesomeIcon icon={faMicrophone} /> Record Audio</h2>
                                <Record />
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default Home;
// Compare this snippet from web/frontend/src/components/Search.js: