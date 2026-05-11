import React, { useState, useEffect } from 'react';
import { Routes, Route, Link, useLocation } from 'react-router-dom';
import { 
  FaChartBar, FaMapMarkerAlt, FaUsers, FaDollarSign, 
  FaPlus, FaEdit, FaTrash, FaTimes, FaSave, FaGlobe,
  FaRobot, FaDatabase, FaComments, FaUserClock, FaSync,
  FaCog, FaCheck, FaExclamationTriangle
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
            <button type="button" className="admin-cancel-btn" onClick={onClose}>Cancel</button>
            <button type="submit" className="admin-save-btn"><FaSave /> Save</button>
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
        await adminService.updateDestination(editingDestination.id, data);
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
    const destination = destinations[index];
    if (window.confirm('Are you sure you want to delete this destination?')) {
      try {
        await adminService.deleteDestination(destination.id);
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

// Regions Management Component
const RegionsManagement = () => {
  const [regions, setRegions] = useState([
    { id: 1, name: 'Gilgit Baltistan', destinations: 8, status: 'active' },
    { id: 2, name: 'Punjab', destinations: 6, status: 'active' },
    { id: 3, name: 'Sindh', destinations: 4, status: 'active' },
    { id: 4, name: 'KPK', destinations: 5, status: 'active' },
    { id: 5, name: 'Balochistan', destinations: 3, status: 'active' },
    { id: 6, name: 'Kashmir', destinations: 4, status: 'active' }
  ]);
  const [showAddForm, setShowAddForm] = useState(false);
  const [newRegion, setNewRegion] = useState('');

  const handleAddRegion = () => {
    if (newRegion.trim()) {
      setRegions([...regions, { 
        id: regions.length + 1, 
        name: newRegion.trim(), 
        destinations: 0, 
        status: 'active' 
      }]);
      setNewRegion('');
      setShowAddForm(false);
      toast.success('Region added successfully');
    }
  };

  const handleDeleteRegion = (id) => {
    setRegions(regions.filter(r => r.id !== id));
    toast.success('Region deleted');
  };

  const toggleStatus = (id) => {
    setRegions(regions.map(r => 
      r.id === id ? { ...r, status: r.status === 'active' ? 'inactive' : 'active' } : r
    ));
  };

  return (
    <div className="regions-management">
      <div className="management-header">
        <h2><FaGlobe /> Regions Management</h2>
        <button className="add-btn" onClick={() => setShowAddForm(true)}>
          <FaPlus /> Add Region
        </button>
      </div>

      {showAddForm && (
        <div className="modal-overlay">
          <div className="modal-content compact">
            <div className="modal-header">
              <h3>Add New Region</h3>
              <button className="close-btn" onClick={() => setShowAddForm(false)}><FaTimes /></button>
            </div>
            <div className="form-group">
              <label>Region Name</label>
              <input 
                type="text" 
                value={newRegion} 
                onChange={(e) => setNewRegion(e.target.value)}
                placeholder="Enter region name"
              />
            </div>
            <div className="form-actions">
              <button className="cancel-btn" onClick={() => setShowAddForm(false)}>Cancel</button>
              <button className="save-btn" onClick={handleAddRegion}><FaSave /> Save</button>
            </div>
          </div>
        </div>
      )}

      <div className="table-container">
        <table className="data-table">
          <thead>
            <tr>
              <th>Region Name</th>
              <th>Destinations</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {regions.map((region) => (
              <tr key={region.id}>
                <td><strong>{region.name}</strong></td>
                <td>{region.destinations}</td>
                <td>
                  <span className={`status-badge ${region.status}`}>
                    {region.status}
                  </span>
                </td>
                <td className="actions-cell">
                  <button className="edit-btn" onClick={() => toggleStatus(region.id)}>
                    <FaCog />
                  </button>
                  <button className="delete-btn" onClick={() => handleDeleteRegion(region.id)}>
                    <FaTrash />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

// AI Models Management Component
const AIModelsManagement = () => {
  const [models, setModels] = useState([
    { 
      id: 1, 
      name: 'Content-Based Filtering', 
      version: '1.2.0',
      status: 'active',
      accuracy: 87,
      lastTrained: '2024-01-15',
      description: 'Recommends destinations based on activity preferences and user history'
    },
    { 
      id: 2, 
      name: 'Collaborative Filtering', 
      version: '2.0.1',
      status: 'active',
      accuracy: 92,
      lastTrained: '2024-01-20',
      description: 'Uses user similarity patterns for recommendations'
    },
    { 
      id: 3, 
      name: 'NLP Query Parser', 
      version: '1.5.0',
      status: 'active',
      accuracy: 95,
      lastTrained: '2024-01-18',
      description: 'Parses natural language queries for destination search'
    },
    { 
      id: 4, 
      name: 'Budget Optimizer', 
      version: '1.0.0',
      status: 'inactive',
      accuracy: 78,
      lastTrained: '2024-01-10',
      description: 'Optimizes trip costs based on user budget constraints'
    }
  ]);
  const [retraining, setRetraining] = useState(null);

  const handleRetrain = (id) => {
    setRetraining(id);
    setTimeout(() => {
      setModels(models.map(m => 
        m.id === id ? { 
          ...m, 
          lastTrained: new Date().toISOString().split('T')[0],
          accuracy: Math.min(99, m.accuracy + Math.floor(Math.random() * 3))
        } : m
      ));
      setRetraining(null);
      toast.success('Model retrained successfully');
    }, 2000);
  };

  const toggleModelStatus = (id) => {
    setModels(models.map(m => 
      m.id === id ? { ...m, status: m.status === 'active' ? 'inactive' : 'active' } : m
    ));
    toast.success('Model status updated');
  };

  return (
    <div className="ai-models-management">
      <div className="management-header">
        <h2><FaRobot /> AI Models Management</h2>
      </div>

      <div className="models-grid">
        {models.map((model) => (
          <div key={model.id} className={`model-card ${model.status}`}>
            <div className="model-header">
              <h3>{model.name}</h3>
              <span className={`status-badge ${model.status}`}>{model.status}</span>
            </div>
            <p className="model-description">{model.description}</p>
            <div className="model-stats">
              <div className="stat">
                <span className="stat-label">Version</span>
                <span className="stat-value">{model.version}</span>
              </div>
              <div className="stat">
                <span className="stat-label">Accuracy</span>
                <span className="stat-value">{model.accuracy}%</span>
              </div>
              <div className="stat">
                <span className="stat-label">Last Trained</span>
                <span className="stat-value">{model.lastTrained}</span>
              </div>
            </div>
            <div className="model-actions">
              <button 
                className={`retrain-btn ${retraining === model.id ? 'loading' : ''}`}
                onClick={() => handleRetrain(model.id)}
                disabled={retraining === model.id}
              >
                <FaSync className={retraining === model.id ? 'spinning' : ''} />
                {retraining === model.id ? 'Retraining...' : 'Retrain'}
              </button>
              <button 
                className={`toggle-btn ${model.status}`}
                onClick={() => toggleModelStatus(model.id)}
              >
                {model.status === 'active' ? 'Disable' : 'Enable'}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// Dataset Management Component
const DatasetManagement = () => {
  const [datasets, setDatasets] = useState([
    { id: 1, name: 'destinations.json', records: 25, lastUpdated: '2024-01-20', size: '45 KB' },
    { id: 2, name: 'cost_rates.json', records: 6, lastUpdated: '2024-01-18', size: '8 KB' },
    { id: 3, name: 'users.json', records: 3, lastUpdated: '2024-01-22', size: '12 KB' },
    { id: 4, name: 'user_preferences.json', records: 150, lastUpdated: '2024-01-21', size: '85 KB' },
    { id: 5, name: 'seasonal_data.json', records: 100, lastUpdated: '2024-01-15', size: '32 KB' }
  ]);
  const [syncing, setSyncing] = useState(null);
  const [showUpload, setShowUpload] = useState(false);

  const handleSync = (id) => {
    setSyncing(id);
    setTimeout(() => {
      setDatasets(datasets.map(d => 
        d.id === id ? { ...d, lastUpdated: new Date().toISOString().split('T')[0] } : d
      ));
      setSyncing(null);
      toast.success('Dataset synchronized');
    }, 1500);
  };

  const handleUpload = () => {
    setShowUpload(false);
    toast.success('Dataset uploaded successfully');
  };

  return (
    <div className="dataset-management">
      <div className="management-header">
        <h2><FaDatabase /> Recommendation Datasets</h2>
        <button className="add-btn" onClick={() => setShowUpload(true)}>
          <FaPlus /> Upload Dataset
        </button>
      </div>

      {showUpload && (
        <div className="modal-overlay">
          <div className="modal-content compact">
            <div className="modal-header">
              <h3>Upload Dataset</h3>
              <button className="close-btn" onClick={() => setShowUpload(false)}><FaTimes /></button>
            </div>
            <div className="form-group">
              <label>Dataset Type</label>
              <select>
                <option>Destinations Data</option>
                <option>User Preferences</option>
                <option>Cost Rates</option>
                <option>Seasonal Data</option>
              </select>
            </div>
            <div className="form-group">
              <label>Upload File (JSON/CSV)</label>
              <input type="file" accept=".json,.csv" />
            </div>
            <div className="form-actions">
              <button className="cancel-btn" onClick={() => setShowUpload(false)}>Cancel</button>
              <button className="save-btn" onClick={handleUpload}><FaSave /> Upload</button>
            </div>
          </div>
        </div>
      )}

      <div className="table-container">
        <table className="data-table">
          <thead>
            <tr>
              <th>Dataset Name</th>
              <th>Records</th>
              <th>Size</th>
              <th>Last Updated</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {datasets.map((dataset) => (
              <tr key={dataset.id}>
                <td><strong>{dataset.name}</strong></td>
                <td>{dataset.records}</td>
                <td>{dataset.size}</td>
                <td>{dataset.lastUpdated}</td>
                <td className="actions-cell">
                  <button 
                    className={`sync-btn ${syncing === dataset.id ? 'loading' : ''}`}
                    onClick={() => handleSync(dataset.id)}
                    disabled={syncing === dataset.id}
                  >
                    <FaSync className={syncing === dataset.id ? 'spinning' : ''} />
                  </button>
                  <button className="edit-btn"><FaEdit /></button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

// User Activity Statistics Component
const UserActivityStats = () => {
  const [activityData] = useState({
    totalSearches: 1247,
    totalBookmarks: 89,
    averageSessionTime: '12 min',
    popularSearches: [
      { query: 'hunza in summer', count: 145 },
      { query: 'beach destinations', count: 98 },
      { query: 'budget trip under 50000', count: 87 },
      { query: 'adventure in gilgit', count: 76 },
      { query: 'family vacation', count: 65 }
    ],
    userActivity: [
      { date: '2024-01-22', searches: 45, signups: 3 },
      { date: '2024-01-21', searches: 67, signups: 5 },
      { date: '2024-01-20', searches: 52, signups: 2 },
      { date: '2024-01-19', searches: 78, signups: 4 },
      { date: '2024-01-18', searches: 43, signups: 1 }
    ],
    topDestinations: [
      { name: 'Hunza Valley', views: 456 },
      { name: 'Skardu', views: 389 },
      { name: 'Naran Kaghan', views: 312 },
      { name: 'Swat Valley', views: 287 },
      { name: 'Karachi Beach', views: 234 }
    ]
  });

  return (
    <div className="user-activity-stats">
      <div className="management-header">
        <h2><FaUserClock /> User Activity Statistics</h2>
      </div>

      <div className="activity-overview">
        <div className="activity-card">
          <FaChartBar className="activity-icon" />
          <div className="activity-info">
            <span className="activity-value">{activityData.totalSearches}</span>
            <span className="activity-label">Total Searches</span>
          </div>
        </div>
        <div className="activity-card">
          <FaUsers className="activity-icon" />
          <div className="activity-info">
            <span className="activity-value">{activityData.totalBookmarks}</span>
            <span className="activity-label">Bookmarks</span>
          </div>
        </div>
        <div className="activity-card">
          <FaUserClock className="activity-icon" />
          <div className="activity-info">
            <span className="activity-value">{activityData.averageSessionTime}</span>
            <span className="activity-label">Avg Session</span>
          </div>
        </div>
      </div>

      <div className="activity-details">
        <div className="detail-card">
          <h3>Popular Searches</h3>
          <ul className="search-list">
            {activityData.popularSearches.map((search, index) => (
              <li key={index}>
                <span className="search-query">"{search.query}"</span>
                <span className="search-count">{search.count}</span>
              </li>
            ))}
          </ul>
        </div>

        <div className="detail-card">
          <h3>Top Destinations</h3>
          <ul className="destination-list">
            {activityData.topDestinations.map((dest, index) => (
              <li key={index}>
                <span className="dest-rank">#{index + 1}</span>
                <span className="dest-name">{dest.name}</span>
                <span className="dest-views">{dest.views} views</span>
              </li>
            ))}
          </ul>
        </div>

        <div className="detail-card">
          <h3>Daily Activity</h3>
          <div className="activity-table">
            <table>
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Searches</th>
                  <th>Signups</th>
                </tr>
              </thead>
              <tbody>
                {activityData.userActivity.map((day, index) => (
                  <tr key={index}>
                    <td>{day.date}</td>
                    <td>{day.searches}</td>
                    <td>{day.signups}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

// Feedback Management Component
const FeedbackManagement = () => {
  const [feedbacks, setFeedbacks] = useState([
    { id: 1, user: 'john@email.com', destination: 'Hunza Valley', rating: 5, comment: 'Amazing experience! The recommendations were spot on.', date: '2024-01-22', status: 'new' },
    { id: 2, user: 'sara@email.com', destination: 'Skardu', rating: 4, comment: 'Good trip overall. Budget estimation was helpful.', date: '2024-01-21', status: 'reviewed' },
    { id: 3, user: 'ahmed@email.com', destination: 'Karachi Beach', rating: 3, comment: 'Expected more activity suggestions.', date: '2024-01-20', status: 'new' },
    { id: 4, user: 'fatima@email.com', destination: 'Naran Kaghan', rating: 5, comment: 'Perfect recommendations for family trip!', date: '2024-01-19', status: 'resolved' },
    { id: 5, user: 'ali@email.com', destination: 'Swat Valley', rating: 4, comment: 'Loved the AI suggestions. Very accurate!', date: '2024-01-18', status: 'reviewed' }
  ]);

  const updateStatus = (id, status) => {
    setFeedbacks(feedbacks.map(f => f.id === id ? { ...f, status } : f));
    toast.success('Feedback status updated');
  };

  const getStatusIcon = (status) => {
    switch(status) {
      case 'new': return <FaExclamationTriangle style={{ color: '#f59e0b' }} />;
      case 'reviewed': return <FaCheck style={{ color: '#3b82f6' }} />;
      case 'resolved': return <FaCheck style={{ color: '#10b981' }} />;
      default: return null;
    }
  };

  return (
    <div className="feedback-management">
      <div className="management-header">
        <h2><FaComments /> User Feedback</h2>
      </div>

      <div className="feedback-summary">
        <div className="feedback-stat">
          <span className="stat-number">{feedbacks.filter(f => f.status === 'new').length}</span>
          <span className="stat-label">New</span>
        </div>
        <div className="feedback-stat">
          <span className="stat-number">{feedbacks.filter(f => f.status === 'reviewed').length}</span>
          <span className="stat-label">Reviewed</span>
        </div>
        <div className="feedback-stat">
          <span className="stat-number">{feedbacks.filter(f => f.status === 'resolved').length}</span>
          <span className="stat-label">Resolved</span>
        </div>
      </div>

      <div className="feedback-list">
        {feedbacks.map((feedback) => (
          <div key={feedback.id} className={`feedback-card ${feedback.status}`}>
            <div className="feedback-header">
              <div className="feedback-user">
                <strong>{feedback.user}</strong>
                <span className="feedback-destination">on {feedback.destination}</span>
              </div>
              <div className="feedback-meta">
                <span className="feedback-rating">
                  {'⭐'.repeat(feedback.rating)}
                </span>
                <span className="feedback-date">{feedback.date}</span>
              </div>
            </div>
            <p className="feedback-comment">"{feedback.comment}"</p>
            <div className="feedback-actions">
              <span className={`status-badge ${feedback.status}`}>
                {getStatusIcon(feedback.status)} {feedback.status}
              </span>
              <div className="action-buttons">
                {feedback.status !== 'reviewed' && (
                  <button 
                    className="action-btn review"
                    onClick={() => updateStatus(feedback.id, 'reviewed')}
                  >
                    Mark Reviewed
                  </button>
                )}
                {feedback.status !== 'resolved' && (
                  <button 
                    className="action-btn resolve"
                    onClick={() => updateStatus(feedback.id, 'resolved')}
                  >
                    Resolve
                  </button>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
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
    if (location.pathname.includes('regions')) return 'regions';
    if (location.pathname.includes('models')) return 'models';
    if (location.pathname.includes('datasets')) return 'datasets';
    if (location.pathname.includes('activity')) return 'activity';
    if (location.pathname.includes('feedback')) return 'feedback';
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
          <Link 
            to="/admin/regions" 
            className={getActiveTab() === 'regions' ? 'active' : ''}
          >
            <FaGlobe /> Regions
          </Link>
          <Link 
            to="/admin/models" 
            className={getActiveTab() === 'models' ? 'active' : ''}
          >
            <FaRobot /> AI Models
          </Link>
          <Link 
            to="/admin/datasets" 
            className={getActiveTab() === 'datasets' ? 'active' : ''}
          >
            <FaDatabase /> Datasets
          </Link>
          <Link 
            to="/admin/activity" 
            className={getActiveTab() === 'activity' ? 'active' : ''}
          >
            <FaUserClock /> Activity
          </Link>
          <Link 
            to="/admin/feedback" 
            className={getActiveTab() === 'feedback' ? 'active' : ''}
          >
            <FaComments /> Feedback
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
          <Route path="regions" element={<RegionsManagement />} />
          <Route path="models" element={<AIModelsManagement />} />
          <Route path="datasets" element={<DatasetManagement />} />
          <Route path="activity" element={<UserActivityStats />} />
          <Route path="feedback" element={<FeedbackManagement />} />
        </Routes>
      </div>
    </div>
  );
};

export default AdminDashboard;
