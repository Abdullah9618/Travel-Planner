import React from 'react';
import { Link } from 'react-router-dom';
import { FaPlane, FaFacebook, FaTwitter, FaInstagram, FaEnvelope } from 'react-icons/fa';
import '../styles/Footer.css';

const Footer = () => {
  return (
    <footer className="footer">
      <div className="footer-container">
        <div className="footer-section">
          <div className="footer-logo">
            <FaPlane className="logo-icon" />
            <span>Travel Planner</span>
          </div>
          <p className="footer-description">
            Your AI-powered travel companion for exploring the beauty of Pakistan. 
            Plan your perfect trip with personalized recommendations.
          </p>
        </div>

        <div className="footer-section">
          <h4>Quick Links</h4>
          <ul className="footer-links">
            <li><Link to="/">Home</Link></li>
            <li><Link to="/login">Login</Link></li>
            <li><Link to="/register">Register</Link></li>
          </ul>
        </div>

        <div className="footer-section">
          <h4>Popular Destinations</h4>
          <ul className="footer-links">
            <li><Link to="/search?region=Gilgit%20Baltistan">Gilgit Baltistan</Link></li>
            <li><Link to="/search?region=KPK">KPK</Link></li>
            <li><Link to="/search?region=Punjab">Punjab</Link></li>
            <li><Link to="/search?region=Sindh">Sindh</Link></li>
          </ul>
        </div>

        <div className="footer-section">
          <h4>Contact Us</h4>
          <div className="footer-contact">
            <p><FaEnvelope /> info@travelplanner.pk</p>
          </div>
          <div className="social-icons">
            <a href="#facebook" aria-label="Facebook"><FaFacebook /></a>
            <a href="#twitter" aria-label="Twitter"><FaTwitter /></a>
            <a href="#instagram" aria-label="Instagram"><FaInstagram /></a>
          </div>
        </div>
      </div>

      <div className="footer-bottom">
        <p>&copy; 2026 Travel Planner Pakistan. All rights reserved.</p>
      </div>
    </footer>
  );
};

export default Footer;
