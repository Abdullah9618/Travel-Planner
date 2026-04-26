import React, { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { FaMapMarkedAlt, FaCloudSun, FaWallet, FaRoute, FaUtensils } from 'react-icons/fa';
import { MapContainer, Marker, Popup, TileLayer } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { destinationService } from '../services/api';
import { useAuth } from '../context/AuthContext';
import '../styles/ItineraryPlanner.css';

// Fix default marker icons in many React build setups
import L from 'leaflet';
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

const defaultCenter = [30.3753, 69.3451];

const ItineraryPlanner = () => {
  const { isAuthenticated, user } = useAuth();
  const [formData, setFormData] = useState({
    query: '',
    destination: '',
    days: 3,
    budget: 25000,
  });
  const [itinerary, setItinerary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const mapCenter = useMemo(() => {
    const lat = itinerary?.map?.center?.lat;
    const lng = itinerary?.map?.center?.lng;
    if (typeof lat === 'number' && typeof lng === 'number') return [lat, lng];
    return defaultCenter;
  }, [itinerary]);

  const tileUrl = itinerary?.map?.tile_url || `https://api.maptiler.com/maps/streets/{z}/{x}/{y}.png?key=${process.env.REACT_APP_MAPTILER_API_KEY || ''}`;

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: name === 'days' || name === 'budget' ? Number(value) : value,
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

  return (
    <div className="planner-page">
      <div className="planner-header">
        <h1><FaRoute /> AI Itinerary Planner</h1>
        <p>Create a complete day-by-day trip plan with live weather, places, map, and budget estimation.</p>
      </div>

      <form className="planner-form" onSubmit={handleSubmit}>
        <div className="planner-grid">
          <div className="form-group">
            <label>Natural Language Query</label>
            <input
              name="query"
              value={formData.query}
              onChange={handleChange}
              placeholder="Plan a 3-day trip to northern Pakistan under 25,000 PKR"
            />
          </div>
          <div className="form-group">
            <label>Destination (optional)</label>
            <input
              name="destination"
              value={formData.destination}
              onChange={handleChange}
              placeholder="Hunza Valley"
            />
          </div>
          <div className="form-group">
            <label>Days</label>
            <input type="number" min="1" max="14" name="days" value={formData.days} onChange={handleChange} />
          </div>
          <div className="form-group">
            <label>Budget (PKR)</label>
            <input type="number" min="5000" step="1000" name="budget" value={formData.budget} onChange={handleChange} />
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
            {!isAuthenticated && (
              <p className="planner-login-tip">You are browsing as guest. <Link to="/login">Login</Link> to save plans.</p>
            )}
          </div>

          <div className="planner-panels">
            <div className="panel">
              <h3><FaCloudSun /> Live Weather</h3>
              <p><strong>{itinerary.weather?.temperature}°C</strong> • {itinerary.weather?.condition}</p>
              <p>{itinerary.weather?.description}</p>
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
          </div>

          <div className="itinerary-days panel">
            <h3>Day-by-Day Plan</h3>
            <div className="day-list">
              {(itinerary.daily_plan || []).map((day) => (
                <div key={day.day} className="day-card">
                  <h4>{day.title}</h4>
                  <p><strong>Morning:</strong> {day.morning}</p>
                  <p><strong>Afternoon:</strong> {day.afternoon}</p>
                  <p><strong>Evening:</strong> {day.evening}</p>
                  {day.event && <p><strong>Event:</strong> {day.event}</p>}
                </div>
              ))}
            </div>
          </div>

          <div className="panel map-panel">
            <h3><FaMapMarkedAlt /> Destination Map</h3>
            <MapContainer center={mapCenter} zoom={6} scrollWheelZoom={true} style={{ height: '320px', width: '100%' }}>
              <TileLayer
                attribution='&copy; OpenStreetMap contributors &copy; MapTiler'
                url={tileUrl}
              />
              <Marker position={mapCenter}>
                <Popup>
                  {itinerary.destination?.name} ({itinerary.destination?.region})
                </Popup>
              </Marker>
            </MapContainer>
            {itinerary.map?.search_url && (
              <a className="map-link" href={itinerary.map.search_url} target="_blank" rel="noreferrer">Open directions in map</a>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ItineraryPlanner;
