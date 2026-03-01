import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FaSearch, FaMicrophone } from 'react-icons/fa';
import '../styles/SearchBar.css';

const SearchBar = ({ onSearch, initialQuery = '' }) => {
  const [query, setQuery] = useState(initialQuery);
  const [isFocused, setIsFocused] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim()) {
      if (onSearch) {
        onSearch(query);
      } else {
        navigate(`/search?q=${encodeURIComponent(query)}`);
      }
    }
  };

  const sampleQueries = [
    "Plan a 3-day trip to northern Pakistan under 25,000 PKR",
    "Adventure spots in Gilgit under 30,000",
    "Family trip to Murree for weekend",
    "Best beaches in Pakistan under 20k"
  ];

  return (
    <div className="search-bar-container">
      <form onSubmit={handleSubmit} className={`search-form ${isFocused ? 'focused' : ''}`}>
        <div className="search-input-wrapper">
          <FaSearch className="search-icon" />
          <input
            type="text"
            className="search-input"
            placeholder="Plan a 3-day trip to northern Pakistan under 25,000 PKR..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setTimeout(() => setIsFocused(false), 200)}
          />
          <button type="button" className="voice-btn" title="Voice search (coming soon)">
            <FaMicrophone />
          </button>
        </div>
        <button type="submit" className="search-btn">
          Search
        </button>
      </form>

      {isFocused && (
        <div className="search-suggestions">
          <p className="suggestions-title">Try searching for:</p>
          {sampleQueries.map((suggestion, index) => (
            <button
              key={index}
              className="suggestion-item"
              onClick={() => {
                setQuery(suggestion);
                if (onSearch) {
                  onSearch(suggestion);
                } else {
                  navigate(`/search?q=${encodeURIComponent(suggestion)}`);
                }
              }}
            >
              <FaSearch className="suggestion-icon" />
              {suggestion}
            </button>
          ))}
        </div>
      )}
    </div>
  );
};

export default SearchBar;
