import React from 'react';
import { FaHotel, FaBus, FaUtensils, FaHiking, FaCalculator } from 'react-icons/fa';
import '../styles/BudgetTable.css';

const BudgetTable = ({ budgetData, destination, days }) => {
  const { hotel, travel, meals, activities, total } = budgetData;

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-PK', {
      style: 'currency',
      currency: 'PKR',
      maximumFractionDigits: 0
    }).format(amount);
  };

  const budgetItems = [
    { icon: FaHotel, label: `Hotel (${days} nights)`, cost: hotel, color: '#3b82f6' },
    { icon: FaBus, label: 'Travel/Transport', cost: travel, color: '#10b981' },
    { icon: FaUtensils, label: `Meals (${days} days)`, cost: meals, color: '#f59e0b' },
    { icon: FaHiking, label: 'Activities', cost: activities, color: '#8b5cf6' }
  ];

  const getPercentage = (cost) => ((cost / total) * 100).toFixed(1);

  return (
    <div className="budget-table-container">
      <div className="budget-header">
        <FaCalculator className="budget-icon" />
        <div>
          <h3>Budget Estimation</h3>
          <p>{destination} • {days} Days Trip</p>
        </div>
      </div>

      <div className="budget-breakdown">
        {budgetItems.map((item, index) => (
          <div key={index} className="budget-item">
            <div className="item-info">
              <item.icon className="item-icon" style={{ color: item.color }} />
              <span className="item-label">{item.label}</span>
            </div>
            <div className="item-cost">
              <span className="cost-value">{formatCurrency(item.cost)}</span>
              <span className="cost-percentage">{getPercentage(item.cost)}%</span>
            </div>
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ 
                  width: `${getPercentage(item.cost)}%`,
                  backgroundColor: item.color 
                }}
              ></div>
            </div>
          </div>
        ))}
      </div>

      <div className="budget-total">
        <span className="total-label">Total Estimated Cost</span>
        <span className="total-value">{formatCurrency(total)}</span>
      </div>

      <div className="budget-tips">
        <h4>💡 Budget Tips</h4>
        <ul>
          <li>Book hotels in advance for better rates</li>
          <li>Consider local transport options</li>
          <li>Try local cuisine for authentic experience</li>
          <li>Travel during off-peak season for discounts</li>
        </ul>
      </div>
    </div>
  );
};

export default BudgetTable;
