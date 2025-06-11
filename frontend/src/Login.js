import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate, Link } from 'react-router-dom';

function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const handleLogin = async () => {
    try {
      const response = await axios.post('http://localhost:5000/api/login', {
        username: username,
        password: password,
      });

      if (response.status === 200) {
        alert('로그인 성공');
        localStorage.setItem('user_id', response.data.user_id);
        navigate('/main'); // 성공 시 메인 페이지로 이동
      }
    } catch (error) {
      alert('로그인 실패');
    }
  };

  const containerStyle = {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    height: '100vh',
    fontFamily: 'Arial, sans-serif',
    backgroundColor: '#f5f5f5',
  };

  const formStyle = {
    display: 'flex',
    flexDirection: 'column',
    padding: '30px',
    borderRadius: '10px',
    backgroundColor: 'white',
    boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
    minWidth: '300px',
    gap: '10px',
  };

  const inputStyle = {
    padding: '10px',
    fontSize: '14px',
    border: '1px solid #ccc',
    borderRadius: '5px',
  };

  const buttonStyle = {
    padding: '10px',
    fontSize: '16px',
    backgroundColor: '#4CAF50',
    color: 'white',
    border: 'none',
    borderRadius: '5px',
    cursor: 'pointer',
    marginTop: '10px',
  };

  const linkStyle = {
    marginTop: '15px',
    fontSize: '14px',
    textDecoration: 'none',
    color: '#007bff',
    textAlign: 'center',
  };

  return (
    <div style={containerStyle}>
      <div style={formStyle}>
        <h2 style={{ textAlign: 'center' }}>로그인</h2>
        <input
          type="text"
          placeholder="이름"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          style={inputStyle}
        />
        <input
          type="password"
          placeholder="비밀번호"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          style={inputStyle}
        />
        <button onClick={handleLogin} style={buttonStyle}>로그인</button>
        <Link to="/signup" style={linkStyle}>계정이 없으신가요? 회원가입 →</Link>
      </div>
    </div>
  );
}

export default Login;
