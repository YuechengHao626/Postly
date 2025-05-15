import React, { createContext, useState, useContext, useEffect } from 'react';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const parseToken = (token) => {
    try {
      const tokenParts = token.split('.');
      const payload = JSON.parse(atob(tokenParts[1]));
      console.log('Parsed token payload:', payload);
      return payload;
    } catch (error) {
      console.error('Error parsing token:', error);
      return null;
    }
  };

  // 从后端获取最新的用户信息
  const updateUserInfo = async () => {
    console.log('Starting updateUserInfo...');
    try {
      const token = localStorage.getItem('access_token');
      console.log('Using token:', token);

      const response = await fetch('/api/user/detail/', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      console.log('Response status:', response.status);
      if (response.ok) {
        const userData = await response.json();
        console.log('Received user data:', userData);
        
        // 获取当前用户信息进行比较
        const currentUser = user;
        const storedInfo = localStorage.getItem('user_info');
        console.log('Current user state:', currentUser);
        console.log('Current stored info:', storedInfo);
        
        // 更新状态和存储
        setUser(userData);
        localStorage.setItem('user_info', JSON.stringify(userData));
        console.log('User info updated successfully');
        
        // 验证更新
        const newStoredInfo = localStorage.getItem('user_info');
        console.log('New stored info:', newStoredInfo);
      } else {
        const errorData = await response.json();
        console.error('Failed to fetch user info:', errorData);
      }
    } catch (error) {
      console.error('Error in updateUserInfo:', error);
      throw error; // 重新抛出错误以便调用者处理
    }
  };

  useEffect(() => {
    // 检查本地存储中的token
    const token = localStorage.getItem('access_token');
    const userInfo = localStorage.getItem('user_info');
    console.log('Initial token:', token);
    console.log('Initial user info:', userInfo);

    if (token && userInfo) {
      try {
        const payload = parseToken(token);
        const storedUser = JSON.parse(userInfo);
        console.log('Stored user:', storedUser);
        console.log('Token payload:', payload);

        if (payload && payload.role !== storedUser.role) {
          console.log('Role mismatch, updating from token');
          const updatedUser = { ...storedUser, role: payload.role };
          setUser(updatedUser);
          localStorage.setItem('user_info', JSON.stringify(updatedUser));
        } else {
          setUser(storedUser);
        }
      } catch (error) {
        console.error('Error in auth initialization:', error);
        setUser(JSON.parse(userInfo));
      }
    }
    setLoading(false);
  }, []);

  const login = (tokens, username) => {
    try {
      const payload = parseToken(tokens.access);
      console.log('Login payload:', payload);
      if (payload) {
        const userData = {
          username: username,
          role: payload.role,
        };
        console.log('Setting user data:', userData);
        setUser(userData);
        localStorage.setItem('access_token', tokens.access);
        localStorage.setItem('refresh_token', tokens.refresh);
        localStorage.setItem('user_info', JSON.stringify(userData));
        // 登录后立即获取最新的用户信息
        updateUserInfo();
      }
    } catch (error) {
      console.error('Error in login:', error);
    }
  };

  const updateTokens = (accessToken, refreshToken) => {
    console.log('Updating tokens');
    // 更新本地存储中的token
    localStorage.setItem('access_token', accessToken);
    localStorage.setItem('refresh_token', refreshToken);

    // 解析新的access token以获取用户信息
    try {
      const payload = parseToken(accessToken);
      console.log('Update tokens payload:', payload);
      if (payload) {
        const userData = {
          ...user,
          role: payload.role,
        };
        console.log('Updating user data:', userData);
        setUser(userData);
        localStorage.setItem('user_info', JSON.stringify(userData));
      }
    } catch (error) {
      console.error('Error in updateTokens:', error);
    }
  };

  const logout = async () => {
    const refresh_token = localStorage.getItem('refresh_token');
    const access_token = localStorage.getItem('access_token');
    
    try {
      const response = await fetch('/api/auth/logout/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${access_token}`,
        },
        body: JSON.stringify({ refresh_token }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || 'Logout failed');
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // 无论服务器响应如何，都清除本地存储
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user_info');
      setUser(null);
    }
  };

  const value = {
    user,
    login,
    logout,
    loading,
    updateTokens,
    updateUserInfo  // 导出 updateUserInfo 函数
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}; 