import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { FaStar, FaMapMarkerAlt, FaCalendarAlt, FaShieldAlt, FaHeart, FaRegHeart } from 'react-icons/fa';
import '../styles/DestinationCard.css';

const DestinationCard = ({ 
  destination, 
  showBudget = false, 
  onSave, 
  isSaved = false,
  compact = false 
}) => {
  const navigate = useNavigate();
  const {
    name,
    type,
    region,
    cost,
    best_season,
    activities,
    safety_rating,
    user_rating,
    image,
    description,
    budget_estimate,
    recommendation_score,
    match_reason
  } = destination;

  // Generate placeholder image URL based on destination id - optimized for fast loading
  const placeholderImages = {
    'Hunza Valley': 'https://picsum.photos/seed/hunza/400/300',
    'Gwadar Beach': 'https://picsum.photos/seed/beach/400/300',
    'Murree': 'https://picsum.photos/seed/hills/400/300',
    'Skardu': 'https://picsum.photos/seed/mountains/400/300',
    'Swat Valley': 'https://picsum.photos/seed/valley/400/300',
    'Naran Kaghan': 'https://picsum.photos/seed/lake/400/300',
    'Lahore': 'https://picsum.photos/seed/city/400/300',
    'Islamabad': 'https://picsum.photos/seed/capital/400/300',
    'Karachi': 'https://picsum.photos/seed/karachi/400/300',
    'Fairy Meadows': 'https://picsum.photos/seed/meadows/400/300',
  };
  
  const imageUrl = image?.startsWith('http') 
    ? image 
    : (placeholderImages[name] || `https://picsum.photos/seed/${encodeURIComponent(name)}/400/300`);

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-PK', {
      style: 'currency',
      currency: 'PKR',
      maximumFractionDigits: 0
    }).format(amount);
  };

  const handleCardClick = (e) => {
    // Only navigate if the click isn't on the save button or its icon
    if (!e.target.closest('.save-btn') && !e.target.closest('.view-btn')) {
      navigate(`/destination/${encodeURIComponent(name)}`);
    }
  };

  return (
    <div 
      className={`destination-card ${compact ? 'compact' : ''}`} 
      onClick={handleCardClick}
      style={{ cursor: 'pointer' }}
    >
      <div className="card-image-container">
        <img 
          src={imageUrl} 
          alt={name} 
          className="card-image"
          onError={(e) => {
            e.target.src = `https://via.placeholder.com/400x300?text=${encodeURIComponent(name)}`;
          }}
        />
        <div className="card-type-badge">{type}</div>
        {onSave && (
          <button 
            className={`save-btn ${isSaved ? 'saved' : ''}`}
            onClick={(e) => {
              e.preventDefault();
              onSave(destination);
            }}
            title={isSaved ? 'Remove from saved' : 'Save trip'}
          >
            {isSaved ? <FaHeart /> : <FaRegHeart />}
          </button>
        )}
        {recommendation_score && (
          <div className="match-score">
            {Math.round(recommendation_score * 100)}% Match
          </div>
        )}
      </div>

      <div className="card-content">
        <div className="card-header">
          <h3 className="card-title">{name}</h3>
          <div className="card-rating">
            <FaStar className="star-icon" />
            <span>{user_rating?.toFixed(1)}</span>
          </div>
        </div>

        <div className="card-location">
          <FaMapMarkerAlt />
          <span>{region}</span>
        </div>

        {!compact && (
          <>
            <p className="card-description">
              {description || `Experience the beauty of ${name} with its unique ${type.toLowerCase()} offerings.`}
            </p>

            <div className="card-meta">
              <div className="meta-item">
                <FaCalendarAlt />
                <span>{best_season}</span>
              </div>
              <div className="meta-item">
                <FaShieldAlt />
                <span>Safety: {safety_rating}/5</span>
              </div>
            </div>

            {activities && activities.length > 0 && (
              <div className="card-activities">
                {activities.slice(0, 3).map((activity, index) => (
                  <span key={index} className="activity-tag">{activity}</span>
                ))}
                {activities.length > 3 && (
                  <span className="activity-tag more">+{activities.length - 3}</span>
                )}
              </div>
            )}

            {match_reason && (
              <p className="match-reason">{match_reason}</p>
            )}
          </>
        )}

        <div className="card-footer">
          <div className="card-price">
            <span className="price-label">Starting from</span>
            <span className="price-value">{formatCurrency(cost)}</span>
          </div>
          <Link to={`/destination/${encodeURIComponent(name)}`} className="view-btn">
            View Details
          </Link>
        </div>

        {showBudget && budget_estimate && (
          <div className="budget-summary">
            <div className="budget-header">
              <span>Estimated Budget ({budget_estimate.days} days)</span>
              <span className="budget-total">{formatCurrency(budget_estimate.total)}</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DestinationCard;
