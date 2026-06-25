import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import ScrollToTop from './components/ScrollToTop';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import Profile from './pages/Profile';
import SharedTrip from './pages/SharedTrip';
import Destination from './pages/Destination';
import SearchResults from './pages/SearchResults';
import AdminDashboard from './pages/AdminDashboard';
import ItineraryPlanner from './pages/ItineraryPlanner';
import ProtectedRoute from './components/ProtectedRoute';
import './styles/App.css';
import './styles/ItineraryPlanner.css';
import './styles/SharedTrip.css';

function App() {
  return (
    <div className="app">
      <ScrollToTop />
      <Navbar />
      <main className="main-content">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/search" element={<SearchResults />} />
          <Route path="/planner" element={<ItineraryPlanner />} />
          <Route path="/shared-trip/:token" element={<SharedTrip />} />
          <Route path="/destination/:id" element={<Destination />} />
          <Route 
            path="/profile" 
            element={
              <ProtectedRoute>
                <Profile />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/admin/*" 
            element={
              <ProtectedRoute adminOnly>
                <AdminDashboard />
              </ProtectedRoute>
            } 
          />
        </Routes>
      </main>
      <Footer />
    </div>
  );
}

export default App;
