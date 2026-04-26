import React, { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  FaStar, FaMapMarkerAlt, FaCalendarAlt, FaShieldAlt, 
  FaCloud, FaHeart, FaShare, FaArrowLeft, FaHiking
} from 'react-icons/fa';
import { toast } from 'react-toastify';
import BudgetTable from '../components/BudgetTable';
import DestinationCard from '../components/DestinationCard';
import { destinationService, budgetService } from '../services/api';
import { useAuth } from '../context/AuthContext';
import '../styles/Destination.css';

const Destination = () => {
  const { id } = useParams();
  const { isAuthenticated, saveTrip } = useAuth();
  
  const [destination, setDestination] = useState(null);
  const [similarDestinations, setSimilarDestinations] = useState([]);
  const [budgetEstimate, setBudgetEstimate] = useState(null);
  const [selectedDays, setSelectedDays] = useState(3);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const fetchDestination = useCallback(async () => {
    setLoading(true);
    try {
      // Try to get by ID first, then by name
      const response = await destinationService.getAll();
      const allDestinations = response.data;
      
      let found = allDestinations.find(d => d.id === parseInt(id));
      if (!found) {
        found = allDestinations.find(d => 
          d.name.toLowerCase() === decodeURIComponent(id).toLowerCase()
        );
      }
      
      if (found) {
        setDestination(found);
        
        // Get similar destinations
        const similar = allDestinations
          .filter(d => d.id !== found.id && (d.type === found.type || d.region === found.region))
          .slice(0, 4);
        setSimilarDestinations(similar);
      }
    } catch (error) {
      console.error('Error fetching destination:', error);
      toast.error('Failed to load destination');
    } finally {
      setLoading(false);
    }
  }, [id]);

  const fetchBudgetEstimate = useCallback(async () => {
    try {
      const response = await budgetService.estimate(destination.name, selectedDays);
      setBudgetEstimate(response.data.budget_breakdown);
    } catch (error) {
      console.error('Error fetching budget:', error);
    }
  }, [destination, selectedDays]);

  useEffect(() => {
    fetchDestination();
  }, [fetchDestination]);

  useEffect(() => {
    if (destination) {
      fetchBudgetEstimate();
    }
  }, [destination, selectedDays, fetchBudgetEstimate]);

  const handleSaveTrip = async () => {
    if (!isAuthenticated) {
      toast.info('Please login to save trips');
      return;
    }

    setSaving(true);
    const result = await saveTrip({
      destination: destination.name,
      days: selectedDays,
      budget_estimate: budgetEstimate,
      saved_at: new Date().toISOString()
    });
    setSaving(false);

    if (result.success) {
      toast.success('Trip saved to your profile!');
    } else {
      toast.error(result.error);
    }
  };

  const handleShare = () => {
    if (navigator.share) {
      navigator.share({
        title: `${destination.name} - Travel Planner`,
        text: `Check out ${destination.name} on Travel Planner Pakistan!`,
        url: window.location.href
      });
    } else {
      navigator.clipboard.writeText(window.location.href);
      toast.success('Link copied to clipboard!');
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-PK', {
      style: 'currency',
      currency: 'PKR',
      maximumFractionDigits: 0
    }).format(amount);
  };

  if (loading) {
    return (
      <div className="destination-page loading">
        <div className="loading-spinner"></div>
        <p>Loading destination...</p>
      </div>
    );
  }

  if (!destination) {
    return (
      <div className="destination-page not-found">
        <h2>Destination not found</h2>
        <p>The destination you're looking for doesn't exist.</p>
        <Link to="/" className="back-btn">
          <FaArrowLeft /> Back to Home
        </Link>
      </div>
    );
  }

  // Image mapping for destinations - optimized for fast loading
  const placeholderImages = {
    'Hunza Valley': 'https://picsum.photos/seed/hunza/1200/600',
    'Gwadar Beach': 'https://picsum.photos/seed/beach/1200/600',
    'Murree': 'https://picsum.photos/seed/hills/1200/600',
    'Skardu': 'https://picsum.photos/seed/mountains/1200/600',
    'Swat Valley': 'https://picsum.photos/seed/valley/1200/600',
    'Naran Kaghan': 'https://picsum.photos/seed/lake/1200/600',
    'Lahore': 'https://picsum.photos/seed/city/1200/600',
    'Islamabad': 'https://picsum.photos/seed/capital/1200/600',
    'Karachi': 'https://picsum.photos/seed/karachi/1200/600',
    'Fairy Meadows': 'https://picsum.photos/seed/meadows/1200/600',
  };

  const imageUrl = destination.image?.startsWith('http') 
    ? destination.image 
    : (placeholderImages[destination.name] || `https://picsum.photos/seed/${encodeURIComponent(destination.name)}/1200/600`);

  return (
    <div className="destination-page">
      {/* Hero Section */}
      <section className="destination-hero">
        <img 
          src={imageUrl} 
          alt={destination.name} 
          className="hero-image"
          onError={(e) => {
            e.target.src = `https://picsum.photos/seed/${encodeURIComponent(destination.name)}/1200/600`;
          }}
        />
        <div className="hero-overlay"></div>
        <div className="hero-content">
          <Link to="/search" className="back-link">
            <FaArrowLeft /> Back to Search
          </Link>
          <div className="hero-info">
            <span className="type-badge">{destination.type}</span>
            <h1>{destination.name}</h1>
            <div className="hero-meta">
              <span><FaMapMarkerAlt /> {destination.region}</span>
              <span><FaStar /> {destination.user_rating?.toFixed(1)} Rating</span>
              <span><FaShieldAlt /> Safety: {destination.safety_rating}/5</span>
            </div>
          </div>
          <div className="hero-actions">
            <button 
              className="action-btn save" 
              onClick={handleSaveTrip}
              disabled={saving}
            >
              <FaHeart /> {saving ? 'Saving...' : 'Save Trip'}
            </button>
            <button className="action-btn share" onClick={handleShare}>
              <FaShare /> Share
            </button>
          </div>
        </div>
      </section>

      {/* Main Content */}
      <div className="destination-content">
        <div className="content-grid">
          {/* Left Column - Details */}
          <div className="details-column">
            {/* Overview */}
            <section className="content-section">
              <h2>Overview</h2>
              <p className="description">
                {destination.description || 
                  `Experience the beauty of ${destination.name} in ${destination.region}. 
                  This ${destination.type.toLowerCase()} destination offers a unique blend of 
                  natural beauty, cultural richness, and memorable experiences.`}
              </p>
            </section>

            {/* Quick Facts */}
            <section className="content-section facts-section">
              <h2>Quick Facts</h2>
              <div className="facts-grid">
                <div className="fact-card">
                  <FaCloud className="fact-icon" />
                  <span className="fact-label">Weather</span>
                  <span className="fact-value">{destination.weather}</span>
                </div>
                <div className="fact-card">
                  <FaCalendarAlt className="fact-icon" />
                  <span className="fact-label">Best Season</span>
                  <span className="fact-value">{destination.best_season}</span>
                </div>
                <div className="fact-card">
                  <FaShieldAlt className="fact-icon" />
                  <span className="fact-label">Safety</span>
                  <span className="fact-value">{destination.safety_rating}/5</span>
                </div>
                <div className="fact-card">
                  <FaStar className="fact-icon" />
                  <span className="fact-label">Rating</span>
                  <span className="fact-value">{destination.user_rating?.toFixed(1)}</span>
                </div>
              </div>
            </section>

            {/* Activities */}
            <section className="content-section">
              <h2><FaHiking /> Activities</h2>
              <div className="activities-list">
                {destination.activities?.map((activity, index) => (
                  <span key={index} className="activity-badge">{activity}</span>
                ))}
              </div>
            </section>
          </div>

          {/* Right Column - Budget */}
          <div className="budget-column">
            <div className="budget-card">
              <h2>Plan Your Trip</h2>
              
              <div className="days-selector">
                <label>Trip Duration</label>
                <div className="days-options">
                  {[2, 3, 5, 7].map(days => (
                    <button
                      key={days}
                      className={`days-btn ${selectedDays === days ? 'active' : ''}`}
                      onClick={() => setSelectedDays(days)}
                    >
                      {days} Days
                    </button>
                  ))}
                </div>
              </div>

              {budgetEstimate && (
                <BudgetTable 
                  budgetData={budgetEstimate} 
                  destination={destination.name}
                  days={selectedDays}
                />
              )}

              <div className="starting-price">
                <span>Destination Starting Cost</span>
                <span className="price">{formatCurrency(destination.cost)}</span>
              </div>

              <button 
                className="book-btn"
                onClick={handleSaveTrip}
                disabled={saving}
              >
                {saving ? 'Saving...' : 'Save This Trip'}
              </button>
              
              {!isAuthenticated && (
                <p className="login-notice">
                  <Link to="/login">Login</Link> to save trips
                </p>
              )}
            </div>
          </div>
        </div>

        {/* Similar Destinations */}
        {similarDestinations.length > 0 && (
          <section className="similar-section">
            <h2>Similar Destinations</h2>
            <div className="similar-grid">
              {similarDestinations.map((dest, index) => (
                <DestinationCard key={index} destination={dest} compact />
              ))}
            </div>
          </section>
        )}
      </div>
    </div>
  );
};

export default Destination;
