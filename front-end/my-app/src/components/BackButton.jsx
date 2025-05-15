import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeftIcon } from '@heroicons/react/24/outline';

const BackButton = () => {
  const navigate = useNavigate();

  return (
    <button
      onClick={() => navigate(-1)}
      className="absolute left-6 flex items-center text-gray-600 hover:text-gray-900 transition-colors"
      aria-label="Go back"
    >
      <ArrowLeftIcon className="h-5 w-5" />
      <span className="ml-1">Back</span>
    </button>
  );
};

export default BackButton; 