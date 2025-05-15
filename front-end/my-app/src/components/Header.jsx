import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { UserCircleIcon, MagnifyingGlassIcon } from "@heroicons/react/24/outline";

const SearchResult = ({ result, type }) => {
  if (type === 'post') {
    return (
      <Link
        to={`/post/${result.id}`}
        className="block p-4 hover:bg-gray-50 border-b last:border-b-0"
      >
        <h3 className="font-medium text-gray-900">{result.title}</h3>
        <p className="text-sm text-gray-500 mt-1 line-clamp-2">{result.content}</p>
        <div className="text-xs text-gray-500 mt-1">
          Posted by {result.author} in /{result.sub_forum_name}
        </div>
      </Link>
    );
  } else if (type === 'subforum') {
    return (
      <Link
        to={`/subforum/${result.id}`}
        className="block p-4 hover:bg-gray-50 border-b last:border-b-0"
      >
        <h3 className="font-medium text-gray-900">/{result.name}</h3>
        <p className="text-sm text-gray-500 mt-1 line-clamp-2">{result.description}</p>
        <div className="text-xs text-gray-500 mt-1">
          Created by {result.created_by} • {result.post_count} posts
        </div>
      </Link>
    );
  }
  return null;
};

const Header = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState("");
  const [searchType, setSearchType] = useState("posts");
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const endpoint = searchType === 'posts' 
        ? '/api/search/posts/'
        : '/api/search/subforums/';

      const response = await fetch(`${endpoint}?q=${encodeURIComponent(searchQuery)}`);
      
      if (!response.ok) {
        throw new Error('Search failed');
      }

      const data = await response.json();
      setSearchResults(data.results || []);
    } catch (err) {
      setError('Failed to perform search');
      console.error('Search error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <header className="border-b" role="banner">
      <nav
        className="flex items-center justify-between px-8 py-4"
        aria-label="Main navigation"
      >
        <Link to="/" className="text-xl font-bold">Postly</Link>
        <div className="flex items-center gap-4">
          <form 
            role="search" 
            aria-label="Search communities and posts"
            onSubmit={handleSearch}
            className="relative"
          >
            <div className="flex items-center gap-2">
              <select
                value={searchType}
                onChange={(e) => setSearchType(e.target.value)}
                className="border border-gray-300 rounded-l-full px-4 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="posts">Posts</option>
                <option value="subforums">Communities</option>
              </select>
              <div className="relative flex-1">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder={`Search ${searchType}...`}
                  className="border border-gray-300 px-4 py-1.5 rounded-r-full focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm w-64"
                />
                <button
                  type="submit"
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  disabled={loading}
                >
                  <MagnifyingGlassIcon className="h-5 w-5" />
                </button>
              </div>
            </div>

            {/* Search Results Dropdown */}
            {searchResults.length > 0 && (
              <div className="absolute top-full left-0 right-0 mt-1 bg-white rounded-lg shadow-lg border border-gray-200 max-h-96 overflow-y-auto z-50">
                {searchResults.map((result) => (
                  <SearchResult
                    key={result.id}
                    result={result}
                    type={searchType === 'posts' ? 'post' : 'subforum'}
                  />
                ))}
              </div>
            )}

            {/* Loading State */}
            {loading && (
              <div className="absolute top-full left-0 right-0 mt-1 bg-white rounded-lg shadow-lg border border-gray-200 p-4 text-center text-gray-500">
                Searching...
              </div>
            )}

            {/* Error State */}
            {error && (
              <div className="absolute top-full left-0 right-0 mt-1 bg-white rounded-lg shadow-lg border border-red-200 p-4 text-center text-red-500">
                {error}
              </div>
            )}
          </form>
          
          {user ? (
            <div className="flex items-center gap-4">
              <Link
                to="/profile"
                className="flex items-center gap-2 text-gray-700 hover:text-gray-900 transition"
              >
                <UserCircleIcon className="h-6 w-6" />
                <span>{user.username}</span>
              </Link>
              <button
                onClick={handleLogout}
                className="border border-gray-500 text-gray-800 px-4 py-1.5 rounded-full hover:bg-gray-100 transition"
              >
                Log Out
              </button>
            </div>
          ) : (
            <>
              <Link
                to="/login"
                className="border border-gray-500 text-gray-800 px-4 py-1.5 rounded-full hover:bg-gray-100 transition"
              >
                Log In
              </Link>
              <Link
                to="/signup"
                className="bg-blue-600 text-white px-4 py-1.5 rounded-full hover:bg-blue-700 transition"
              >
                Sign Up
              </Link>
            </>
          )}
        </div>
      </nav>
    </header>
  );
};

export default Header; 