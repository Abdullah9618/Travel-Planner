import React, { useState } from 'react';
import { FaUser, FaSave, FaHeart, FaCog, FaHistory, FaEdit, FaShareAlt, FaTrash, FaTimes } from 'react-icons/fa';
import { toast } from 'react-toastify';
import { useAuth } from '../context/AuthContext';
import '../styles/Profile.css';

const Profile = () => {
  const { user, updateProfile, updateSavedTrip, deleteSavedTrip, shareSavedTrip } = useAuth();
  const [activeTab, setActiveTab] = useState('preferences');
  const [editing, setEditing] = useState(false);
  const [loading, setLoading] = useState(false);
  const [tripModalOpen, setTripModalOpen] = useState(false);
  const [selectedTrip, setSelectedTrip] = useState(null);
  const [tripLoading, setTripLoading] = useState(false);
  const [shareLoadingId, setShareLoadingId] = useState(null);

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

  const [tripFormData, setTripFormData] = useState({
    destination: '',
    days: 1,
    budget_total: 0,
    notes: ''
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

  const openTripEditor = (trip) => {
    setSelectedTrip(trip);
    setTripFormData({
      destination: trip.destination || '',
      days: trip.days || 1,
      budget_total: trip.budget_estimate?.total || 0,
      notes: trip.notes || ''
    });
    setTripModalOpen(true);
  };

  const closeTripEditor = () => {
    setTripModalOpen(false);
    setSelectedTrip(null);
    setTripLoading(false);
  };

  const handleTripChange = (e) => {
    const { name, value } = e.target;
    setTripFormData(prev => ({
      ...prev,
      [name]: name === 'days' || name === 'budget_total' ? Number(value) : value
    }));
  };

  const handleTripSave = async (e) => {
    e.preventDefault();
    if (!selectedTrip) return;

    setTripLoading(true);
    const result = await updateSavedTrip(selectedTrip.id, {
      destination: tripFormData.destination,
      days: tripFormData.days,
      notes: tripFormData.notes,
      budget_estimate: {
        ...(selectedTrip.budget_estimate || {}),
        total: Number(tripFormData.budget_total) || 0
      }
    });
    setTripLoading(false);

    if (result.success) {
      toast.success('Saved trip updated successfully!');
      closeTripEditor();
    } else {
      toast.error(result.error);
    }
  };

  const handleTripDelete = async (trip) => {
    const confirmed = window.confirm(`Delete your saved trip to ${trip.destination}?`);
    if (!confirmed) return;

    setTripLoading(true);
    const result = await deleteSavedTrip(trip.id);
    setTripLoading(false);

    if (result.success) {
      toast.success('Saved trip deleted successfully!');
    } else {
      toast.error(result.error);
    }
  };

  const handleTripShare = async (trip) => {
    setShareLoadingId(trip.id);
    const result = await shareSavedTrip(trip.id);
    setShareLoadingId(null);

    if (result.success && result.shareUrl) {
      try {
        await navigator.clipboard.writeText(result.shareUrl);
        toast.success('Share link copied to clipboard!');
      } catch (error) {
        window.prompt('Copy your share link', result.shareUrl);
        toast.success('Share link ready to copy');
      }
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
                <div className="header-actions" style={{ display: 'flex', gap: '0.5rem' }}>
                  <button 
                    className="edit-btn"
                    onClick={() => setEditing(!editing)}
                    type="button"
                  >
                    <FaEdit /> {editing ? 'Cancel' : 'Edit'}
                  </button>
                  {editing && (
                    <button 
                      className="edit-btn" 
                      style={{ background: 'var(--primary-color)', color: 'white' }}
                      disabled={loading}
                      onClick={handleSubmit}
                      type="button"
                    >
                      {loading ? 'Saving...' : <><FaSave /> Save</>}
                    </button>
                  )}
                </div>
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
                  <button type="submit" className="save-btn" disabled={loading} style={{ marginTop: '2rem', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
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
                      <div className="trip-actions">
                        <button className="trip-action-btn" onClick={() => openTripEditor(trip)} type="button">
                          <FaEdit /> Edit
                        </button>
                        <button
                          className="trip-action-btn share"
                          onClick={() => handleTripShare(trip)}
                          type="button"
                          disabled={shareLoadingId === trip.id}
                        >
                          <FaShareAlt /> {shareLoadingId === trip.id ? 'Sharing...' : 'Share'}
                        </button>
                        <button
                          className="trip-action-btn delete"
                          onClick={() => handleTripDelete(trip)}
                          type="button"
                          disabled={tripLoading}
                        >
                          <FaTrash /> Delete
                        </button>
                      </div>
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

      {tripModalOpen && selectedTrip && (
        <div className="modal-overlay" role="dialog" aria-modal="true">
          <div className="modal-content trip-modal">
            <div className="modal-header">
              <h2>Edit Saved Trip</h2>
              <button className="close-btn" onClick={closeTripEditor} type="button" aria-label="Close trip editor">
                <FaTimes />
              </button>
            </div>

            <form className="destination-form" onSubmit={handleTripSave}>
              <div className="form-group">
                <label>Destination</label>
                <input
                  type="text"
                  name="destination"
                  value={tripFormData.destination}
                  onChange={handleTripChange}
                />
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>Days</label>
                  <input
                    type="number"
                    name="days"
                    min="1"
                    value={tripFormData.days}
                    onChange={handleTripChange}
                  />
                </div>
                <div className="form-group">
                  <label>Budget Total (PKR)</label>
                  <input
                    type="number"
                    name="budget_total"
                    min="0"
                    value={tripFormData.budget_total}
                    onChange={handleTripChange}
                  />
                </div>
              </div>
              <div className="form-group">
                <label>Notes</label>
                <textarea
                  name="notes"
                  rows="4"
                  value={tripFormData.notes}
                  onChange={handleTripChange}
                  placeholder="Add anything you want to remember about this trip"
                />
              </div>
              <div className="form-actions">
                <button type="button" className="admin-cancel-btn" onClick={closeTripEditor}>
                  Cancel
                </button>
                <button type="submit" className="add-btn" disabled={tripLoading}>
                  {tripLoading ? 'Saving...' : <><FaSave /> Save Trip</>}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Profile;
