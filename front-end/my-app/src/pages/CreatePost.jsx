import React, { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import ReactMarkdown from 'react-markdown';

const CreatePost = () => {
  const { id: subforumId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  
  const [formData, setFormData] = useState({
    title: '',
    body: '',
    tags: ''
  });
  const [error, setError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      const response = await fetch('/api/posts/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
          title: formData.title,
          content: formData.body,
          tags: formData.tags.split(',').map(tag => tag.trim()).filter(Boolean),
          subforum_id: subforumId
        })
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to create post');
      }

      const post = await response.json();
      navigate(`/post/${post.id}`);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!user) {
    navigate('/login');
    return null;
  }

  return (
    <div className="bg-gray-50 min-h-screen p-6">
      <main className="max-w-5xl mx-auto bg-white p-6 rounded-xl shadow space-y-6" aria-label="Post creation form">
        <h1 className="text-2xl font-bold text-gray-800">Create a New Post</h1>

        {error && (
          <div className="bg-red-50 text-red-600 p-4 rounded-md" role="alert">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Post title */}
          <div>
            <label htmlFor="title" className="block text-sm font-medium text-gray-700">
              Post Title <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              id="title"
              name="title"
              value={formData.title}
              onChange={handleChange}
              required
              aria-required="true"
              className="mt-1 block w-full border border-gray-300 rounded-md px-4 py-2"
              placeholder="e.g. How AI is changing everything..."
            />
          </div>

          {/* Markdown editor and preview */}
          <div>
            <label htmlFor="body" className="block text-sm font-medium text-gray-700 mb-1">
              Post Body (Markdown supported)
            </label>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4" aria-label="Markdown editor with preview">
              {/* Editor */}
              <textarea
                id="body"
                name="body"
                value={formData.body}
                onChange={handleChange}
                className="w-full h-48 border border-gray-300 rounded-md px-4 py-2 font-mono text-sm"
                placeholder="# Heading&#10;&#10;- Bullet&#10;- **Bold text**"
                aria-describedby="preview-desc"
              />

              {/* Live Markdown Preview */}
              <div
                className="w-full h-48 border border-gray-100 bg-gray-50 rounded-md px-4 py-2 overflow-y-auto prose prose-sm"
                role="region"
                aria-labelledby="preview-heading"
                tabIndex="0"
              >
                <h2 id="preview-heading" className="font-semibold text-lg mb-2">Preview</h2>
                <p id="preview-desc" className="sr-only">Live preview of your post's markdown content.</p>
                <ReactMarkdown>{formData.body || '*Preview will appear here*'}</ReactMarkdown>
              </div>
            </div>
          </div>

          {/* Tags */}
          <div>
            <label htmlFor="tags" className="block text-sm font-medium text-gray-700">
              Tags (optional)
            </label>
            <input
              type="text"
              id="tags"
              name="tags"
              value={formData.tags}
              onChange={handleChange}
              className="mt-1 block w-full border border-gray-300 rounded-md px-4 py-2"
              placeholder="e.g. AI, Research, JavaScript (comma separated)"
            />
          </div>

          {/* Submit button */}
          <div className="text-right">
            <button
              type="submit"
              className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 transition disabled:opacity-50"
              disabled={isSubmitting}
              aria-disabled={isSubmitting}
              aria-label="Submit your post"
            >
              {isSubmitting ? 'Submitting...' : 'Submit Post'}
            </button>
          </div>
        </form>
      </main>
    </div>
  );
};

export default CreatePost; 