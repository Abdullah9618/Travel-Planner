import React, { useState, useEffect } from 'react';
import { Routes, Route, Link, useLocation } from 'react-router-dom';
import { 
  FaChartBar, FaMapMarkerAlt, FaUsers, FaDollarSign, 
  FaPlus, FaEdit, FaTrash, FaTimes, FaSave
} from 'react-icons/fa';
import { toast } from 'react-toastify';
import { adminService } from '../services/api';
import '../styles/AdminDashboard.css';

// Stats Overview Component
const StatsOverview = ({ stats }) => {
  const statCards = [
    { label: 'Total Destinations', value: stats.total_destinations, icon: FaMapMarkerAlt, color: '#3b82f6' },
    { label: 'Total Users', value: stats.total_users, icon: FaUsers, color: '#10b981' },
    { label: 'Average Rating', value: stats.average_user_rating?.toFixed(2), icon: FaChartBar, color: '#f59e0b' },
  ];

  return (
    <div className="stats-overview">
      {statCards.map((stat, index) => (
        <div key={index} className="stat-card" style={{ borderColor: stat.color }}>
          <stat.icon className="stat-icon" style={{ color: stat.color }} />
          <div className="stat-info">
            <span className="stat-value">{stat.value}</span>
            <span className="stat-label">{stat.label}</span>
          </div>
        </div>
      ))}
    </div>
  );
};

