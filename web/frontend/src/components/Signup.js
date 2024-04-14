import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate} from 'react-router-dom'; // Import useHistory

function Signup({ onSignup }) {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [email, setEmail] = useState('');
    const navigate = useNavigate();  // For navigation

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const res = await axios.post('http://localhost:5000/signup', { username, password, email });
            if (res.data) {
                console.log('Signup successful:', res.data);
                // onSignup();  // Update the parent state
                navigate('/home');
            }
        } catch (error) {
            console.error('Signup failed:', error);
        }
    };

    return (
        <div className="container mt-5">
            <form onSubmit={handleSubmit} className="card p-4 col-md-4 offset-md-4">
                <div className="mb-3">
                    <label htmlFor="username" className="form-label">Username</label>
                    <input
                        type="text"
                        className="form-control"
                        id="username"
                        value={username}
                        onChange={e => setUsername(e.target.value)}
                        placeholder="Enter username"
                        required
                    />
                </div>
                <div className="mb-3">
                    <label htmlFor="password" className="form-label">Password</label>
                    <input
                        type="password"
                        className="form-control"
                        id="password"
                        value={password}
                        onChange={e => setPassword(e.target.value)}
                        placeholder="Enter password"
                        required
                    />
                </div>
                <div className="mb-3">
                    <label htmlFor="email" className="form-label">Email</label>
                    <input
                        type="email"
                        className="form-control"
                        id="email"
                        value={email}
                        onChange={e => setEmail(e.target.value)}
                        placeholder="Enter email"
                        required
                    />
                </div>
                <button type="submit" className="btn btn-primary">Sign Up</button>
            </form>
        </div>
    );
}

export default Signup;