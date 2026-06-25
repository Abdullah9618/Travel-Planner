import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { FaMapMarkerAlt, FaCompass, FaStar, FaUsers } from 'react-icons/fa';
import SearchBar from '../components/SearchBar';
import DestinationCard from '../components/DestinationCard';
import { destinationService } from '../services/api';
import { useAuth } from '../context/AuthContext';
import '../styles/Home.css';

const Home = () => {
  const [recommendations, setRecommendations] = useState([]);
  const [travelSuggestions, setTravelSuggestions] = useState([]);
  const [homeInsights, setHomeInsights] = useState(null);
  const [loading, setLoading] = useState(true);
  const { user, isAuthenticated } = useAuth();

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Fetch recommendations based on user status
        let recsResponse;
        if (isAuthenticated && user?.preferences) {
          recsResponse = await destinationService.getRecommendations(
            user.preferences,
            user.history || []
          );
        } else {
          recsResponse = await destinationService.getRecommendations();
        }
        setRecommendations(recsResponse.data);

        // Fetch travel suggestions
        const suggestionsResponse = await destinationService.getTravelSuggestions();
        setTravelSuggestions(suggestionsResponse.data);

        const insightsResponse = await destinationService.getHomeInsights();
        setHomeInsights(insightsResponse.data);
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [isAuthenticated, user]);

  const stats = [
    { icon: FaMapMarkerAlt, value: '50+', label: 'Destinations' },
    { icon: FaCompass, value: '1000+', label: 'Trips Planned' },
    { icon: FaStar, value: '4.8', label: 'Average Rating' },
    { icon: FaUsers, value: '5000+', label: 'Happy Travelers' }
  ];

  return (
    <div className="home">
      {/* Hero Section */}
      <section className="hero">
        <div className="hero-overlay"></div>
        <div className="hero-content">
          <h1>{isAuthenticated ? `Welcome back, ${user?.name || 'Traveler'}!` : 'Discover the Beauty of Pakistan'}</h1>
          <p>Plan your perfect trip with AI-powered recommendations</p>
          <SearchBar />
          <div className="cta-buttons" style={{ marginTop: '1.2rem' }}>
            <Link to="/planner" className="btn btn-primary">Plan My Trip</Link>
          </div>
          
          {!isAuthenticated && (
            <p className="guest-notice">
               Browse as guest or <Link to="/register">create an account</Link> to save your trips
            </p>
          )}
        </div>
      </section>

      {/* Stats Section */}
      <section className="stats-section">
        <div className="stats-container">
          {stats.map((stat, index) => (
            <div key={index} className="stat-item">
              <stat.icon className="stat-icon" />
              <span className="stat-value">{stat.value}</span>
              <span className="stat-label">{stat.label}</span>
            </div>
          ))}
        </div>
      </section>

      {homeInsights && (
        <section className="section suggestion-section">
          <div className="section-header">
            <h2>Live Weather & Travel Advisories</h2>
          </div>
          <div className="destinations-row">
            {homeInsights.weather_highlights?.map((item, idx) => (
              <div key={idx} className="saved-trip-card">
                <h3>{item.destination}</h3>
                <p>{item.region}</p>
                <p><strong>{item.temperature}°C</strong> • {item.condition}</p>
                <span className="saved-date">{item.description}</span>
              </div>
            ))}
          </div>
          <div style={{ marginTop: '1rem' }}>
            {homeInsights.travel_advisories?.map((advisory, idx) => (
              <p key={idx} style={{ marginBottom: '0.4rem' }}>• <strong>{advisory.title}:</strong> {advisory.message}</p>
            ))}
          </div>
        </section>
      )}

      {homeInsights?.ai_suggestions?.length > 0 && (
        <section className="section suggestion-section">
          <div className="section-header">
            <h2>AI Suggestions</h2>
          </div>
          <div className="destinations-row" style={{ gap: '0.75rem', flexWrap: 'wrap' }}>
            {homeInsights.ai_suggestions.map((item, idx) => (
              <div key={idx} className="saved-trip-card" style={{ minWidth: '240px' }}>
                <h3>{item}</h3>
              </div>
            ))}
          </div>
        </section>
      )}

      {homeInsights?.trending_destinations?.length > 0 && (
        <section className="section recommendations-section">
          <div className="section-header">
            <h2>Trending Destinations</h2>
            <p>Popular picks based on saves and views across the app</p>
          </div>
          <div className="destinations-grid">
            {homeInsights.trending_destinations.map((dest, index) => (
              <DestinationCard key={`${dest.name}-${index}`} destination={dest} />
            ))}
          </div>
        </section>
      )}

      {/* Recommendations Section */}
      <section className="section recommendations-section">
        <div className="section-header">
          <h2>
            {isAuthenticated ? `Recommended for ${user?.name}` : 'Popular Destinations'}
          </h2>
          <p>
            {isAuthenticated 
              ? 'Based on your preferences and travel history'
              : 'Discover the most loved destinations in Pakistan'}
          </p>
        </div>
        
        {loading ? (
          <div className="loading-grid">
            {[1, 2, 3, 4, 5, 6].map(i => (
              <div key={i} className="skeleton-card"></div>
            ))}
          </div>
        ) : (
          <div className="destinations-grid">
            {recommendations.map((dest, index) => (
              <DestinationCard key={index} destination={dest} />
            ))}
          </div>
        )}
      </section>

      {/* Travel Suggestions Section */}
      {travelSuggestions.map((suggestion, index) => (
        <section key={index} className="section suggestion-section">
          <div className="section-header">
            <h2>{suggestion.title}</h2>
          </div>
          <div className="destinations-row">
            {suggestion.destinations.map((dest, idx) => (
              <DestinationCard key={idx} destination={dest} compact />
            ))}
          </div>
        </section>
      ))}

      {/* CTA Section */}
      <section className="cta-section">
        <div className="cta-content">
          <h2>Ready to Start Your Adventure?</h2>
          <p>Join thousands of travelers who have discovered their perfect destinations</p>
          {!isAuthenticated ? (
            <div className="cta-buttons">
              <Link to="/register" className="btn btn-primary">Get Started Free</Link>
              <Link to="/search?type=Adventure" className="btn btn-secondary">Explore Destinations</Link>
            </div>
          ) : (
            <Link to="/profile" className="btn btn-primary">View Your Trips</Link>
          )}
        </div>
      </section>
    </div>
  );
};

export default Home;
