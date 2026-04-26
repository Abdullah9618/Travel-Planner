import React, { useState } from 'react';
import { FaUser, FaSave, FaHeart, FaCog, FaHistory, FaEdit } from 'react-icons/fa';
import { toast } from 'react-toastify';
import { useAuth } from '../context/AuthContext';
import '../styles/Profile.css';

const Profile = () => {
  const { user, updateProfile } = useAuth();
  const [activeTab, setActiveTab] = useState('preferences');
  const [editing, setEditing] = useState(false);
  const [loading, setLoading] = useState(false);

  const [formData, setFormData] = useState({
    name: user?.name || '',
    preferences: {
      budget_range: user?.preferences?.budget_range || { min: 10000, max: 50000 },
      travel_style: user?.preferences?.travel_style || [],
      duration: user?.preferences?.duration || 3,
      weather_preference: user?.preferences?.weather_preference || '',
      preferred_activities: user?.preferences?.preferred_activities || []
    }
  });

  const travelStyles = ['Adventure', 'Relaxation', 'Family', 'Cultural', 'Historical', 'Religious'];
  const weatherOptions = ['Cold', 'Cool', 'Moderate', 'Warm', 'Hot'];
  const activityOptions = [
    'Hiking', 'Trekking', 'Camping', 'Photography', 'Sightseeing',
    'Swimming', 'Boating', 'Skiing', 'Shopping', 'Food Tours'
  ];

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handlePreferenceChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      preferences: {
        ...prev.preferences,
        [field]: value
      }
    }));
  };

  const handleStyleToggle = (style) => {
    const current = formData.preferences.travel_style;
    const updated = current.includes(style)
      ? current.filter(s => s !== style)
      : [...current, style];
    handlePreferenceChange('travel_style', updated);
  };

  const handleActivityToggle = (activity) => {
    const current = formData.preferences.preferred_activities;
    const updated = current.includes(activity)
      ? current.filter(a => a !== activity)
      : [...current, activity];
    handlePreferenceChange('preferred_activities', updated);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    const result = await updateProfile(formData);
    setLoading(false);

    if (result.success) {
      toast.success('Profile updated successfully!');
      setEditing(false);
    } else {
      toast.error(result.error);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-PK', {
      style: 'currency',
      currency: 'PKR',
      maximumFractionDigits: 0
    }).format(amount);
  };

  return (
    <div className="profile-page">
      <div className="profile-container">
        {/* Profile Header */}
        <div className="profile-header">
          <div className="profile-avatar">
            <FaUser />
          </div>
          <div className="profile-info">
            <h1>{user?.name}</h1>
            <p>{user?.email}</p>
            <span className="member-badge">
              {user?.role === 'admin' ? '👑 Admin' : '✈️ Traveler'}
            </span>
          </div>
        </div>

        {/* Profile Tabs */}
        <div className="profile-tabs">
          <button 
            className={`tab ${activeTab === 'preferences' ? 'active' : ''}`}
            onClick={() => setActiveTab('preferences')}
          >
            <FaCog /> Preferences
          </button>
          <button 
            className={`tab ${activeTab === 'saved' ? 'active' : ''}`}
            onClick={() => setActiveTab('saved')}
          >
            <FaHeart /> Saved Trips
          </button>
          <button 
            className={`tab ${activeTab === 'history' ? 'active' : ''}`}
            onClick={() => setActiveTab('history')}
          >
            <FaHistory /> Travel History
          </button>
        </div>

        {/* Tab Content */}
        <div className="profile-content">
          {activeTab === 'preferences' && (
            <div className="preferences-section">
              <div className="section-header">
                <h2>Travel Preferences</h2>
                <button 
                  className="edit-btn"
                  onClick={() => setEditing(!editing)}
                >
                  <FaEdit /> {editing ? 'Cancel' : 'Edit'}
                </button>
              </div>

              <form onSubmit={handleSubmit} className="preferences-form">
                {/* Name */}
                <div className="form-group">
                  <label>Display Name</label>
                  <input
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleChange}
                    disabled={!editing}
                  />
                </div>

                {/* Budget Range */}
                <div className="form-group">
                  <label>Budget Range (PKR)</label>
                  <div className="budget-range">
                    <div className="range-input">
                      <span>Min:</span>
                      <input
                        type="number"
                        value={formData.preferences.budget_range.min}
                        onChange={(e) => handlePreferenceChange('budget_range', {
                          ...formData.preferences.budget_range,
                          min: parseInt(e.target.value) || 0
                        })}
                        disabled={!editing}
                        step="5000"
                      />
                    </div>
                    <div className="range-input">
                      <span>Max:</span>
                      <input
                        type="number"
                        value={formData.preferences.budget_range.max}
                        onChange={(e) => handlePreferenceChange('budget_range', {
                          ...formData.preferences.budget_range,
                          max: parseInt(e.target.value) || 0
                        })}
                        disabled={!editing}
                        step="5000"
                      />
                    </div>
                  </div>
                  <p className="range-display">
                    {formatCurrency(formData.preferences.budget_range.min)} - {formatCurrency(formData.preferences.budget_range.max)}
                  </p>
                </div>

                {/* Travel Style */}
                <div className="form-group">
                  <label>Travel Style</label>
                  <div className="toggle-group">
                    {travelStyles.map(style => (
                      <button
                        key={style}
                        type="button"
                        className={`toggle-btn ${formData.preferences.travel_style.includes(style) ? 'active' : ''}`}
                        onClick={() => editing && handleStyleToggle(style)}
                        disabled={!editing}
                      >
                        {style}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Preferred Duration */}
                <div className="form-group">
                  <label>Preferred Trip Duration (Days)</label>
                  <select
                    value={formData.preferences.duration}
                    onChange={(e) => handlePreferenceChange('duration', parseInt(e.target.value))}
                    disabled={!editing}
                  >
                    {[1, 2, 3, 4, 5, 6, 7, 10, 14].map(days => (
                      <option key={days} value={days}>{days} {days === 1 ? 'Day' : 'Days'}</option>
                    ))}
                  </select>
                </div>

                {/* Weather Preference */}
                <div className="form-group">
                  <label>Weather Preference</label>
                  <div className="toggle-group">
                    {weatherOptions.map(weather => (
                      <button
                        key={weather}
                        type="button"
                        className={`toggle-btn ${formData.preferences.weather_preference === weather ? 'active' : ''}`}
                        onClick={() => editing && handlePreferenceChange('weather_preference', weather)}
                        disabled={!editing}
                      >
                        {weather}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Preferred Activities */}
                <div className="form-group">
                  <label>Preferred Activities</label>
                  <div className="toggle-group activities">
                    {activityOptions.map(activity => (
                      <button
                        key={activity}
                        type="button"
                        className={`toggle-btn ${formData.preferences.preferred_activities.includes(activity) ? 'active' : ''}`}
                        onClick={() => editing && handleActivityToggle(activity)}
                        disabled={!editing}
                      >
                        {activity}
                      </button>
                    ))}
                  </div>
                </div>

                {editing && (
                  <button type="submit" className="save-btn" disabled={loading}>
                    {loading ? 'Saving...' : <><FaSave /> Save Preferences</>}
                  </button>
                )}
              </form>
            </div>
          )}

          {activeTab === 'saved' && (
            <div className="saved-section">
              <h2>Saved Trips</h2>
              {user?.saved_trips?.length > 0 ? (
                <div className="saved-trips-grid">
                  {user.saved_trips.map((trip, index) => (
                    <div key={index} className="saved-trip-card">
                      <h3>{trip.destination}</h3>
                      <p>{trip.days} days trip</p>
                      <p className="trip-cost">
                        {formatCurrency(trip.budget_estimate?.total || 0)}
                      </p>
                      <span className="saved-date">
                        Saved: {new Date(trip.saved_at).toLocaleDateString()}
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="empty-state">
                  <FaHeart className="empty-icon" />
                  <h3>No saved trips yet</h3>
                  <p>Start exploring and save your favorite destinations!</p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'history' && (
            <div className="history-section">
              <h2>Travel History</h2>
              {user?.history?.length > 0 ? (
                <div className="saved-trips-grid">
                  {user.history.map((item, index) => (
                    <div key={index} className="saved-trip-card">
                      <h3>{item.destination}</h3>
                      <p>{item.days} days trip</p>
                      <p className="trip-cost">
                        {formatCurrency(item.budget_estimate?.total || 0)}
                      </p>
                      <span className="saved-date">
                        {item.action || 'saved'} on {new Date(item.saved_at).toLocaleDateString()}
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="empty-state">
                  <FaHistory className="empty-icon" />
                  <h3>No travel history</h3>
                  <p>Your completed trips will appear here</p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Profile;
