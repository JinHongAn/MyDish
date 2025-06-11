// Login.js
import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const handleLogin = async () => {
    try {
      const res = await axios.post('http://localhost:5000/api/login', {
        email,
        password,
      });

      if (res.status === 200) {
        console.log('로그인 성공', res.data);
        localStorage.setItem('token', res.data.token); // 필요한 경우
        navigate('/home'); // 로그인 성공 시 이동
      }
    } catch (err) {
      console.error(err);
      alert('로그인 실패');
    }
  };

  return (
    <div>
      <h2>로그인</h2>
      <input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="이메일" />
      <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="비밀번호" />
      <button onClick={handleLogin}>로그인</button>
    </div>
  );
}

export default Login;
