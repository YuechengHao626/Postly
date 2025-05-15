import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import BackButton from '../components/BackButton';

const Profile = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [posts, setPosts] = useState([]);
  const [comments, setComments] = useState([]);
  const [userDetail, setUserDetail] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!user) {
      navigate('/login');
      return;
    }
    fetchUserContent();
  }, [user, navigate]);

  const fetchUserContent = async () => {
    try {
      // 获取用户详情
      const userDetailResponse = await fetch('/api/user/detail/', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      // 获取用户的帖子
      const postsResponse = await fetch('/api/posts/?author=' + user.username, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      // 获取用户的评论
      const commentsResponse = await fetch('/api/comments/?author=' + user.username, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      if (!userDetailResponse.ok || !postsResponse.ok || !commentsResponse.ok) {
        throw new Error('Failed to fetch user content');
      }

      const userDetailData = await userDetailResponse.json();
      const postsData = await postsResponse.json();
      const commentsData = await commentsResponse.json();

      setUserDetail(userDetailData);
      setPosts(postsData);
      setComments(commentsData);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDeletePost = async (postId) => {
    if (!window.confirm('Are you sure you want to delete this post?')) {
      return;
    }

    try {
      const response = await fetch(`/api/posts/${postId}/`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to delete post');
      }

      // 重新获取帖子列表
      fetchUserContent();
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

  return (
    <div className="bg-gray-50 min-h-screen p-6 text-gray-800">
      <BackButton />
      <main className="max-w-5xl mx-auto space-y-8 mt-12" aria-label={`User Dashboard for ${user.username}`}>
        {/* Profile Header */}
        <section className="bg-white p-6 rounded-xl shadow" aria-labelledby="profile-heading">
          <h2 id="profile-heading" className="text-2xl font-bold mb-4">Profile</h2>
          <div className="flex flex-col md:flex-row gap-6 items-center md:items-start">
            <img src={`https://api.dicebear.com/7.x/initials/svg?seed=${user.username}`} alt="User avatar" className="rounded-full w-20 h-20" />
            <div className="flex-1 space-y-2 text-center md:text-left">
              <h3 className="text-xl font-semibold">u/{userDetail?.username}</h3>
              <p className="text-sm text-gray-600">Email: {userDetail?.email}</p>
              <p className="text-sm text-gray-600">Joined: {new Date(userDetail?.created_at).toLocaleString('en-AU', { timeZone: 'Australia/Brisbane' })}</p>
              <p className="text-sm text-gray-600">📝 {posts.length} Posts • 💬 {comments.length} Comments</p>
            </div>
            <div className="flex flex-col gap-2 md:flex-row md:items-center md:gap-3">
              <Link
                to="/permissions"
                className="text-sm bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition"
                aria-label="Go to Role and Permissions Matrix"
              >
                Permissions Matrix
              </Link>
            </div>
          </div>
        </section>

        {/* My Posts */}
        <section className="bg-white p-6 rounded-xl shadow space-y-4" aria-labelledby="myposts-heading">
          <h3 id="myposts-heading" className="text-lg font-semibold text-gray-800">My Posts</h3>
          {posts.length > 0 ? (
            <ul role="list" className="space-y-4">
              {posts.map(post => (
                <li key={post.id} role="listitem" className="border rounded-md p-4 hover:shadow focus-within:ring-2 focus-within:ring-blue-500">
                  <div className="flex justify-between">
                    <div>
                      <Link to={`/post/${post.id}`}>
                        <h4 className="text-md font-medium text-gray-800 hover:text-blue-600">{post.title}</h4>
                      </Link>
                      <p className="text-sm text-gray-500">
                        Posted in /{post.sub_forum.name} • {new Date(post.created_at).toLocaleString('en-AU', { timeZone: 'Australia/Brisbane' })} • 💬 {post.comment_count || 0} comments
                      </p>
                    </div>
                    <div className="text-sm space-x-2">
                      <Link
                        to={`/post/${post.id}/edit`}
                        className="text-blue-600 hover:underline"
                        aria-label={`Edit post: ${post.title}`}
                      >
                        Edit
                      </Link>
                      <button
                        onClick={() => handleDeletePost(post.id)}
                        className="text-red-600 hover:underline"
                        aria-label={`Delete post: ${post.title}`}
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-gray-500 text-center py-4">No posts yet</p>
          )}
        </section>

        {/* My Comments */}
        <section className="bg-white p-6 rounded-xl shadow space-y-4" aria-labelledby="mycomments-heading">
          <h3 id="mycomments-heading" className="text-lg font-semibold text-gray-800">My Comments</h3>
          {comments.length > 0 ? (
            <ul role="list" className="divide-y">
              {comments.map(comment => (
                <li key={comment.id} className="py-4" role="listitem">
                  <p className="text-sm text-gray-700">{comment.content}</p>
                  <p className="text-xs text-gray-500 mt-1">
                    {comment.reply_to_user && `Reply @${comment.reply_to_user}: `}
                    On: "{comment.post.title}" in /{comment.post.sub_forum.name} • {new Date(comment.created_at).toLocaleString('en-AU', { timeZone: 'Australia/Brisbane' })}
                  </p>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-gray-500 text-center py-4">No comments yet</p>
          )}
        </section>
      </main>
    </div>
  );
};

export default Profile; 