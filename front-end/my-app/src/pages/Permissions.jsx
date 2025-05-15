import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

const Toast = ({ message, type, onClose }) => {
  useEffect(() => {
    const timer = setTimeout(() => {
      onClose();
    }, 3000);
    return () => clearTimeout(timer);
  }, [onClose]);

  const bgColor = type === 'success' ? 'bg-green-500' : 'bg-red-500';
  const position = type === 'success' ? 'top-4 right-4' : 'top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2';

  return (
    <div className={`fixed ${position} ${bgColor} text-white px-6 py-3 rounded-lg shadow-lg z-[100] animate-fade-in-down min-w-[300px] text-center`}>
      {message}
    </div>
  );
};

const Permissions = () => {
  const { updateUserInfo } = useAuth();
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [toast, setToast] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [managedSubforums, setManagedSubforums] = useState([]);
  const [formData, setFormData] = useState({
    username: '',
    subforumName: '',
    role: ''
  });
  const navigate = useNavigate();

  useEffect(() => {
    const fetchUserInfo = async () => {
      try {
        setLoading(true);
        const response = await fetch('/api/user/detail/', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        });

        if (response.ok) {
          const userData = await response.json();
          setCurrentUser(userData);
          await updateUserInfo();

          // 如果是子论坛管理员，获取其管理的论坛列表
          if (userData.role === 'subforum_admin') {
            const subforumsResponse = await fetch('/api/moderator/my-subforums/', {
              headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
              }
            });
            if (subforumsResponse.ok) {
              const subforumsData = await subforumsResponse.json();
              setManagedSubforums(subforumsData);
            }
          }
        } else {
          const errorData = await response.json();
          setError(errorData.error || 'Failed to fetch user information');
        }
      } catch (error) {
        console.error('Error fetching user info:', error);
        setError('Failed to load user information');
      } finally {
        setLoading(false);
      }
    };

    fetchUserInfo();
  }, []);

  const permissions = {
    'Create Sub-forums': {
      super_admin: true,
      subforum_admin: true,
      moderator: false,
      user: false
    },
    'Delete Sub-forums': {
      super_admin: true,
      subforum_admin: false,
      moderator: false,
      user: false
    },
    'Appoint Moderators': {
      super_admin: true,
      subforum_admin: true,
      moderator: false,
      user: false
    },
    'Delete Posts/Comments': {
      super_admin: true,
      subforum_admin: true,
      moderator: true,
      user: false
    },
    'Ban Users': {
      super_admin: true,
      subforum_admin: true,
      moderator: true,
      user: false
    },
    'Edit Forum Settings': {
      super_admin: true,
      subforum_admin: true,
      moderator: false,
      user: false
    },
    'Appoint / Ban Sub-forum Admin': {
      super_admin: true,
      subforum_admin: false,
      moderator: false,
      user: false
    }
  };

  const roleColors = {
    super_admin: 'text-red-600',
    subforum_admin: 'text-blue-600',
    moderator: 'text-green-600',
    user: 'text-gray-600'
  };

  const roleDisplayNames = {
    super_admin: 'Super Admin',
    subforum_admin: 'Sub-forum Admin',
    moderator: 'Moderator',
    user: 'Regular User'
  };

  const showToast = (message, type) => {
    setToast({ message, type });
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    // 清除之前的错误
    setError(null);
  };

  const validateForm = () => {
    if (!formData.username.trim()) {
      showToast('Please enter a username', 'error');
      return false;
    }

    if (!formData.role) {
      showToast('Please select a role', 'error');
      return false;
    }

    if ((formData.role === 'moderator' || formData.role === 'subforum_admin') && !formData.subforumName.trim()) {
      showToast('Please enter a subforum name', 'error');
      return false;
    }

    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateForm()) return;

    setLoading(true);
    setError(null);

    try {
      // 1. 首先搜索用户
      const userSearchResponse = await fetch(`/api/search/users/?q=${encodeURIComponent(formData.username)}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      if (!userSearchResponse.ok) {
        throw new Error('Failed to find user');
      }

      const userData = await userSearchResponse.json();
      const user = userData.results?.[0] || userData[0];

      if (!user) {
        showToast('User not found. Please check the username and try again.', 'error');
        return;
      }

      // 2. 如果需要，搜索子论坛
      let subforumId;
      if (formData.role === 'moderator' || formData.role === 'subforum_admin') {
        const subforumSearchResponse = await fetch(`/api/search/subforums/?q=${encodeURIComponent(formData.subforumName)}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        });

        if (!subforumSearchResponse.ok) {
          throw new Error('Failed to find subforum');
        }

        const subforumData = await subforumSearchResponse.json();
        const subforum = subforumData.results?.[0] || subforumData[0];

        if (!subforum) {
          showToast('Subforum not found. Please check the name and try again.', 'error');
          return;
        }

        subforumId = subforum.id;
      }

      // 3. 分配角色
      let endpoint;
      if (formData.role === 'subforum_admin') {
        endpoint = `/api/subforums/${subforumId}/assign-admin/`;
      } else if (formData.role === 'moderator') {
        endpoint = `/api/subforums/${subforumId}/assign-moderator/`;
      }

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
          user_id: user.id
        })
      });

      const result = await response.json();

      if (response.ok) {
        showToast(result.detail || 'Role assigned successfully', 'success');
        setFormData({
          username: '',
          subforumName: '',
          role: ''
        });
        setIsModalOpen(false);
      } else {
        showToast(result.detail || 'Failed to assign role', 'error');
      }
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-lg text-gray-600">Loading...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-lg text-red-600">{error}</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Show toast if exists */}
      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
        />
      )}

      <header className="bg-white shadow px-6 py-4 flex justify-between items-center">
        <div className="flex items-center gap-6">
          <h1 className="text-xl font-bold">Postly Admin Dashboard</h1>
          <nav className="hidden md:flex gap-4 text-sm text-blue-600">
            <a href="/" className="hover:underline">🏠 Forum Home</a>
            <a href="/profile" className="hover:underline">👤 My Profile</a>
          </nav>
        </div>
        <span className={`px-3 py-1 rounded-full text-sm ${roleColors[currentUser?.role]} bg-opacity-10 bg-current`}>
          {roleDisplayNames[currentUser?.role] || 'Guest'}
        </span>
      </header>

      <main className="max-w-7xl mx-auto p-6 space-y-12">
        {/* Managed Subforums Section */}
        {currentUser?.role === 'subforum_admin' && managedSubforums.length > 0 && (
          <section className="bg-white rounded-xl shadow p-6">
            <h2 className="text-lg font-semibold mb-4">Your Managed Sub-forums</h2>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {managedSubforums.map((subforum) => (
                <div
                  key={subforum.id}
                  className="bg-gray-50 rounded-lg p-4 border border-gray-200 hover:border-blue-500 transition-colors"
                >
                  <h3 className="font-medium text-lg mb-2">{subforum.name}</h3>
                  <p className="text-sm text-gray-600 mb-3">{subforum.description}</p>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-500">
                      {subforum.moderator_count || 0} moderators
                    </span>
                    <span className="text-gray-500">
                      {subforum.post_count || 0} posts
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        <section className="bg-white rounded-xl shadow p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold">Global Permissions Matrix</h2>
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-600">Current Role:</span>
              <span className={`font-semibold ${roleColors[currentUser?.role]}`}>
                {roleDisplayNames[currentUser?.role] || 'Guest'}
              </span>
            </div>
          </div>
          <p className="text-sm text-gray-500 mb-4">
            Role hierarchy: <strong>Super Admin &gt; Sub-forum Admin &gt; Moderator &gt; Regular User</strong>.<br />
            Lower roles cannot ban or modify higher roles, even if granted moderation rights.
          </p>

          <div className="overflow-x-auto mb-6">
            <table className="min-w-full text-sm border border-gray-200">
              <thead className="bg-gray-100">
                <tr>
                  <th scope="col" className="text-left p-3 border">Permission</th>
                  <th scope="col" className={`p-3 border text-red-600 ${currentUser?.role === 'super_admin' ? 'bg-red-50' : ''}`}>
                    Super Admin
                  </th>
                  <th scope="col" className={`p-3 border text-blue-600 ${currentUser?.role === 'subforum_admin' ? 'bg-blue-50' : ''}`}>
                    Sub-forum Admin
                  </th>
                  <th scope="col" className={`p-3 border text-green-600 ${currentUser?.role === 'moderator' ? 'bg-green-50' : ''}`}>
                    Moderator
                  </th>
                  <th scope="col" className={`p-3 border text-gray-600 ${currentUser?.role === 'user' ? 'bg-gray-50' : ''}`}>
                    Regular User
                  </th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(permissions).map(([permission, roles]) => (
                  <tr key={permission} className="hover:bg-gray-50">
                    <td className="p-3 border font-medium">{permission}</td>
                    {Object.entries(roles).map(([role, hasPermission]) => (
                      <td key={role} className={`text-center border ${currentUser?.role === role ? `bg-${roleColors[role].split('-')[1]}-50` : ''}`}>
                        {hasPermission ? '✅' : '❌'}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {(currentUser?.role === 'super_admin' || currentUser?.role === 'subforum_admin') && (
            <div className="text-right">
              <button
                onClick={() => setIsModalOpen(true)}
                className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 transition text-sm"
              >
                Manage Users →
              </button>
            </div>
          )}
        </section>
      </main>

      {/* Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold mb-4">Assign Role</h3>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Username
                </label>
                <input
                  type="text"
                  name="username"
                  value={formData.username}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Role
                </label>
                <select
                  name="role"
                  value={formData.role}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                >
                  <option value="">Select a role</option>
                  {currentUser?.role === 'super_admin' && (
                    <option value="subforum_admin">Sub-forum Admin</option>
                  )}
                  <option value="moderator">Moderator</option>
                </select>
              </div>

              {(formData.role === 'moderator' || formData.role === 'subforum_admin') && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Sub-forum Name
                  </label>
                  <input
                    type="text"
                    name="subforumName"
                    value={formData.subforumName}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  />
                </div>
              )}

              <div className="flex justify-end gap-2 mt-6">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
                >
                  {loading ? 'Assigning...' : 'Assign Role'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Permissions; 