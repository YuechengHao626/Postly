import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import ReactMarkdown from 'react-markdown';
import BackButton from '../components/BackButton';

const AdminModal = ({ isOpen, onClose, admins, moderators }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold">Admin Team</h3>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700"
          >
            ✕
          </button>
        </div>
        
        <div className="space-y-4">
          {/* Sub-forum Admins */}
          <div>
            <h4 className="font-medium text-blue-600 mb-2">Sub-forum Admins</h4>
            {admins?.length > 0 ? (
              <ul className="space-y-2">
                {admins.map(admin => (
                  <li key={admin.id} className="flex items-center gap-2">
                    <span className="text-gray-900">{admin.username}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-gray-500 text-sm">No sub-forum admins</p>
            )}
          </div>

          {/* Moderators */}
          <div>
            <h4 className="font-medium text-green-600 mb-2">Moderators</h4>
            {moderators?.length > 0 ? (
              <ul className="space-y-2">
                {moderators.map(mod => (
                  <li key={mod.id} className="flex items-center gap-2">
                    <span className="text-gray-900">{mod.username}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-gray-500 text-sm">No moderators</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

const SubForum = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [subforum, setSubforum] = useState(null);
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [sortBy, setSortBy] = useState('recent');
  const [isAdminModalOpen, setIsAdminModalOpen] = useState(false);
  const [adminTeam, setAdminTeam] = useState({ admins: [], moderators: [] });

  useEffect(() => {
    fetchSubforumAndPosts();
  }, [id]);

  const fetchSubforumAndPosts = async () => {
    try {
      // 获取子论坛信息
      const subforumResponse = await fetch(`/api/subforums/${id}/`, {
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (!subforumResponse.ok) {
        throw new Error('Failed to fetch subforum');
      }

      const subforumData = await subforumResponse.json();
      setSubforum(subforumData);

      // 获取管理团队信息
      const adminTeamResponse = await fetch(`/api/subforums/${id}/admin-team/`, {
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (adminTeamResponse.ok) {
        const adminTeamData = await adminTeamResponse.json();
        setAdminTeam(adminTeamData);
      }

      // 获取帖子列表
      const postsResponse = await fetch(`/api/subforums/${id}/posts/`, {
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (!postsResponse.ok) {
        throw new Error('Failed to fetch posts');
      }

      const postsData = await postsResponse.json();
      setPosts(postsData);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this community?')) {
      return;
    }

    try {
      const response = await fetch(`/api/subforums/${id}/`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to delete subforum');
      }

      navigate('/');
    } catch (err) {
      setError(err.message);
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

  if (!subforum) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-600">Community not found</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <BackButton />
      <main className="max-w-5xl mx-auto space-y-8 mt-12" aria-label={`Sub-forum: ${subforum.name}`}>
        {/* Sub-forum Header */}
        <section className="bg-white p-6 rounded-xl shadow" aria-labelledby="forum-title">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <h1 id="forum-title" className="text-2xl font-bold">/{subforum.name}</h1>
              <p className="text-gray-600 mt-1">{subforum.description}</p>
              <p className="text-sm text-gray-500 mt-1">
                Created by <span className="font-semibold text-blue-600">{subforum.created_by}</span>
              </p>
              <p className="text-sm text-gray-500 mt-1" aria-label="Forum stats">
                📝 {posts.length} Posts
              </p>
            </div>
            <div className="flex gap-3">
              <button
                onClick={() => setIsAdminModalOpen(true)}
                className="bg-gray-100 text-gray-700 px-4 py-2 rounded-md text-sm hover:bg-gray-200 transition-colors"
                aria-label="View admin team"
              >
                👥 Admin Team
              </button>
              {user && (subforum.created_by === user.username || user.role === 'super_admin') && (
                <>
                  <Link
                    to={`/subforum/${id}/edit`}
                    className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm hover:bg-blue-700 transition-colors"
                    aria-label="Edit community"
                  >
                    ✏️ Edit
                  </Link>
                  <button
                    onClick={handleDelete}
                    className="bg-red-600 text-white px-4 py-2 rounded-md text-sm hover:bg-red-700 transition-colors"
                    aria-label="Delete community"
                  >
                    🗑️ Delete
                  </button>
                </>
              )}
            </div>
          </div>
        </section>

        {/* Admin Modal */}
        <AdminModal
          isOpen={isAdminModalOpen}
          onClose={() => setIsAdminModalOpen(false)}
          admins={adminTeam.admins}
          moderators={adminTeam.moderators}
        />

        {/* Actions: Sort + Create Post */}
        <section className="flex flex-col md:flex-row md:items-center md:justify-between gap-4" aria-label="Post actions">
          <div className="flex items-center gap-2 text-sm">
            <label htmlFor="sort" className="text-gray-600 font-medium">Sort by:</label>
            <select
              id="sort"
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="border border-gray-300 rounded px-3 py-1"
            >
              <option value="recent">Most Recent</option>
              <option value="comments">Most Commented</option>
            </select>
          </div>
          {user && (
            <Link
              to={`/subforum/${id}/create-post`}
              className="bg-blue-600 text-white px-5 py-2 rounded-md hover:bg-blue-700 text-sm"
              aria-label="Create a new post in this forum"
            >
              + Create Post
            </Link>
          )}
        </section>

        {/* Post List */}
        <section className="space-y-4" aria-labelledby="post-list-heading">
          <h2 id="post-list-heading" className="sr-only">Post List</h2>

          {posts.map(post => (
            <article
              key={post.id}
              className="bg-white p-6 rounded-xl shadow hover:shadow-md transition"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <Link
                    to={`/post/${post.id}`}
                    className="block group"
                  >
                    <h3 className="text-xl font-semibold text-gray-900 group-hover:text-blue-600">
                      {post.title}
                    </h3>
                    <div className="mt-2 text-gray-600 line-clamp-2 prose prose-sm">
                      {post.format === 'markdown' ? (
                        <ReactMarkdown>{post.content}</ReactMarkdown>
                      ) : (
                        post.content
                      )}
                    </div>
                  </Link>
                  <div className="mt-4 flex items-center gap-4 text-sm text-gray-500">
                    <span>Posted by {post.author}</span>
                    <span>•</span>
                    <span>{new Date(post.created_at).toLocaleDateString()}</span>
                    <div className="flex items-center gap-4">
                      <span className="flex items-center gap-1 text-gray-500">
                        <span>👍</span>
                        <span>0</span>
                      </span>
                      <Link
                        to={`/post/${post.id}`}
                        className="flex items-center gap-1 text-gray-500 hover:text-blue-600"
                      >
                        <span>💬</span>
                        <span>{post.comment_count}</span>
                      </Link>
                    </div>
                  </div>
                  {post.tags && post.tags.length > 0 && (
                    <div className="mt-3 flex flex-wrap gap-2">
                      {post.tags.map(tag => (
                        <span
                          key={tag}
                          className="px-2 py-0.5 bg-gray-100 text-gray-600 text-xs rounded-full"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </article>
          ))}

          {posts.length === 0 && (
            <div className="text-center py-12 bg-white rounded-xl shadow">
              <p className="text-gray-600">No posts yet.</p>
              {user && (
                <Link
                  to={`/subforum/${id}/create-post`}
                  className="text-blue-600 hover:text-blue-700 mt-2 inline-block"
                >
                  Create the first post
                </Link>
              )}
            </div>
          )}
        </section>
      </main>
    </div>
  );
};

export default SubForum; 