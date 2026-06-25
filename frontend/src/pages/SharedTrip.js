import React, { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { FaMapMarkedAlt, FaRegCalendarAlt, FaMoneyBillWave, FaClipboardList, FaUser } from 'react-icons/fa';
import { toast } from 'react-toastify';
import { destinationService } from '../services/api';
import '../styles/SharedTrip.css';

const SharedTrip = () => {
  const { token } = useParams();
  const [trip, setTrip] = useState(null);
  const [owner, setOwner] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadSharedTrip = async () => {
      try {
        const response = await destinationService.getSharedTrip(token);
        setTrip(response.data.trip);
        setOwner(response.data.owner);
      } catch (err) {
        setError(err.response?.data?.error || 'Unable to load shared trip');
      } finally {
        setLoading(false);
      }
    };

    loadSharedTrip();
  }, [token]);

  const copyLink = async () => {
    try {
      await navigator.clipboard.writeText(window.location.href);
      toast.success('Link copied!');
    } catch (error) {
      window.prompt('Copy this link', window.location.href);
    }
  };

  if (loading) {
    return <div className="shared-trip-page"><div className="shared-trip-shell">Loading shared trip…</div></div>;
  }

  if (error) {
    return (
      <div className="shared-trip-page">
        <div className="shared-trip-shell error-state">
          <h1>Shared trip not found</h1>
          <p>{error}</p>
          <Link to="/" className="shared-trip-button">Go home</Link>
        </div>
      </div>
    );
  }

  const budgetTotal = trip?.budget_estimate?.total || 0;

  return (
    <div className="shared-trip-page">
      <div className="shared-trip-shell">
        <div className="shared-trip-hero">
          <span className="shared-trip-badge">Shared travel plan</span>
          <h1>{trip?.destination}</h1>
          <p>
            <FaUser /> Shared by {owner?.name || 'a traveler'}
          </p>
        </div>

        <div className="shared-trip-grid">
          <div className="shared-trip-card">
            <div className="shared-trip-card-title">
              <FaMapMarkedAlt /> Trip summary
            </div>
            <div className="shared-trip-stat">{trip?.days} days</div>
            <p>{trip?.notes || 'No notes were added to this trip.'}</p>
          </div>

          <div className="shared-trip-card">
            <div className="shared-trip-card-title">
              <FaRegCalendarAlt /> Saved on
            </div>
            <div className="shared-trip-stat">
              {trip?.saved_at ? new Date(trip.saved_at).toLocaleDateString() : 'Unknown'}
            </div>
            <p>Share link generated from a saved itinerary.</p>
          </div>

          <div className="shared-trip-card">
            <div className="shared-trip-card-title">
              <FaMoneyBillWave /> Estimated budget
            </div>
            <div className="shared-trip-stat">PKR {budgetTotal.toLocaleString()}</div>
            <p>Budget details are based on the saved trip snapshot.</p>
          </div>
        </div>

        {Array.isArray(trip?.daily_plan) && trip.daily_plan.length > 0 && (
          <div className="shared-trip-plan">
            <h2><FaClipboardList /> Daily plan</h2>
            <div className="shared-plan-list">
              {trip.daily_plan.map((day, index) => (
                <div key={`${day.day || index}-${index}`} className="shared-plan-item">
                  <div className="shared-plan-day">Day {day.day || index + 1}</div>
                  <h3>{day.title || day.name || 'Planned activity'}</h3>
                  <p>{day.description || day.summary || 'No extra details provided.'}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="shared-trip-footer">
          <button className="shared-trip-button secondary" type="button" onClick={copyLink}>
            Copy share link
          </button>
          <Link to="/planner" className="shared-trip-button">
            Build your own trip
          </Link>
        </div>
      </div>
    </div>
  );
};

export default SharedTrip;
