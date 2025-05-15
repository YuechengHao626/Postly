import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import CommentSection from '../components/CommentSection';
import ReactMarkdown from 'react-markdown';
import BackButton from '../components/BackButton';

const PostDetail = () => {
  const { id } = useParams();
  const { user, updateUserInfo } = useAuth();
  const navigate = useNavigate();
  const [post, setPost] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [toast, setToast] = useState(null);

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      // 确保用户信息是最新的
      try {
        await updateUserInfo();
      } catch (err) {
        console.error('Error updating user info:', err);
      }
      await fetchPost();
      setLoading(false);
    };

    if (user) {
      loadData();
    }
  }, [id, user?.username]); // 只在 id 和 username 变化时重新加载

  const fetchPost = async () => {
    if (!user) return;
    
    try {
      console.log('Current user info:', {
        username: user.username,
        role: user.role,
        token: localStorage.getItem('access_token')
      });
      
      const response = await fetch(`/api/posts/${id}/`, {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch post');
      }

      const data = await response.json();
      console.log('Received post data:', {
        id: data.id,
        title: data.title,
        author: data.author,
        subForum: data.sub_forum,
        isModerator: data.sub_forum.is_moderator
      });
      setPost(data);
    } catch (err) {
      console.error('Error fetching post:', err);
      setError(err.message);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this post?')) {
      return;
    }

    try {
      const response = await fetch(`/api/posts/${id}/`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to delete post');
      }

      navigate(`/subforum/${post.sub_forum.id}`);
    } catch (err) {
      setToast({
        type: 'error',
        message: err.message
      });
    }
  };

  // 检查用户是否有权限编辑/删除帖子
  const canModifyPost = () => {
    if (!user || !post) {
      console.log('No user or post data available');
      return false;
    }
    
    console.log('Checking post permissions:', {
      user: {
        username: user.username,
        role: user.role
      },
      post: {
        id: post.id,
        author: post.author,
        subForum: {
          id: post.sub_forum.id,
          name: post.sub_forum.name,
          isModerator: post.sub_forum.is_moderator
        }
      }
    });
    
    // 作者可以修改
    if (post.author === user.username) {
      console.log('User is post author');
      return true;
    }
    
    // 超级管理员可以修改任何帖子
    if (user.role === 'super_admin') {
      console.log('User is super admin');
      return true;
    }
    
    // 子论坛管理员和版主可以修改其管理的子论坛中的帖子
    const hasModeratorRole = user.role === 'subforum_admin' || user.role === 'moderator';
    const hasModeratorPermission = post.sub_forum.is_moderator;
    
    console.log('Moderator check:', {
      hasModeratorRole,
      hasModeratorPermission,
      userRole: user.role,
      isModerator: post.sub_forum.is_moderator
    });

    if (hasModeratorRole && hasModeratorPermission) {
      console.log('User is moderator/admin and has permission');
      return true;
    }
    
    console.log('User does not have permission');
    return false;
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
      {toast && (
        <div className={`fixed top-4 right-4 px-4 py-2 rounded-md ${
          toast.type === 'error' ? 'bg-red-500' : 'bg-green-500'
        } text-white`}>
          {toast.message}
        </div>
      )}
      <BackButton />
      <main className="max-w-4xl mx-auto space-y-6 mt-12">
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
              {canModifyPost() && (
                <div className="flex items-center gap-2">
                  <Link
                    to={`/post/${post.id}/edit`}
                    className="text-sm px-3 py-1 bg-blue-100 text-blue-600 rounded-md hover:bg-blue-200 transition"
                  >
                    Edit
                  </Link>
                  <button
                    onClick={handleDelete}
                    className="text-sm px-3 py-1 bg-red-100 text-red-600 rounded-md hover:bg-red-200 transition"
                  >
                    Delete
                  </button>
                </div>
              )}
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