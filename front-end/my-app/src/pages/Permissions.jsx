import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate, Link } from 'react-router-dom';
import BackButton from '../components/BackButton';

const Toast = ({ message, type, onClose }) => {
  useEffect(() => {
    const timer = setTimeout(() => {
      onClose();
    }, 3000);
    return () => clearTimeout(timer);
  }, [onClose]);

  const bgColor = type === 'success' ? 'bg-green-500' : 'bg-red-500';

  return (
    <div className={`fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 ${bgColor} text-white px-6 py-3 rounded-lg shadow-lg z-[100] animate-fade-in-down min-w-[300px] text-center`}>
      {message}
    </div>
  );
};

const SubforumCard = ({ subforum }) => {
  return (
    <Link
      to={`/subforum/${subforum.id}`}
      className="block bg-gray-50 rounded-lg p-4 border border-gray-200 hover:border-blue-500 hover:shadow-md transition-all duration-200 group"
    >
      <div className="flex justify-between items-start mb-2">
        <h3 className="font-medium text-lg group-hover:text-blue-600 transition-colors">
          {subforum.name}
        </h3>
        <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
          View Details →
        </span>
      </div>
      <p className="text-sm text-gray-600 mb-3 line-clamp-2">{subforum.description}</p>
      <div className="flex items-center justify-end text-sm">
        <div className="flex items-center gap-2">
          <span className="text-gray-500">
            <span className="font-medium">{subforum.post_count || 0}</span>
            <span className="text-gray-400"> posts</span>
          </span>
        </div>
      </div>
    </Link>
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
  const [activeTab, setActiveTab] = useState('assign');
  const [searchResults, setSearchResults] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [formData, setFormData] = useState({
    username: '',
    subforumName: '',
    role: ''
  });
  const [isSearching, setIsSearching] = useState(false);
  const [noResults, setNoResults] = useState(false);
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

          // 如果是子论坛管理员或超级管理员，获取论坛列表
          if (userData.role === 'subforum_admin' || userData.role === 'super_admin') {
            const endpoint = userData.role === 'super_admin' 
              ? '/api/subforums/' 
              : '/api/moderator/my-subforums/';
              
            const subforumsResponse = await fetch(endpoint, {
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

  const handleInputChange = async (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    setError(null);

    // 当用户输入用户名时，进行搜索
    if (name === 'username' && value.trim()) {
      setIsSearching(true);
      setNoResults(false);
      try {
        const response = await fetch(`/api/search/users/?q=${encodeURIComponent(value)}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        });

        if (response.ok) {
          const data = await response.json();
          const results = data.results || data;
          setSearchResults(results);
          setNoResults(results.length === 0);
        }
      } catch (err) {
        console.error('Error searching users:', err);
        setNoResults(true);
      } finally {
        setIsSearching(false);
      }
    } else if (name === 'username') {
      setSearchResults([]);
      setNoResults(false);
    }
  };

  const handleUserSelect = async (user) => {
    setSelectedUser(user);
    setFormData(prev => ({
      ...prev,
      username: user.username
    }));
    setSearchResults([]);

    // 如果是撤职操作，获取用户的角色信息
    if (activeTab === 'remove') {
      try {
        const response = await fetch(`/api/moderator/my-subforums/`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        });

        if (response.ok) {
          const data = await response.json();
          setManagedSubforums(data);
        }
      } catch (err) {
        console.error('Error fetching subforums:', err);
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedUser || !formData.role) {
      showToast('Please select a user and a role', 'error');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      let endpoint;
      if (formData.role === 'subforum_admin') {
        endpoint = `/api/subforums/${formData.subforumName}/assign-admin/`;
      } else if (formData.role === 'moderator') {
        endpoint = `/api/subforums/${formData.subforumName}/assign-moderator/`;
      }

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
          user_id: selectedUser.id
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
        setSelectedUser(null);
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

  const handleRemoveRole = async (e) => {
    e.preventDefault();
    if (!selectedUser || !formData.subforumName) {
      showToast('Please select a user and a subforum', 'error');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const subforumId = formData.subforumName;
      const response = await fetch(`/api/subforums/${subforumId}/remove-moderator/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
          user_id: selectedUser.id
        })
      });

      const result = await response.json();

      if (response.ok) {
        showToast(result.detail || 'Role removed successfully', 'success');
        setFormData({
          username: '',
          subforumName: '',
          role: ''
        });
        setSelectedUser(null);
        setIsModalOpen(false);
      } else {
        showToast(result.detail || 'Failed to remove role', 'error');
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

      <main className="max-w-7xl mx-auto p-6 space-y-12">
        {/* Permissions Matrix Section */}
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
            Lower roles cannot ban or modify higher roles, even if granted moderation rights.<br />
            Note: Sub-forum Admins can delete sub-forums they created, but cannot delete other sub-forums.
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

        {/* Managed Subforums Section */}
        {(currentUser?.role === 'subforum_admin' || currentUser?.role === 'super_admin') && managedSubforums.length > 0 && (
          <section className="bg-white rounded-xl shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">
                {currentUser?.role === 'super_admin' ? 'All Sub-forums' : 'Your Managed Sub-forums'}
              </h2>
              <span className="text-sm text-gray-500">
                Click on a forum to view details
              </span>
            </div>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {managedSubforums.map((subforum) => (
                <SubforumCard key={subforum.id} subforum={subforum} />
              ))}
            </div>
          </section>
        )}
      </main>

      {/* Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold">Manage User Roles</h3>
              <div className="flex gap-2">
                <button
                  onClick={() => {
                    setActiveTab('assign');
                    setSelectedUser(null);
                    setFormData({ username: '', subforumName: '', role: '' });
                  }}
                  className={`px-4 py-2 rounded-md text-sm transition-colors ${
                    activeTab === 'assign'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  Assign Role
                </button>
                <button
                  onClick={() => {
                    setActiveTab('remove');
                    setSelectedUser(null);
                    setFormData({ username: '', subforumName: '', role: '' });
                  }}
                  className={`px-4 py-2 rounded-md text-sm transition-colors ${
                    activeTab === 'remove'
                      ? 'bg-red-600 text-white'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  Remove Role
                </button>
              </div>
            </div>

            <form onSubmit={activeTab === 'assign' ? handleSubmit : handleRemoveRole} className="space-y-4">
              <div className="relative">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Username
                </label>
                <input
                  type="text"
                  name="username"
                  value={formData.username}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Start typing to search users..."
                  required
                />
                {/* Search Results Dropdown */}
                {formData.username.trim() && !selectedUser && (
                  <div className="absolute z-10 w-full mt-1 bg-white border rounded-md shadow-lg max-h-60 overflow-auto">
                    {isSearching ? (
                      <div className="px-4 py-3 text-sm text-gray-500 text-center">
                        Searching...
                      </div>
                    ) : noResults ? (
                      <div className="px-4 py-3 text-sm text-gray-500 text-center">
                        No users found
                      </div>
                    ) : searchResults.length > 0 ? (
                      searchResults.map((user) => (
                        <button
                          key={user.id}
                          type="button"
                          onClick={() => handleUserSelect(user)}
                          className="w-full px-4 py-2 text-left hover:bg-gray-100 focus:outline-none"
                        >
                          <span className="font-medium">{user.username}</span>
                          <span className="text-sm text-gray-500 ml-2">({user.role})</span>
                        </button>
                      ))
                    ) : null}
                  </div>
                )}
              </div>

              {selectedUser && (
                <>
                  {activeTab === 'assign' && (
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
                  )}

                  {((activeTab === 'assign' && (formData.role === 'moderator' || formData.role === 'subforum_admin')) || 
                    (activeTab === 'remove' && managedSubforums.length > 0)) && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Sub-forum
                      </label>
                      <select
                        name="subforumName"
                        value={formData.subforumName}
                        onChange={handleInputChange}
                        className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        required
                      >
                        <option value="">Select a sub-forum</option>
                        {managedSubforums.map(sf => (
                          <option key={sf.id} value={sf.id}>
                            {sf.name}
                          </option>
                        ))}
                      </select>
                    </div>
                  )}
                </>
              )}

              <div className="flex justify-end gap-2 mt-6">
                <button
                  type="button"
                  onClick={() => {
                    setIsModalOpen(false);
                    setSelectedUser(null);
                    setFormData({ username: '', subforumName: '', role: '' });
                  }}
                  className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={loading || !selectedUser || (activeTab === 'assign' ? !formData.role : !formData.subforumName)}
                  className={`px-4 py-2 text-white rounded-md disabled:opacity-50 ${
                    activeTab === 'assign'
                      ? 'bg-blue-600 hover:bg-blue-700'
                      : 'bg-red-600 hover:bg-red-700'
                  }`}
                >
                  {loading
                    ? activeTab === 'assign'
                      ? 'Assigning...'
                      : 'Removing...'
                    : activeTab === 'assign'
                    ? 'Assign Role'
                    : 'Remove Role'}
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