import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import 'bootstrap/dist/css/bootstrap.min.css';
import './Login.css'; // Import custom CSS
import config from '../Config.json';

function Login() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();

        try {
            const res = await axios.post(config.python_url+'/login', {
                username,
                password
            });

            if (res.data && res.data.access_token) {
                localStorage.setItem('token', res.data.access_token); // Store the token in localStorage
                console.log('Login successful and token stored');
                navigate('/home');
            } else {
                console.error('No token received');
                alert('Login failed, no token received');
            }
        } catch (error) {
            console.error('Login failed:', error);
            alert('Login failed, check console for more information');
        }
    };
    return (
        <div className="login-container">
            <div className="login-card">
                <h2 className="login-title">Login</h2>
                <form onSubmit={handleSubmit} className="login-form">
                    <div className="form-group">
                        <label htmlFor="username" className="form-label">
                            Username
                        </label>
                        <input
                            type="text"
                            className="form-control"
                            id="username"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            placeholder="Enter username"
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="password" className="form-label">
                            Password
                        </label>
                        <input
                            type="password"
                            className="form-control"
                            id="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="Enter password"
                            required
                        />
                    </div>

                    <button type="submit" className="btn btn-primary login-btn">
                        Login
                    </button>
                </form>
            </div>
        </div>
    );
}

export default Login;
