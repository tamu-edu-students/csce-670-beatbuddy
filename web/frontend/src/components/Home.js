import React, { useState } from 'react';
import Search from './Search';
import Record from './Record';
import SongList from './SongList'; // Importing SongList which replaces Songs and Recommendations
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faMicrophone, faSearch } from '@fortawesome/free-solid-svg-icons';
import { useNavigate } from 'react-router-dom';
import 'bootstrap/dist/css/bootstrap.min.css';
import './Home.css';

function Home() {
    const navigate = useNavigate();
    const [activeView, setActiveView] = useState('songs'); // Default view is 'songs'
    const [query, setQuery] = React.useState('');
    const handleSetActiveView = (view) => {
        setActiveView(view);
    };

    const handleSearchTextTriggered = (query) => {
        console.log('Received query: ', query);
        setQuery(query);
        setActiveView('search text results'); // Change view to show search results
    };
    const handleSearchClipTriggered = () => {
        setActiveView('search clip results'); // Change view to show search results
    };

    const handleLogout = () => {
        navigate('/');
    };

    return (
        <div className="home-container">
            <nav className="navbar navbar-expand-lg navbar-dark bg-dark">
                <div className="container">
                    <a className="navbar-brand" href="#">BeatBuddy</a>
                    <button className="navbar-toggler" type="button" data-toggle="collapse"
                        data-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false"
                        aria-label="Toggle navigation">
                        <span className="navbar-toggler-icon"></span>
                    </button>
                    <div className="collapse navbar-collapse justify-content-end" id="navbarNav">
                        <ul className="navbar-nav">
                            <li className="nav-item">
                                <button className="nav-link btn btn-link logout-btn" onClick={handleLogout}>
                                    Logout
                                </button>
                            </li>
                        </ul>
                    </div>
                </div>
            </nav>

            <div className="container mt-5">
            <div className="row justify-content-center">
                <div className="col-md-6 col-lg-5 mb-4">  {/* Adjusted column sizing for better responsiveness */}
                    <div className="card feature-card h-100 shadow">  {/* Optional shadow for better depth perception */}
                        <div className="card-body">
                            <h2 className="card-title">
                                <FontAwesomeIcon icon={faSearch} /> Search Songs
                            </h2>
                            <Search onSearchTextTrigger={handleSearchTextTriggered} />
                        </div>
                    </div>
                </div>
                <div className="col-md-6 col-lg-5 mb-4"> 
                    <div className="card feature-card h-100 shadow">
                        <div className="card-body text-center">
                        <FontAwesomeIcon icon={faMicrophone} />
                            
                            <div className="record-container d-flex justify-content-center align-items-center h-100">
                            
                                <Record onSearchClipTrigger={handleSearchClipTriggered}/>
                            </div>
                        </div>
                    </div>
                </div>
            </div>


                <div className="container mt-5">
                    <div className="text-center mb-4">
                        <button className={`btn ${activeView === 'songs' ? 'btn-primary' : 'btn-outline-primary'}`}
                                onClick={() => handleSetActiveView('songs')}>
                            Songs
                        </button>
                        <button className={`btn ${activeView === 'recommendations' ? 'btn-primary' : 'btn-outline-primary'} ml-2`}
                                onClick={() => handleSetActiveView('recommendations')}>
                            Recommendations for You
                        </button>
                    </div>

                    {/* Conditional rendering based on activeView */}
                    {activeView === 'songs' && <SongList endpoint="all_songs" title="All Songs" />}
                    {activeView === 'recommendations' && <SongList endpoint="recommendations" title="Recommendations" />}
                    {activeView === 'search text results' && <SongList endpoint={`search_via_text?query=${query}`} title="Search Text Results" />}
                    {activeView === 'search clip results' && <SongList endpoint="search_via_clip" title="Search Clip Results" />}
                </div>
            </div>
        </div>
    );
}

export default Home;

