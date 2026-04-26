import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { FaEnvelope, FaLock, FaSignInAlt, FaPlane } from 'react-icons/fa';
import { GoogleLogin } from '@react-oauth/google';
import { toast } from 'react-toastify';
import { useAuth } from '../context/AuthContext';
import '../styles/Auth.css';

const Login = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});
  
  const { login, loginWithGoogle } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  
  const from = location.state?.from?.pathname || '/';

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    setErrors(prev => ({ ...prev, [name]: '' }));
  };

  const validate = () => {
    const newErrors = {};
    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Invalid email format';
    }
    if (!formData.password) {
      newErrors.password = 'Password is required';
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;

    setLoading(true);
    const result = await login(formData.email, formData.password);
    setLoading(false);

    if (result.success) {
      toast.success('Login successful! Welcome back.');
      navigate(from, { replace: true });
    } else {
      toast.error(result.error);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-container">
        <div className="auth-left">
          <div className="auth-branding">
            <FaPlane className="brand-icon" />
            <h1>Travel Planner</h1>
            <p>Your journey begins here</p>
          </div>
          <div className="auth-features">
            <div className="feature">
              <span className="feature-icon">🎯</span>
              <span>AI-Powered Recommendations</span>
            </div>
            <div className="feature">
              <span className="feature-icon">💰</span>
              <span>Smart Budget Planning</span>
            </div>
            <div className="feature">
              <span className="feature-icon">🗺️</span>
              <span>50+ Destinations</span>
            </div>
          </div>
        </div>

        <div className="auth-right">
          <div className="auth-form-container">
            <h2>Welcome Back</h2>
            <p className="auth-subtitle">Sign in to access your saved trips and preferences</p>

            <form onSubmit={handleSubmit} className="auth-form">
              <div className={`form-group ${errors.email ? 'error' : ''}`}>
                <label htmlFor="email">
                  <FaEnvelope /> Email Address
                </label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  placeholder="Enter your email"
                  autoComplete="email"
                />
                {errors.email && <span className="error-message">{errors.email}</span>}
              </div>

              <div className={`form-group ${errors.password ? 'error' : ''}`}>
                <label htmlFor="password">
                  <FaLock /> Password
                </label>
                <input
                  type="password"
                  id="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  placeholder="Enter your password"
                  autoComplete="current-password"
                />
                {errors.password && <span className="error-message">{errors.password}</span>}
              </div>

              <button type="submit" className="auth-btn" disabled={loading}>
                {loading ? (
                  <span className="loading-spinner-small"></span>
                ) : (
                  <>
                    <FaSignInAlt /> Sign In
                  </>
                )}
              </button>
            </form>

            <div className="auth-divider">
              <span>or continue as</span>
            </div>

            {process.env.REACT_APP_GOOGLE_CLIENT_ID && (
              <div style={{ marginBottom: '1rem' }}>
                <GoogleLogin
                  onSuccess={async (credentialResponse) => {
                    if (!credentialResponse?.credential) {
                      toast.error('Google credential was not received');
                      return;
                    }
                    const result = await loginWithGoogle(credentialResponse.credential);
                    if (result.success) {
                      toast.success('Logged in with Google successfully!');
                      navigate(from, { replace: true });
                    } else {
                      toast.error(result.error);
                    }
                  }}
                  onError={() => toast.error('Google sign-in failed')}
                />
              </div>
            )}

            <Link to="/" className="guest-btn">
              Browse as Guest
            </Link>

            <p className="auth-switch">
              Don't have an account? <Link to="/register">Create one</Link>
            </p>

            <div className="demo-credentials">
              <p><strong>Demo Admin:</strong> admin@travelplanner.com / admin123</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
