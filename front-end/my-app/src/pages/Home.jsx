import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { UserCircleIcon } from "@heroicons/react/24/outline";

const Home = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const handleCreateCommunity = () => {
    if (!user) {
      navigate('/login');
    } else {
      navigate('/create-subforum');
    }
  };

  return (
    <>
      {/* Navbar */}
      <header className="border-b" role="banner">
        <nav
          className="flex items-center justify-between px-8 py-4"
          aria-label="Main navigation"
        >
          <Link to="/" className="text-xl font-bold">Postly</Link>
          <div className="flex items-center gap-4">
            <form role="search" aria-label="Search communities">
              <label htmlFor="search" className="sr-only">
                Search communities
              </label>
              <input
                type="text"
                id="search"
                placeholder="Search communities..."
                aria-label="Search communities"
                className="border border-gray-300 px-4 py-1.5 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm w-64"
              />
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

      {/* Hero Section */}
      <main
        className="flex flex-col items-center justify-center text-center mt-32 px-4"
        role="main"
      >
        <h2 className="sr-only">Welcome to Postly</h2>
        <p className="text-lg max-w-xl mb-8" id="hero-desc">
          Create or join communities to discuss your favorite topics with like-minded people
        </p>

        <div className="flex flex-col gap-4 w-64" aria-describedby="hero-desc">
          <button
            type="button"
            className="bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition"
            aria-label="Browse all available communities"
          >
            Browse All Communities
          </button>
          <button
            type="button"
            onClick={handleCreateCommunity}
            className="bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition"
            aria-label="Create a new community"
          >
            Create Now
          </button>
        </div>
      </main>
    </>
  );
};

export default Home;