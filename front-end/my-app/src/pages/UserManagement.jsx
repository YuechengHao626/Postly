import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { CheckCircleIcon, XCircleIcon } from '@heroicons/react/24/solid';

const UserManagement = () => {
  const { user: currentUser } = useAuth();
  const [searchQuery, setSearchQuery] = useState('');
  const [searchType, setSearchType] = useState('user'); // 'user' or 'subforum'
  const [searchResults, setSearchResults] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [selectedSubforum, setSelectedSubforum] = useState(null);
  const [mySubforums, setMySubforums] = useState([]); // 当前管理员管理的子论坛
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  // 获取当前管理员管理的子论坛
  useEffect(() => {
    const fetchMySubforums = async () => {
      if (currentUser?.role === 'subforum_admin') {
        try {
          const response = await fetch('/api/moderator/my-subforums/', {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            }
          });
          if (response.ok) {
            const data = await response.json();
            setMySubforums(data);
          }
        } catch (error) {
          console.error('Error fetching subforums:', error);
        }
      }
    };

    fetchMySubforums();
  }, [currentUser]);

  // 搜索用户或子论坛
  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    
    setLoading(true);
    setError('');
    try {
      const endpoint = searchType === 'user' ? '/api/search/users/' : '/api/search/subforums/';
      const response = await fetch(`${endpoint}?q=${encodeURIComponent(searchQuery)}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setSearchResults(data.results || data);  // 处理分页响应
      } else {
        const errorData = await response.json();
        setError(errorData.message || 'Search failed');
      }
    } catch (error) {
      setError('Failed to perform search');
    } finally {
      setLoading(false);
    }
  };

  // 分配权限
  const assignRole = async (userId, role, subforumId = null) => {
    try {
      setLoading(true);
      setError('');
      setSuccess('');

      let endpoint;
      if (role === 'subforum_admin') {
        endpoint = `/api/moderator/assign-admin/${subforumId}/`;
      } else if (role === 'moderator') {
        endpoint = `/api/moderator/assign-moderator/${subforumId}/`;
      }

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
          user_id: userId
        })
      });

      const data = await response.json();

      if (response.ok) {
        setSuccess(data.detail || `Successfully assigned ${role} role`);
        // 刷新搜索结果
        handleSearch();
      } else {
        setError(data.detail || 'Failed to assign role');
      }
    } catch (error) {
      setError('An error occurred while assigning role');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <main className="max-w-7xl mx-auto">
        <div className="bg-white rounded-xl shadow p-6">
          <h1 className="text-2xl font-bold mb-6">User Role Management</h1>

          {/* Search Section */}
          <div className="mb-8">
            <div className="flex gap-4 mb-4">
              <select
                value={searchType}
                onChange={(e) => setSearchType(e.target.value)}
                className="rounded-md border border-gray-300 px-3 py-2"
              >
                <option value="user">Search Users</option>
                {currentUser?.role === 'super_admin' && (
                  <option value="subforum">Search Subforums</option>
                )}
              </select>
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder={`Search ${searchType === 'user' ? 'users' : 'subforums'}...`}
                className="flex-1 rounded-md border border-gray-300 px-4 py-2"
              />
              <button
                onClick={handleSearch}
                disabled={loading}
                className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 transition disabled:opacity-50"
              >
                {loading ? 'Searching...' : 'Search'}
              </button>
            </div>

            {/* Error and Success Messages */}
            {error && (
              <div className="mb-4 text-red-600 text-sm">{error}</div>
            )}
            {success && (
              <div className="mb-4 text-green-600 text-sm">{success}</div>
            )}

            {/* Search Results */}
            <div className="mt-6">
              {searchResults.length > 0 ? (
                <div className="border rounded-lg overflow-hidden">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          {searchType === 'user' ? 'Username' : 'Subforum Name'}
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Current Role
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Actions
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {searchResults.map((result) => (
                        <tr key={result.id}>
                          <td className="px-6 py-4 whitespace-nowrap">
                            {searchType === 'user' ? result.username : result.name}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            {result.role || 'N/A'}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            {searchType === 'user' && (
                              <div className="flex gap-2 items-center">
                                {currentUser?.role === 'super_admin' && (
                                  <button
                                    onClick={() => assignRole(result.id, 'subforum_admin')}
                                    disabled={result.role === 'subforum_admin' || loading}
                                    className="inline-flex items-center px-3 py-1.5 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
                                  >
                                    <CheckCircleIcon className="w-5 h-5 mr-1" />
                                    Make Subforum Admin
                                  </button>
                                )}
                                {(currentUser?.role === 'super_admin' || currentUser?.role === 'subforum_admin') && (
                                  <div className="flex items-center gap-2">
                                    <select
                                      onChange={(e) => {
                                        if (e.target.value) {
                                          assignRole(result.id, 'moderator', e.target.value);
                                        }
                                      }}
                                      className="rounded-md border border-gray-300 px-3 py-1.5 bg-white text-gray-700 hover:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors duration-200"
                                      disabled={loading}
                                    >
                                      <option value="">Assign as Moderator...</option>
                                      {currentUser?.role === 'super_admin' ? (
                                        searchResults
                                          .filter(sf => sf.type === 'subforum')
                                          .map(sf => (
                                            <option key={sf.id} value={sf.id}>
                                              {sf.name}
                                            </option>
                                          ))
                                      ) : (
                                        mySubforums.map(sf => (
                                          <option key={sf.id} value={sf.id}>
                                            {sf.name}
                                          </option>
                                        ))
                                      )}
                                    </select>
                                    <button
                                      onClick={() => {
                                        // Add confirmation logic here if needed
                                      }}
                                      className="inline-flex items-center p-1.5 text-red-600 hover:text-red-800 rounded-full hover:bg-red-100 transition-colors duration-200"
                                    >
                                      <XCircleIcon className="w-5 h-5" />
                                    </button>
                                  </div>
                                )}
                              </div>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p className="text-gray-500 text-center">No results found</p>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default UserManagement; 