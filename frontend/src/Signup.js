import React, { useState } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom'; // 로그인 링크용

function Signup() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [allergy, setAllergy] = useState('');
  const [height, setHeight] = useState('');
  const [weight, setWeight] = useState('');
  const [goal, setGoal] = useState('maintain');

  const handleSignup = async () => {
    try {
      const res = await axios.post('http://localhost:5000/api/signup', {
        username,
        password,
        allergy,
        height_cm: parseFloat(height),
        weight_kg: parseFloat(weight),
        goal
      });
      alert(`회원가입 성공! ID: ${res.data.user_id}`);
    } catch (err) {
      alert(err.response?.data?.message || '회원가입 실패');
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
    gap: '10px'
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
  };

  return (
    <div style={containerStyle}>
      <div style={formStyle}>
        <h2 style={{ textAlign: 'center' }}>회원가입</h2>
        <input style={inputStyle} placeholder="이름" onChange={e => setUsername(e.target.value)} />
        <input style={inputStyle} placeholder="비밀번호" type="password" onChange={e => setPassword(e.target.value)} />
        <input style={inputStyle} placeholder="알러지 (쉼표로)" onChange={e => setAllergy(e.target.value)} />
        <input style={inputStyle} placeholder="키 (cm)" type="number" onChange={e => setHeight(e.target.value)} />
        <input style={inputStyle} placeholder="몸무게 (kg)" type="number" onChange={e => setWeight(e.target.value)} />
        <select style={inputStyle} onChange={e => setGoal(e.target.value)} value={goal}>
          <option value="maintain">체중 유지</option>
          <option value="loss">감량</option>
          <option value="gain">증량</option>
        </select>
        <button style={buttonStyle} onClick={handleSignup}>가입하기</button>
        <Link to="/login" style={linkStyle}>이미 계정이 있으신가요? 로그인하기 →</Link>
      </div>
    </div>
  );
}

export default Signup;