// Destination Form Modal
const DestinationForm = ({ destination, onSave, onClose }) => {
  const [formData, setFormData] = useState(destination || {
    name: '',
    type: 'Adventure',
    region: 'Gilgit Baltistan',
    cost: 20000,
    weather: 'Cool',
    best_season: 'Summer',
    activities: [],
    safety_rating: 4,
    user_rating: 4.0,
    image: '',
    description: ''
  });
  const [activityInput, setActivityInput] = useState('');

  const types = ['Adventure', 'Relaxation', 'Family', 'Cultural', 'Historical', 'Religious'];
  const regions = ['Gilgit Baltistan', 'KPK', 'Punjab', 'Sindh', 'Balochistan', 'AJK'];
  const weathers = ['Cold', 'Cool', 'Moderate', 'Warm', 'Hot'];
  const seasons = ['Summer', 'Winter', 'Spring', 'Autumn', 'All Year'];

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ 
      ...prev, 
      [name]: name === 'cost' || name === 'safety_rating' ? parseInt(value) : 
              name === 'user_rating' ? parseFloat(value) : value 
    }));
  };

  const addActivity = () => {
    if (activityInput.trim() && !formData.activities.includes(activityInput.trim())) {
      setFormData(prev => ({
        ...prev,
        activities: [...prev.activities, activityInput.trim()]
      }));
      setActivityInput('');
    }
  };

  const removeActivity = (activity) => {
    setFormData(prev => ({
      ...prev,
      activities: prev.activities.filter(a => a !== activity)
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave(formData);
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <div className="modal-header">
          <h2>{destination ? 'Edit Destination' : 'Add New Destination'}</h2>
          <button className="close-btn" onClick={onClose}><FaTimes /></button>
        </div>
        
        <form onSubmit={handleSubmit} className="destination-form">
          <div className="form-row">
            <div className="form-group">
              <label>Name *</label>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleChange}
                required
              />
            </div>
            <div className="form-group">
              <label>Type *</label>
              <select name="type" value={formData.type} onChange={handleChange}>
                {types.map(t => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Region *</label>
              <select name="region" value={formData.region} onChange={handleChange}>
                {regions.map(r => <option key={r} value={r}>{r}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label>Cost (PKR) *</label>
              <input
                type="number"
                name="cost"
                value={formData.cost}
                onChange={handleChange}
                min="0"
                step="1000"
                required
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Weather</label>
              <select name="weather" value={formData.weather} onChange={handleChange}>
                {weathers.map(w => <option key={w} value={w}>{w}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label>Best Season</label>
              <select name="best_season" value={formData.best_season} onChange={handleChange}>
                {seasons.map(s => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Safety Rating (1-5)</label>
              <input
                type="number"
                name="safety_rating"
                value={formData.safety_rating}
                onChange={handleChange}
                min="1"
                max="5"
              />
            </div>
            <div className="form-group">
              <label>User Rating (1-5)</label>
              <input
                type="number"
                name="user_rating"
                value={formData.user_rating}
                onChange={handleChange}
                min="1"
                max="5"
                step="0.1"
              />
            </div>
          </div>

          <div className="form-group">
            <label>Activities</label>
            <div className="activity-input-group">
              <input
                type="text"
                value={activityInput}
                onChange={(e) => setActivityInput(e.target.value)}
                placeholder="Add activity"
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addActivity())}
              />
              <button type="button" onClick={addActivity}>Add</button>
            </div>
            <div className="activities-list">
              {formData.activities.map((activity, index) => (
                <span key={index} className="activity-tag">
                  {activity}
                  <button type="button" onClick={() => removeActivity(activity)}>×</button>
                </span>
              ))}
            </div>
          </div>

          <div className="form-group">
            <label>Image URL</label>
            <input
              type="text"
              name="image"
              value={formData.image}
              onChange={handleChange}
              placeholder="https://example.com/image.jpg"
            />
          </div>

          <div className="form-group">
            <label>Description</label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleChange}
              rows="3"
              placeholder="Brief description of the destination"
            />
          </div>

          <div className="form-actions">
            <button type="button" className="cancel-btn" onClick={onClose}>Cancel</button>
            <button type="submit" className="save-btn"><FaSave /> Save</button>
          </div>
        </form>
      </div>
    </div>
  );
};

// Destinations Management
const DestinationsManagement = () => {
  const [destinations, setDestinations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingDestination, setEditingDestination] = useState(null);

  useEffect(() => {
    fetchDestinations();
  }, []);

  const fetchDestinations = async () => {
    try {
      const response = await adminService.getDestinations();
      setDestinations(response.data);
    } catch (error) {
      console.error('Error fetching destinations:', error);
      toast.error('Failed to load destinations');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (data) => {
    try {
      if (editingDestination) {
        await adminService.updateDestination(destinations.indexOf(editingDestination), data);
        toast.success('Destination updated successfully');
      } else {
        await adminService.addDestination(data);
        toast.success('Destination added successfully');
      }
      fetchDestinations();
      setShowForm(false);
      setEditingDestination(null);
    } catch (error) {
      toast.error('Failed to save destination');
    }
  };

  const handleDelete = async (index) => {
    if (window.confirm('Are you sure you want to delete this destination?')) {
      try {
        await adminService.deleteDestination(index);
        toast.success('Destination deleted');
        fetchDestinations();
      } catch (error) {
        toast.error('Failed to delete destination');
      }
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
    <div className="destinations-management">
      <div className="management-header">
        <h2>Manage Destinations</h2>
        <button className="add-btn" onClick={() => { setEditingDestination(null); setShowForm(true); }}>
          <FaPlus /> Add Destination
        </button>
      </div>

      {loading ? (
        <div className="loading">Loading...</div>
      ) : (
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Type</th>
                <th>Region</th>
                <th>Cost</th>
                <th>Rating</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {destinations.map((dest, index) => (
                <tr key={index}>
                  <td>{dest.name}</td>
                  <td><span className={`type-badge ${dest.type.toLowerCase()}`}>{dest.type}</span></td>
                  <td>{dest.region}</td>
                  <td>{formatCurrency(dest.cost)}</td>
                  <td>⭐ {dest.user_rating?.toFixed(1)}</td>
                  <td className="actions-cell">
                    <button 
                      className="edit-btn"
                      onClick={() => { setEditingDestination(dest); setShowForm(true); }}
                    >
                      <FaEdit />
                    </button>
                    <button 
                      className="delete-btn"
                      onClick={() => handleDelete(index)}
                    >
                      <FaTrash />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {showForm && (
        <DestinationForm
          destination={editingDestination}
          onSave={handleSave}
          onClose={() => { setShowForm(false); setEditingDestination(null); }}
        />
      )}
    </div>
  );
};

// Cost Rates Management
const CostRatesManagement = () => {
  const [costRates, setCostRates] = useState({});
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);

  useEffect(() => {
    fetchCostRates();
  }, []);

  const fetchCostRates = async () => {
    try {
      const response = await adminService.getCostRates();
      setCostRates(response.data);
    } catch (error) {
      toast.error('Failed to load cost rates');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (region, field, value) => {
    setCostRates(prev => ({
      ...prev,
      [region]: {
        ...prev[region],
        [field]: parseInt(value) || 0
      }
    }));
  };

  const handleSave = async () => {
    try {
      await adminService.updateCostRates(costRates);
      toast.success('Cost rates updated successfully');
      setEditing(false);
    } catch (error) {
      toast.error('Failed to update cost rates');
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
    <div className="cost-rates-management">
      <div className="management-header">
        <h2>Cost Rates by Region</h2>
        {editing ? (
          <div className="edit-actions">
            <button className="cancel-btn" onClick={() => { setEditing(false); fetchCostRates(); }}>
              Cancel
            </button>
            <button className="save-btn" onClick={handleSave}>
              <FaSave /> Save Changes
            </button>
          </div>
        ) : (
          <button className="edit-btn" onClick={() => setEditing(true)}>
            <FaEdit /> Edit Rates
          </button>
        )}
      </div>

      {loading ? (
        <div className="loading">Loading...</div>
      ) : (
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Region</th>
                <th>Hotel/Day</th>
                <th>Travel</th>
                <th>Meals/Day</th>
                <th>Activities</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(costRates).map(([region, rates]) => (
                <tr key={region}>
                  <td><strong>{region}</strong></td>
                  <td>
                    {editing ? (
                      <input
                        type="number"
                        value={rates.hotel_per_day}
                        onChange={(e) => handleChange(region, 'hotel_per_day', e.target.value)}
                        step="500"
                      />
                    ) : formatCurrency(rates.hotel_per_day)}
                  </td>
                  <td>
                    {editing ? (
                      <input
                        type="number"
                        value={rates.travel}
                        onChange={(e) => handleChange(region, 'travel', e.target.value)}
                        step="500"
                      />
                    ) : formatCurrency(rates.travel)}
                  </td>
                  <td>
                    {editing ? (
                      <input
                        type="number"
                        value={rates.meals_per_day}
                        onChange={(e) => handleChange(region, 'meals_per_day', e.target.value)}
                        step="100"
                      />
                    ) : formatCurrency(rates.meals_per_day)}
                  </td>
                  <td>
                    {editing ? (
                      <input
                        type="number"
                        value={rates.activities}
                        onChange={(e) => handleChange(region, 'activities', e.target.value)}
                        step="500"
                      />
                    ) : formatCurrency(rates.activities)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

// Main Admin Dashboard Component
const AdminDashboard = () => {
  const location = useLocation();
  const [stats, setStats] = useState({
    total_destinations: 0,
    total_users: 0,
    average_user_rating: 0,
    destinations_by_type: {},
    destinations_by_region: {}
  });

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await adminService.getStats();
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const getActiveTab = () => {
    if (location.pathname.includes('destinations')) return 'destinations';
    if (location.pathname.includes('cost-rates')) return 'cost-rates';
    return 'overview';
  };

  return (
    <div className="admin-dashboard">
      <div className="admin-sidebar">
        <h2>Admin Panel</h2>
        <nav className="admin-nav">
          <Link 
            to="/admin" 
            className={getActiveTab() === 'overview' ? 'active' : ''}
          >
            <FaChartBar /> Overview
          </Link>
          <Link 
            to="/admin/destinations" 
            className={getActiveTab() === 'destinations' ? 'active' : ''}
          >
            <FaMapMarkerAlt /> Destinations
          </Link>
          <Link 
            to="/admin/cost-rates" 
            className={getActiveTab() === 'cost-rates' ? 'active' : ''}
          >
            <FaDollarSign /> Cost Rates
          </Link>
        </nav>
      </div>

      <div className="admin-content">
        <Routes>
          <Route index element={
            <div className="overview-section">
              <h1>Dashboard Overview</h1>
              <StatsOverview stats={stats} />
              
              <div className="charts-row">
                <div className="chart-card">
                  <h3>Destinations by Type</h3>
                  <div className="chart-bars">
                    {Object.entries(stats.destinations_by_type || {}).map(([type, count]) => (
                      <div key={type} className="bar-item">
                        <span className="bar-label">{type}</span>
                        <div className="bar-container">
                          <div 
                            className="bar-fill" 
                            style={{ width: `${(count / stats.total_destinations) * 100}%` }}
                          ></div>
                        </div>
                        <span className="bar-value">{count}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="chart-card">
                  <h3>Destinations by Region</h3>
                  <div className="chart-bars">
                    {Object.entries(stats.destinations_by_region || {}).map(([region, count]) => (
                      <div key={region} className="bar-item">
                        <span className="bar-label">{region}</span>
                        <div className="bar-container">
                          <div 
                            className="bar-fill region" 
                            style={{ width: `${(count / stats.total_destinations) * 100}%` }}
                          ></div>
                        </div>
                        <span className="bar-value">{count}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          } />
          <Route path="destinations" element={<DestinationsManagement />} />
          <Route path="cost-rates" element={<CostRatesManagement />} />
        </Routes>
      </div>
    </div>
  );
};

export default AdminDashboard;
