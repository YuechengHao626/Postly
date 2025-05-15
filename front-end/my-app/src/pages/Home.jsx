import React from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const Home = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  const handleCreateCommunity = () => {
    if (!user) {
      navigate('/login');
    } else {
      navigate('/create-subforum');
    }
  };

  const handleBrowseAll = () => {
    navigate('/subforums');
  };

  return (
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
          onClick={handleBrowseAll}
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
  );
};

export default Home;