import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import BackButton from '../components/BackButton';

const SubForumList = () => {
  const [subforums, setSubforums] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { user } = useAuth();

  useEffect(() => {
    fetchSubforums();
  }, []);

  const fetchSubforums = async () => {
    try {
      const response = await fetch('/api/subforums/', {
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch subforums');
      }

      const data = await response.json();
      setSubforums(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-600">Loading...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-red-600">Error: {error}</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <BackButton />
      <main className="max-w-5xl mx-auto space-y-8 mt-12">
        {/* Header */}
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">Communities</h1>
          {user && (
            <Link
              to="/create-subforum"
              className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition text-sm"
            >
              Create Community
            </Link>
          )}
        </div>

        {/* Subforum List */}
        <div className="space-y-4">
          {subforums.map(subforum => (
            <Link
              key={subforum.id}
              to={`/subforum/${subforum.id}`}
              className="block bg-white p-6 rounded-xl shadow hover:shadow-md transition"
            >
              <div className="flex justify-between items-start">
                <div>
                  <h2 className="text-xl font-semibold text-gray-900">
                    /{subforum.name}
                  </h2>
                  <p className="text-gray-600 mt-1">
                    {subforum.description}
                  </p>
                  <div className="flex items-center gap-4 mt-2 text-sm text-gray-500">
                    <span>Created by {subforum.created_by}</span>
                    <span>•</span>
                    <span>
                      {new Date(subforum.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              </div>
            </Link>
          ))}

          {subforums.length === 0 && (
            <div className="text-center py-12 bg-white rounded-xl shadow">
              <p className="text-gray-600">No communities found.</p>
              {user && (
                <Link
                  to="/create-subforum"
                  className="text-blue-600 hover:text-blue-700 mt-2 inline-block"
                >
                  Create the first community
                </Link>
              )}
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default SubForumList; 