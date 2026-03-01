import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { FaFilter, FaTimes, FaSearch } from 'react-icons/fa';
import SearchBar from '../components/SearchBar';
import DestinationCard from '../components/DestinationCard';
import { destinationService } from '../services/api';
import '../styles/SearchResults.css';

const SearchResults = () => {
  const [searchParams] = useSearchParams();
  const query = searchParams.get('q') || '';
  
  const [results, setResults] = useState([]);
  const [parsedQuery, setParsedQuery] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  
  const [filters, setFilters] = useState({
    type: '',
    region: '',
    maxCost: '',
    minRating: ''
  });

  const travelTypes = ['Adventure', 'Relaxation', 'Family', 'Cultural', 'Historical', 'Religious'];
  const regions = ['Gilgit Baltistan', 'KPK', 'Punjab', 'Sindh', 'Balochistan', 'AJK'];

  useEffect(() => {
    if (query) {
      handleSearch(query);
    } else {
      // Load all destinations if no query
      loadAllDestinations();
    }
  }, [query]);

  const loadAllDestinations = async () => {
    setLoading(true);
    try {
      const response = await destinationService.getAll();
      setResults(response.data);
      setParsedQuery(null);
    } catch (error) {
      console.error('Error loading destinations:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (searchQuery) => {
    setLoading(true);
    try {
      const response = await destinationService.search(searchQuery);
      setResults(response.data.destinations);
      setParsedQuery(response.data.parsed_query);
    } catch (error) {
      console.error('Search error:', error);
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = async () => {
    setLoading(true);
    try {
      const params = {};
      if (filters.type) params.type = filters.type;
      if (filters.region) params.region = filters.region;
      if (filters.maxCost) params.max_cost = parseInt(filters.maxCost);
      
      const response = await destinationService.getAll(params);
      let filtered = response.data;
      
      if (filters.minRating) {
        filtered = filtered.filter(d => d.user_rating >= parseFloat(filters.minRating));
      }
      
      setResults(filtered);
    } catch (error) {
      console.error('Filter error:', error);
    } finally {
      setLoading(false);
    }
  };

  const clearFilters = () => {
    setFilters({ type: '', region: '', maxCost: '', minRating: '' });
    if (query) {
      handleSearch(query);
    } else {
      loadAllDestinations();
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
    <div className="search-results-page">
      <div className="search-header">
        <SearchBar initialQuery={query} onSearch={handleSearch} />
      </div>

      <div className="results-container">
        {/* Filters Sidebar */}
        <aside className={`filters-sidebar ${showFilters ? 'active' : ''}`}>
          <div className="filters-header">
            <h3><FaFilter /> Filters</h3>
            <button className="close-filters" onClick={() => setShowFilters(false)}>
              <FaTimes />
            </button>
          </div>

          <div className="filter-group">
            <label>Travel Type</label>
            <select 
              value={filters.type} 
              onChange={(e) => setFilters({...filters, type: e.target.value})}
            >
              <option value="">All Types</option>
              {travelTypes.map(type => (
                <option key={type} value={type}>{type}</option>
              ))}
            </select>
          </div>

          <div className="filter-group">
            <label>Region</label>
            <select 
              value={filters.region} 
              onChange={(e) => setFilters({...filters, region: e.target.value})}
            >
              <option value="">All Regions</option>
              {regions.map(region => (
                <option key={region} value={region}>{region}</option>
              ))}
            </select>
          </div>

          <div className="filter-group">
            <label>Maximum Budget (PKR)</label>
            <input
              type="number"
              value={filters.maxCost}
              onChange={(e) => setFilters({...filters, maxCost: e.target.value})}
              placeholder="e.g., 30000"
              step="5000"
            />
          </div>

          <div className="filter-group">
            <label>Minimum Rating</label>
            <select 
              value={filters.minRating} 
              onChange={(e) => setFilters({...filters, minRating: e.target.value})}
            >
              <option value="">Any Rating</option>
              <option value="4.5">4.5+ Stars</option>
              <option value="4.0">4.0+ Stars</option>
              <option value="3.5">3.5+ Stars</option>
            </select>
          </div>

          <div className="filter-actions">
            <button className="apply-btn" onClick={applyFilters}>Apply Filters</button>
            <button className="clear-btn" onClick={clearFilters}>Clear All</button>
          </div>
        </aside>

        {/* Results Main Area */}
        <main className="results-main">
          {/* Results Header */}
          <div className="results-header">
            <div className="results-info">
              <h2>
                {query ? `Results for "${query}"` : 'All Destinations'}
              </h2>
              <p>{results.length} destinations found</p>
            </div>
            <button 
              className="filter-toggle"
              onClick={() => setShowFilters(!showFilters)}
            >
              <FaFilter /> Filters
            </button>
          </div>

          {/* Parsed Query Info */}
          {parsedQuery && Object.keys(parsedQuery).length > 1 && (
            <div className="parsed-query-info">
              <h4>We understood:</h4>
              <div className="parsed-tags">
                {parsedQuery.days && (
                  <span className="parsed-tag">📅 {parsedQuery.days} days</span>
                )}
                {parsedQuery.budget && (
                  <span className="parsed-tag">💰 Under {formatCurrency(parsedQuery.budget)}</span>
                )}
                {parsedQuery.region && (
                  <span className="parsed-tag">📍 {parsedQuery.region}</span>
                )}
                {parsedQuery.type && (
                  <span className="parsed-tag">🎯 {parsedQuery.type}</span>
                )}
                {parsedQuery.destination && (
                  <span className="parsed-tag">🏔️ {parsedQuery.destination}</span>
                )}
              </div>
            </div>
          )}

          {/* Results Grid */}
          {loading ? (
            <div className="loading-grid">
              {[1, 2, 3, 4, 5, 6].map(i => (
                <div key={i} className="skeleton-card"></div>
              ))}
            </div>
          ) : results.length > 0 ? (
            <div className="results-grid">
              {results.map((dest, index) => (
                <DestinationCard 
                  key={index} 
                  destination={dest} 
                  showBudget={!!parsedQuery?.days}
                />
              ))}
            </div>
          ) : (
            <div className="no-results">
              <FaSearch className="no-results-icon" />
              <h3>No destinations found</h3>
              <p>Try adjusting your search or filters</p>
              <button onClick={clearFilters}>Clear Filters</button>
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

export default SearchResults;
