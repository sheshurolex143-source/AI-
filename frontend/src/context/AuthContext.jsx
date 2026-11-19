import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../api/client';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(() => localStorage.getItem('finsight_token'));
  const [currencySymbol, setCurrencySymbol] = useState(() => localStorage.getItem('finsight_currency') || '₹');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUser = async () => {
      if (token) {
        try {
          const res = await api.get('/api/auth/me');
          setUser(res.data);
        } catch (err) {
          console.error('Failed to load user', err);
          logout();
        }
      }
      setLoading(false);
    };
    fetchUser();
  }, [token]);

  const login = async (email, password) => {
    const res = await api.post('/api/auth/login', { email, password });
    const accessToken = res.data.access_token;
    localStorage.setItem('finsight_token', accessToken);
    setToken(accessToken);
    const userRes = await api.get('/api/auth/me', {
      headers: { Authorization: `Bearer ${accessToken}` },
    });
    setUser(userRes.data);
    return userRes.data;
  };

  const register = async (email, password, fullName) => {
    const res = await api.post('/api/auth/register', {
      email,
      password,
      full_name: fullName,
    });
    const accessToken = res.data.access_token;
    localStorage.setItem('finsight_token', accessToken);
    setToken(accessToken);
    const userRes = await api.get('/api/auth/me', {
      headers: { Authorization: `Bearer ${accessToken}` },
    });
    setUser(userRes.data);
    return userRes.data;
  };

  const logout = () => {
    localStorage.removeItem('finsight_token');
    setToken(null);
    setUser(null);
  };

  const updateCurrency = (symbol) => {
    setCurrencySymbol(symbol);
    localStorage.setItem('finsight_currency', symbol);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        loading,
        login,
        register,
        logout,
        isAuthenticated: !!token,
        currencySymbol,
        updateCurrency,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
