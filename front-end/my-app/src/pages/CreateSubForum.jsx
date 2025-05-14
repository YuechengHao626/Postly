import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const CreateSubForum = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    rules: '',
    tags: ''
  });

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    try {
      const response = await fetch('/api/subforums/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
          name: formData.name,
          description: formData.description,
          rules: formData.rules || null
        })
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || 'Failed to create sub-forum');
      }

      // 创建成功后跳转到新创建的子论坛
      const newSubForum = await response.json();
      navigate(`/subforum/${newSubForum.id}`);
    } catch (err) {
      setError(err.message);
    }
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-xl font-semibold text-gray-900">Please log in to create a sub-forum</h2>
          <button
            onClick={() => navigate('/login')}
            className="mt-4 bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 transition"
          >
            Log In
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <main className="max-w-2xl mx-auto bg-white p-6 rounded-xl shadow space-y-6" aria-label="Sub-forum creation">
        {/* Title */}
        <div className="border-b pb-4">
          <h2 id="form-title" className="text-2xl font-bold text-gray-900">Create a New Community</h2>
          <p className="mt-2 text-sm text-gray-600">
            Create a unique space for people to discuss and share content about your topic of interest.
          </p>
        </div>

        <form className="space-y-6" onSubmit={handleSubmit} aria-describedby="form-help">
          <p id="form-help" className="sr-only">
            Use this form to create a new community. Fields marked with asterisk are required.
          </p>

          {error && (
            <div className="bg-red-50 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
              <span className="block sm:inline">{error}</span>
            </div>
          )}

          {/* Name */}
          <div>
            <label htmlFor="name" className="block text-sm font-medium text-gray-700">
              Community Name <span className="text-red-500">*</span>
            </label>
            <div className="flex items-center mt-1">
              <span className="bg-gray-100 px-3 py-2 rounded-l-md text-gray-600 border border-r-0 border-gray-300">
                /
              </span>
              <input
                type="text"
                id="name"
                name="name"
                value={formData.name}
                onChange={handleChange}
                required
                placeholder="communityname"
                aria-required="true"
                className="flex-1 px-4 py-2 border border-gray-300 rounded-r-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              />
            </div>
            <p className="mt-1 text-sm text-gray-500">
              Community names cannot be changed once created.
            </p>
          </div>

          {/* Description */}
          <div>
            <label htmlFor="description" className="block text-sm font-medium text-gray-700">
              Description <span className="text-red-500">*</span>
            </label>
            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleChange}
              rows="3"
              required
              aria-required="true"
              className="mt-1 w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              placeholder="Briefly describe what this community is about"
            />
          </div>

          {/* Rules */}
          <div>
            <label htmlFor="rules" className="block text-sm font-medium text-gray-700">
              Community Rules
            </label>
            <textarea
              id="rules"
              name="rules"
              value={formData.rules}
              onChange={handleChange}
              rows="4"
              className="mt-1 w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              placeholder="Add community guidelines (supports markdown)"
            />
            <p className="mt-1 text-sm text-gray-500">
              Clear guidelines help maintain a healthy community.
            </p>
          </div>

          {/* Submit */}
          <div className="flex items-center justify-end gap-4 pt-4 border-t">
            <button
              type="button"
              onClick={() => navigate(-1)}
              className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 transition focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
              aria-label="Submit form to create new community"
            >
              Create Community
            </button>
          </div>
        </form>
      </main>
    </div>
  );
};

export default CreateSubForum; 