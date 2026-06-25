import React, { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { FaMapMarkedAlt, FaCloudSun, FaWallet, FaRoute, FaUtensils, FaSave, FaStar } from 'react-icons/fa';
import { MapContainer, Marker, Popup, TileLayer, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { destinationService } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { toast } from 'react-toastify';
import '../styles/ItineraryPlanner.css';

// Fix default marker icons in many React build setups
import L from 'leaflet';

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

// Create a custom marker icon with better visibility
const customIcon = new L.Icon({
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

const defaultCenter = [30.3753, 69.3451];

// Updates map center and zoom dynamically
function MapUpdater({ center, zoom }) {
  const map = useMap();
  map.setView(center, zoom);
  return null;
}

const ItineraryPlanner = () => {
  const { isAuthenticated, user, saveTrip } = useAuth();
  const [formData, setFormData] = useState({
    query: '',
    destination: '',
    days: '',
    budget: '',
  });

  const [itinerary, setItinerary] = useState(null);
  const [editablePlan, setEditablePlan] = useState([]);
  const [expandedDays, setExpandedDays] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [savingPlan, setSavingPlan] = useState(false);
  const [feedbackForm, setFeedbackForm] = useState({ rating: 5, comment: '' });
  const [submittingFeedback, setSubmittingFeedback] = useState(false);

  const mapCenter = useMemo(() => {
    const lat = itinerary?.map?.center?.lat;
    const lng = itinerary?.map?.center?.lng;
    if (typeof lat === 'number' && typeof lng === 'number') return [lat, lng];
    return defaultCenter;
  }, [itinerary]);

  useEffect(() => {
    const nextPlan = (itinerary?.daily_plan || []).map((day) => ({ ...day }));
    setEditablePlan(nextPlan);
    setExpandedDays(nextPlan.map((_, index) => index === 0));
    setFeedbackForm((prev) => ({ ...prev, comment: '' }));
  }, [itinerary]);

  const tileUrl = itinerary?.map?.tile_url || `https://api.maptiler.com/maps/streets/{z}/{x}/{y}.png?key=${process.env.REACT_APP_MAPTILER_API_KEY || ''}`;

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: (name === 'days' || name === 'budget') ? (value === '' ? '' : Number(value)) : value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await destinationService.generateItinerary({
        ...formData,
        preferences: user?.preferences || {},
      });
      setItinerary(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to generate itinerary.');
    } finally {
      setLoading(false);
    }
  };

  const updatePlanField = (dayIndex, field, value) => {
    setEditablePlan((prev) => prev.map((day, idx) => (
      idx === dayIndex ? { ...day, [field]: value } : day
    )));
  };

  const toggleDay = (dayIndex) => {
    setExpandedDays((prev) => prev.map((isOpen, idx) => (
      idx === dayIndex ? !isOpen : isOpen
    )));
  };

  const expandAllDays = () => {
    setExpandedDays(editablePlan.map(() => true));
  };

  const collapseAllDays = () => {
    setExpandedDays(editablePlan.map(() => false));
  };

  const copyPreviousDay = (dayIndex) => {
    if (dayIndex <= 0) return;
    setEditablePlan((prev) => prev.map((day, idx) => (
      idx === dayIndex ? { ...prev[dayIndex - 1], day: day.day || idx + 1, title: `${prev[dayIndex - 1]?.title || 'Day'} (Copied)` } : day
    )));
    setExpandedDays((prev) => prev.map((isOpen, idx) => (idx === dayIndex ? true : isOpen)));
    toast.info(`Copied day ${dayIndex} into day ${dayIndex + 1}`);
  };

  const resetDay = (dayIndex) => {
    const originalDay = itinerary?.daily_plan?.[dayIndex];
    if (!originalDay) return;
    setEditablePlan((prev) => prev.map((day, idx) => (
      idx === dayIndex ? { ...originalDay } : day
    )));
    toast.info(`Reset day ${dayIndex + 1}`);
  };

  const handleSavePlan = async () => {
    if (!isAuthenticated) {
      toast.info('Please login to save plans');
      return;
    }

    if (!itinerary) return;

    setSavingPlan(true);
    const result = await saveTrip({
      destination: itinerary.destination?.name,
      days: itinerary.days,
      budget_estimate: itinerary.budget_breakdown,
      saved_at: new Date().toISOString(),
      query: formData.query,
      parsed_query: itinerary.parsed_query,
      daily_plan: editablePlan,
      notes: 'Saved from itinerary planner',
    });
    setSavingPlan(false);

    if (result.success) {
      toast.success('Itinerary saved to your profile!');
    } else {
      toast.error(result.error);
    }
  };

  const handleSubmitFeedback = async (e) => {
    e.preventDefault();
    if (!itinerary?.destination?.name) return;

    setSubmittingFeedback(true);
    try {
      const response = await destinationService.submitFeedback({
        destination: itinerary.destination.name,
        rating: feedbackForm.rating,
        comment: feedbackForm.comment,
        user: user?.name || user?.email || 'Anonymous',
        email: user?.email || '',
        source: 'itinerary_planner',
        days: itinerary.days,
      });
      toast.success(response.data?.message || 'Feedback submitted!');
      setFeedbackForm({ rating: 5, comment: '' });
    } catch (err) {
      toast.error(err.response?.data?.error || 'Failed to submit feedback');
    } finally {
      setSubmittingFeedback(false);
    }
  };

  return (
    <div className="planner-page">
      <div className="planner-header">
        <h1><FaRoute /> AI Itinerary Planner</h1>
        <p>Create a complete day-by-day trip plan with live weather, places, map, and budget estimation.</p>
      </div>

      <form className="planner-form" onSubmit={handleSubmit}>
        <div className="planner-grid">
          <div className="form-group" style={{ gridColumn: '1 / -1' }}>
            <label>AI Command (Natural Language)</label>
            <input
              name="query"
              value={formData.query}
              onChange={handleChange}
              placeholder="e.g. 'Plan a 3-day trip to northern Pakistan under 25,000 PKR'"
            />
            <small style={{ color: 'var(--text-secondary)', display: 'block', marginTop: '0.25rem' }}>
              Our AI will automatically fill out the fields below based on your command, or you can enter them manually!
            </small>
          </div>
          <div className="form-group">
            <label>Destination (Optional)</label>
            <input
              name="destination"
              value={formData.destination}
              onChange={handleChange}
              placeholder="e.g. Hunza Valley"
            />
          </div>
          <div className="form-group">
            <label>Duration (Days) — Optional</label>
            <input type="number" min="1" max="14" name="days" value={formData.days} onChange={handleChange} placeholder="e.g. 5" />
          </div>
          <div className="form-group">
            <label>Max Budget (PKR) — Optional</label>
            <input type="number" min="5000" step="1000" name="budget" value={formData.budget} onChange={handleChange} placeholder="e.g. 30000" />
          </div>
        </div>

        <button className="planner-btn" type="submit" disabled={loading}>
          {loading ? 'Generating Plan...' : 'Generate Plan'}
        </button>
      </form>

      {error && <p className="planner-error">{error}</p>}

      {itinerary && (
        <div className="planner-results">
          <div className="planner-summary">
            <h2>{itinerary.destination?.name}</h2>
            <p>{itinerary.destination?.region} • {itinerary.days} Days</p>
            <p className={`budget-status ${itinerary.budget_status}`}>Budget status: {itinerary.budget_status}</p>
            {itinerary.match_reason && <p>Why recommended: {itinerary.match_reason}</p>}
            <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap', marginTop: '1rem' }}>
              <button className="planner-btn" type="button" onClick={handleSavePlan} disabled={savingPlan} style={{ minWidth: '180px' }}>
                <FaSave /> {savingPlan ? 'Saving...' : 'Save Itinerary'}
              </button>
            </div>
            {!isAuthenticated && (
              <p className="planner-login-tip">You are browsing as guest. <Link to="/login">Login</Link> to save plans.</p>
            )}
          </div>

          <div className="planner-panels">
            <div className="panel">
              <h3><FaCloudSun /> Live Weather</h3>
              <p><strong>{itinerary.weather?.temperature}°C</strong> • {itinerary.weather?.condition}</p>
              <p>{itinerary.weather?.description}</p>
              {(itinerary.advisories || []).length > 0 && (
                <ul style={{ marginTop: '0.75rem', paddingLeft: '1.2rem' }}>
                  {itinerary.advisories.map((advisory, idx) => (
                    <li key={idx}><strong>{advisory.title}:</strong> {advisory.message}</li>
                  ))}
                </ul>
              )}
            </div>

            <div className="panel budget-panel">
              <h3><FaWallet /> Budget Breakdown</h3>
              <ul className="budget-list">
                <li>
                  <span>Hotel</span>
                  <strong>PKR {Math.round(itinerary.budget_breakdown?.hotel || 0).toLocaleString()}</strong>
                </li>
                <li>
                  <span>Travel</span>
                  <strong>PKR {Math.round(itinerary.budget_breakdown?.travel || 0).toLocaleString()}</strong>
                </li>
                <li>
                  <span>Meals</span>
                  <strong>PKR {Math.round(itinerary.budget_breakdown?.meals || 0).toLocaleString()}</strong>
                </li>
                <li>
                  <span>Activities</span>
                  <strong>PKR {Math.round(itinerary.budget_breakdown?.activities || 0).toLocaleString()}</strong>
                </li>
              </ul>
              <p className="budget-total-row">
                <span>Total</span>
                <strong>PKR {Math.round(itinerary.budget_breakdown?.total || 0).toLocaleString()}</strong>
              </p>
            </div>

            <div className="panel">
              <h3><FaUtensils /> Recommended Places</h3>
              <p><strong>Attractions</strong></p>
              <ul>
                {(itinerary.recommended_places?.attractions || []).map((place, idx) => (
                  <li key={`a-${idx}`}>{place.name}</li>
                ))}
              </ul>
              <p><strong>Restaurants</strong></p>
              <ul>
                {(itinerary.recommended_places?.restaurants || []).map((place, idx) => (
                  <li key={`r-${idx}`}>{place.name}</li>
                ))}
              </ul>
            </div>

            {itinerary.navigation?.summary && (
              <div className="panel">
                <h3><FaMapMarkedAlt /> Route Summary</h3>
                <p><strong>{itinerary.navigation.summary.segments}</strong> planned segments</p>
                <p><strong>{itinerary.navigation.summary.distance_km} km</strong> estimated travel distance</p>
                <p><strong>{itinerary.navigation.summary.travel_time_minutes} mins</strong> estimated travel time</p>
                {itinerary.navigation.search_url && (
                  <a className="map-link" href={itinerary.navigation.search_url} target="_blank" rel="noreferrer">Open in Google Maps</a>
                )}
              </div>
            )}
          </div>

          <div className="itinerary-days panel">
            <h3>Day-by-Day Plan</h3>
            <p style={{ marginBottom: '1rem', color: 'var(--text-secondary)' }}>
              Edit any day below before saving your final trip plan.
            </p>
            <div className="day-actions">
              <button type="button" className="planner-btn secondary" onClick={expandAllDays}>Expand all</button>
              <button type="button" className="planner-btn secondary" onClick={collapseAllDays}>Collapse all</button>
            </div>
            <div className="day-list">
              {editablePlan.map((day, index) => (
                <div key={day.day || index} className={`day-card ${expandedDays[index] ? 'expanded' : 'collapsed'}`}>
                  <button
                    type="button"
                    className="day-card-header"
                    onClick={() => toggleDay(index)}
                    aria-expanded={!!expandedDays[index]}
                  >
                    <div>
                      <strong>Day {day.day || index + 1}</strong>
                      <span>{day.title || 'Untitled plan'}</span>
                    </div>
                    <span className="day-card-toggle">{expandedDays[index] ? '−' : '+'}</span>
                  </button>

                  {expandedDays[index] ? (
                    <div className="day-card-body">
                      <div className="day-card-toolbar">
                        <button type="button" className="planner-btn secondary" onClick={() => copyPreviousDay(index)} disabled={index === 0}>Copy previous</button>
                        <button type="button" className="planner-btn secondary" onClick={() => resetDay(index)}>Reset day</button>
                      </div>
                      <label>
                        <strong>Title</strong>
                        <input
                          type="text"
                          value={day.title || ''}
                          onChange={(e) => updatePlanField(index, 'title', e.target.value)}
                        />
                      </label>
                      <label>
                        <strong>Morning</strong>
                        <textarea
                          value={day.morning || ''}
                          onChange={(e) => updatePlanField(index, 'morning', e.target.value)}
                        />
                      </label>
                      <label>
                        <strong>Afternoon</strong>
                        <textarea
                          value={day.afternoon || ''}
                          onChange={(e) => updatePlanField(index, 'afternoon', e.target.value)}
                        />
                      </label>
                      <label>
                        <strong>Evening</strong>
                        <textarea
                          value={day.evening || ''}
                          onChange={(e) => updatePlanField(index, 'evening', e.target.value)}
                        />
                      </label>
                      <label>
                        <strong>Event</strong>
                        <input
                          type="text"
                          value={day.event || ''}
                          onChange={(e) => updatePlanField(index, 'event', e.target.value)}
                          placeholder="Optional local event or festival"
                        />
                      </label>
                    </div>
                  ) : (
                    <div className="day-card-preview">
                      <p><strong>Morning:</strong> {day.morning || 'No morning activity set'}</p>
                      <p><strong>Afternoon:</strong> {day.afternoon || 'No afternoon activity set'}</p>
                      <p><strong>Evening:</strong> {day.evening || 'No evening activity set'}</p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          <div className="panel" style={{ marginTop: '1.5rem' }}>
            <h3><FaStar /> Share Feedback</h3>
            <form onSubmit={handleSubmitFeedback} className="planner-feedback-form">
              <div className="form-group">
                <label>Rating</label>
                <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                  {[1, 2, 3, 4, 5].map((rating) => (
                    <button
                      key={rating}
                      type="button"
                      className={feedbackForm.rating === rating ? 'planner-btn' : 'planner-btn secondary'}
                      onClick={() => setFeedbackForm((prev) => ({ ...prev, rating }))}
                      style={{ minWidth: '52px', padding: '0.7rem 1rem' }}
                    >
                      {rating}
                    </button>
                  ))}
                </div>
              </div>
              <div className="form-group">
                <label>Comment</label>
                <textarea
                  value={feedbackForm.comment}
                  onChange={(e) => setFeedbackForm((prev) => ({ ...prev, comment: e.target.value }))}
                  placeholder="Tell us what worked well or what we should improve..."
                  rows="4"
                />
              </div>
              <button className="planner-btn" type="submit" disabled={submittingFeedback}>
                {submittingFeedback ? 'Submitting...' : 'Submit Feedback'}
              </button>
            </form>
          </div>

          <div className="panel map-panel">
            <h3><FaMapMarkedAlt /> Destination Map</h3>
            <MapContainer center={mapCenter} zoom={10} maxZoom={18} scrollWheelZoom={true} style={{ height: '320px', width: '100%' }}>
              <MapUpdater center={mapCenter} zoom={itinerary?.map?.center ? 10 : 5} />
              <TileLayer
                attribution='&copy; OpenStreetMap contributors &copy; MapTiler'
                url={tileUrl}
                maxZoom={18}
              />
              <Marker position={mapCenter} icon={customIcon}>
                <Popup>
                  <strong>{itinerary.destination?.name}</strong><br />
                  {itinerary.destination?.region}<br />
                  <small>Lat: {mapCenter[0].toFixed(4)}, Lng: {mapCenter[1].toFixed(4)}</small>
                </Popup>
              </Marker>
            </MapContainer>
            {itinerary.map?.search_url && (
              <a className="map-link" href={itinerary.map.search_url} target="_blank" rel="noreferrer">Open directions in map</a>
            )}
            {itinerary.navigation?.segments?.length > 0 && (
              <div style={{ marginTop: '1rem' }}>
                <h4>Route plan</h4>
                <ul style={{ paddingLeft: '1.2rem' }}>
                  {itinerary.navigation.segments.map((segment) => (
                    <li key={segment.day}>
                      Day {segment.day}: {segment.from} → {segment.to} — {segment.distance_km} km, about {segment.travel_time_minutes} mins
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ItineraryPlanner;
