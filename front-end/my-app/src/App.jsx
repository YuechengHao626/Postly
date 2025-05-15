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

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/create-subforum" element={<CreateSubForum />} />
          <Route path="/subforum/:id" element={<SubForum />} />
          <Route path="/subforums" element={<SubForumList />} />
          <Route path="/subforum/:id/create-post" element={<CreatePost />} />
          <Route path="/post/:id" element={<PostDetail />} />
          <Route path="/post/:id/edit" element={<EditPost />} />
          <Route path="/profile" element={<Profile />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
