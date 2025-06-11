import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Signup from './Signup';
import Login from './Login';
import MainPage from './MainPage'; // 로그인 후 이동할 메인 페이지 (예시)
import RecommendationList from './RecommendationList';
import RecipeDetailPage from './RecipeDetailPage';
import Header from './Header';

function App() {
  return (
    <Router>
      <Header />
      <Routes>
        <Route path="/" element={<Navigate to="/login" />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/main" element={<MainPage />} />
        <Route path="/recommendations" element={<RecommendationList />} />
        <Route path="/recipe-detail" element={<RecipeDetailPage />} />
      </Routes>
    </Router>
  );
}

export default App;
