import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import CommentSection from '../components/CommentSection';
import ReactMarkdown from 'react-markdown';

const PostDetail = () => {
  const { id } = useParams();
  const { user } = useAuth();
  const [post, setPost] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchPost();
  }, [id]);

  const fetchPost = async () => {
    try {
      const response = await fetch(`/api/posts/${id}/`, {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': user ? `Bearer ${localStorage.getItem('access_token')}` : ''
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch post');
      }

      const data = await response.json();
      setPost(data);
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

  if (!post) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-600">Post not found</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <main className="max-w-4xl mx-auto space-y-6">
        {/* Post Content */}
        <article className="bg-white p-6 rounded-xl shadow">
          <header className="mb-4">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold text-gray-900">{post.title}</h1>
                <div className="mt-2 flex items-center gap-4 text-sm text-gray-500">
                  <span>Posted by {post.author}</span>
                  <span>•</span>
                  <span>{new Date(post.created_at).toLocaleDateString()}</span>
                  <span>•</span>
                  <Link
                    to={`/subforum/${post.sub_forum.id}`}
                    className="text-blue-600 hover:underline"
                  >
                    /{post.sub_forum.name}
                  </Link>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className="flex items-center gap-1 px-3 py-1 rounded-full bg-gray-100 text-gray-600">
                  <span>👍</span>
                  <span>0</span>
                </span>
              </div>
            </div>
          </header>

          <div className="prose max-w-none">
            {post.format === 'markdown' ? (
              <ReactMarkdown>{post.content}</ReactMarkdown>
            ) : (
              post.content
            )}
          </div>

          {post.tags && post.tags.length > 0 && (
            <div className="mt-6 flex flex-wrap gap-2">
              {post.tags.map(tag => (
                <span
                  key={tag}
                  className="px-2 py-1 bg-gray-100 text-gray-600 text-sm rounded-full"
                >
                  {tag}
                </span>
              ))}
            </div>
          )}
        </article>

        {/* Comments Section */}
        <section className="bg-white p-6 rounded-xl shadow">
          <CommentSection postId={id} />
        </section>
      </main>
    </div>
  );
};

export default PostDetail; 