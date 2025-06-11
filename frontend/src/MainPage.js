import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

function MainPage() {
  const navigate = useNavigate();
  const [ingredients, setIngredients] = useState('');
  const userId = localStorage.getItem('user_id');

  const handleLogout = () => {
    alert("로그아웃 되었습니다.");
    navigate('/login');
  };

  const handleRecommend = async () => {
    try {
      const res = await axios.post("http://localhost:5000/api/recommend", {
        user_id: userId,
        ingredients: ingredients.split(',').map(i => i.trim()),
      });

      navigate('/recommendations', { state: { recommendations: res.data } });
    } catch (err) {
      console.error("추천 실패:", err);
      alert("추천 중 오류가 발생했습니다.");
    }
  };

  const containerStyle = {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    padding: '40px',
    fontFamily: 'Arial, sans-serif',
    backgroundColor: '#f8f8f8',
    minHeight: '100vh',
  };

  const inputStyle = {
    width: '300px',
    padding: '10px',
    margin: '10px 0',
    borderRadius: '5px',
    border: '1px solid #ccc',
    fontSize: '14px',
  };

  const buttonStyle = {
    padding: '10px 20px',
    margin: '10px',
    backgroundColor: '#4CAF50',
    color: '#fff',
    border: 'none',
    borderRadius: '5px',
    cursor: 'pointer',
    fontSize: '14px',
  };

  return (
    <div style={containerStyle}>
      <h2>🍲 MyDish 메인 페이지</h2>
      <p>로그인에 성공하셨습니다! 냉장고 속 재료로 레시피를 추천받아보세요.</p>

      <input
        type="text"
        placeholder="냉장고 속 재료 (예: 계란, 우유, 당근)"
        value={ingredients}
        onChange={(e) => setIngredients(e.target.value)}
        style={inputStyle}
      />

      <div>
        <button onClick={handleRecommend} style={buttonStyle}>추천 받기</button>
        <button onClick={handleLogout} style={{ ...buttonStyle, backgroundColor: '#e74c3c' }}>로그아웃</button>
      </div>
    </div>
  );
}

export default MainPage;
