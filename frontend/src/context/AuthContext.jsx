/**
 * Auth Context
 * Manages authentication state across the application
 */

import { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(localStorage.getItem('token'));

  useEffect(() => {
    // Check if user is logged in on mount
    const checkAuth = async () => {
      if (token) {
        try {
          const response = await authAPI.getMe();
          setUser(response.data);
          
          // Load user profile
          try {
            const profileResponse = await authAPI.getProfile();
            setProfile(profileResponse.data);
          } catch (err) {
            console.warn('Could not load profile:', err.message);
          }
        } catch {
          // Token invalid, clear it
          localStorage.removeItem('token');
          setToken(null);
        }
      }
      setLoading(false);
    };
    checkAuth();
  }, [token]);

  const login = async (email, password) => {
    const response = await authAPI.login(email, password);
    const { access_token } = response.data;
    localStorage.setItem('token', access_token);
    setToken(access_token);
    
    // Get user info
    const userResponse = await authAPI.getMe();
    setUser(userResponse.data);
    
    // Load user profile
    try {
      const profileResponse = await authAPI.getProfile();
      setProfile(profileResponse.data);
    } catch (err) {
      console.warn('Could not load profile:', err.message);
    }
    
    return userResponse.data;
  };

  const register = async (userData) => {
    const response = await authAPI.register(userData);
    return response.data;
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('anonymousRequestCount');
    setToken(null);
    setUser(null);
    setProfile(null);
  };

  const updateProfile = async (profileData) => {
    try {
      const response = await authAPI.updateProfile(profileData);
      setProfile(response.data);
      return response.data;
    } catch (err) {
      console.error('Failed to update profile:', err);
      throw err;
    }
  };

  const uploadProfilePicture = async (file) => {
    try {
      const response = await authAPI.uploadProfilePicture(file);
      // Update profile with new picture URL
      setProfile(prev => ({
        ...prev,
        profilePictureUrl: response.data.profilePictureUrl
      }));
      return response.data;
    } catch (err) {
      console.error('Failed to upload profile picture:', err);
      throw err;
    }
  };

  const value = {
    user,
    profile,
    token,
    loading,
    login,
    register,
    logout,
    updateProfile,
    uploadProfilePicture,
    isAuthenticated: !!token && !!user,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    // Return a default context during initialization/hot-refresh
    return {
      user: null,
      token: null,
      loading: true,
      login: async () => {},
      register: async () => {},
      logout: () => {},
      isAuthenticated: false,
    };
  }
  return context;
}
