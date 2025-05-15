import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import Home from "./pages/Home";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import CreateSubForum from "./pages/CreateSubForum";
import SubForum from './pages/SubForum';
import SubForumList from './pages/SubForumList';
import CreatePost from './pages/CreatePost';
import PostDetail from './pages/PostDetail';
import Profile from './pages/Profile';
import EditPost from './pages/EditPost';
import Permissions from './pages/Permissions';
import UserManagement from './pages/UserManagement';
import Header from './components/Header';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="min-h-screen bg-gray-50">
          <Routes>
            <Route path="/" element={<><Header /><Home /></>} />
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />
            <Route path="/create-subforum" element={<><Header /><CreateSubForum /></>} />
            <Route path="/subforum/:id" element={<><Header /><SubForum /></>} />
            <Route path="/subforums" element={<><Header /><SubForumList /></>} />
            <Route path="/subforum/:id/create-post" element={<><Header /><CreatePost /></>} />
            <Route path="/post/:id" element={<><Header /><PostDetail /></>} />
            <Route path="/post/:id/edit" element={<><Header /><EditPost /></>} />
            <Route path="/profile" element={<><Header /><Profile /></>} />
            <Route path="/permissions" element={<><Header /><Permissions /></>} />
            <Route path="/user-management" element={<UserManagement />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
