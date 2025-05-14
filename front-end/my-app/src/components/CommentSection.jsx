import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';

const CommentSection = ({ postId }) => {
  const { user } = useAuth();
  const [comments, setComments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [newComment, setNewComment] = useState('');
  const [replyTo, setReplyTo] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    fetchComments();
  }, [postId]);

  const fetchComments = async () => {
    try {
      const response = await fetch(`/api/posts/${postId}/comments/`, {
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch comments');
      }

      const data = await response.json();
      setComments(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!newComment.trim()) return;

    setIsSubmitting(true);
    setError(null);

    try {
      const response = await fetch('/api/comments/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
          post_id: postId,
          content: newComment,
          reply_to_user_id: replyTo?.id
        })
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to post comment');
      }

      const comment = await response.json();
      setComments(prev => [...prev, comment]);
      setNewComment('');
      setReplyTo(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleReply = (comment) => {
    setReplyTo({
      id: comment.author_id,
      username: comment.author
    });
    document.getElementById('comment-input').focus();
  };

  const handleLike = async (commentId) => {
    if (!user) return;

    try {
      const response = await fetch('/api/votes/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
          target_type: 'comment',
          target_id: commentId
        })
      });

      if (!response.ok) {
        throw new Error('Failed to like comment');
      }

      // 更新评论的点赞状态
      await fetchComments();
    } catch (err) {
      setError(err.message);
    }
  };

  if (loading) {
    return <div className="text-center py-4">Loading comments...</div>;
  }

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-semibold">Comments ({comments.length})</h2>

      {error && (
        <div className="bg-red-50 text-red-600 p-4 rounded-md" role="alert">
          {error}
        </div>
      )}

      {/* Comment Form */}
      {user ? (
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="comment-input" className="sr-only">
              Add a comment
            </label>
            <div className="relative">
              <textarea
                id="comment-input"
                value={newComment}
                onChange={(e) => setNewComment(e.target.value)}
                className="w-full border border-gray-300 rounded-md px-4 py-2 focus:ring-2 focus:ring-blue-500"
                rows="3"
                placeholder={replyTo ? `Reply to @${replyTo.username}` : "Add a comment..."}
              />
              {replyTo && (
                <button
                  type="button"
                  onClick={() => setReplyTo(null)}
                  className="absolute top-2 right-2 text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              )}
            </div>
          </div>
          <div className="flex justify-end">
            <button
              type="submit"
              disabled={isSubmitting || !newComment.trim()}
              className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition disabled:opacity-50"
            >
              {isSubmitting ? 'Posting...' : 'Post Comment'}
            </button>
          </div>
        </form>
      ) : (
        <div className="text-center py-4 bg-gray-50 rounded-md">
          Please <a href="/login" className="text-blue-600 hover:underline">log in</a> to comment
        </div>
      )}

      {/* Comments List */}
      <div className="space-y-4">
        {comments.map(comment => (
          <div key={comment.id} className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex justify-between items-start">
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-medium text-gray-900">{comment.author}</span>
                  <span className="text-gray-500 text-sm">
                    {new Date(comment.created_at).toLocaleDateString()}
                  </span>
                </div>
                {comment.reply_to_user && (
                  <div className="text-sm text-gray-500 mt-1">
                    Replying to @{comment.reply_to_user}
                  </div>
                )}
                <p className="mt-2 text-gray-700">{comment.content}</p>
              </div>
            </div>
            <div className="mt-3 flex items-center gap-4">
              <button
                onClick={() => handleLike(comment.id)}
                className={`text-sm flex items-center gap-1 ${
                  comment.has_liked ? 'text-blue-600' : 'text-gray-500'
                } hover:text-blue-600`}
              >
                <span>👍</span>
                <span>{comment.likes_count || 0}</span>
              </button>
              {user && (
                <button
                  onClick={() => handleReply(comment)}
                  className="text-sm text-gray-500 hover:text-blue-600"
                >
                  Reply
                </button>
              )}
            </div>
          </div>
        ))}

        {comments.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            No comments yet. Be the first to comment!
          </div>
        )}
      </div>
    </div>
  );
};

export default CommentSection; 