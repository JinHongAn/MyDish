import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import axios from 'axios';

function RecipeDetailPage() {
  const { state } = useLocation();
  const navigate = useNavigate();
  const recipe = state?.recipe;
  const userId = localStorage.getItem('user_id');

  if (!recipe) {
    return (
      <div style={styles.container}>
        <div style={styles.box}>
          <p style={styles.error}>레시피 정보를 불러올 수 없습니다.</p>
          <button style={styles.button} onClick={() => navigate(-1)}>뒤로가기</button>
        </div>
      </div>
    );
  }

  const steps = [];
  for (let i = 1; i <= 6; i++) {
    const step = recipe[`MANUAL0${i}`];
    if (step) steps.push(step);
  }

  const handleLike = async () => {
    try {
      await axios.post('http://localhost:5000/api/feedback', {
        user_id: userId,
        recipe_id: recipe.recipe_id,
        liked: true,
      });
      alert('레시피를 즐겨찾기에 추가했습니다!');
    } catch (err) {
      alert('즐겨찾기 추가에 실패했습니다.');
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.box}>
        <h2 style={styles.title}>🍽️ {recipe.recipe_name}</h2>
        <p><strong>전체 재료:</strong> {recipe.ingredients}</p>
        <p><strong>부족한 재료:</strong> {recipe.missing_ingredients}</p>
        <p><strong>추천 점수:</strong> {recipe.score}</p>

        <div style={styles.instructions}>
          <h3>조리 방법</h3>
          {steps.length > 0 ? (
            <ol>
              {steps.map((step, idx) => (
                <ul key={idx} style={styles.step}>{step}</ul>
              ))}
            </ol>
          ) : (
            <p style={{ color: '#888' }}>조리 방법 정보가 없습니다.</p>
          )}
        </div>

        <div style={styles.nutrition}>
          <h3>영양 성분 (1인분 기준)</h3>
          <ul style={styles.nutritionList}>
            <li>나트륨: {recipe.INFO_NA || 0} mg</li>
            <li>단백질: {recipe.INFO_PRO || 0} g</li>
            <li>지방: {recipe.INFO_FAT || 0} g</li>
            <li>탄수화물: {recipe.INFO_CAR || 0} g</li>
            <li>칼로리: {recipe.INFO_ENG || 0} kcal</li>
          </ul>
        </div>

        <div style={{ display: 'flex', gap: '10px' }}>
          <button style={styles.button} onClick={handleLike}>❤️ 즐겨찾기</button>
          <button style={styles.button} onClick={() => navigate(-1)}>목록으로 돌아가기</button>
        </div>
      </div>
    </div>
  );
}

const styles = {
  container: {
    minHeight: '100vh',
    backgroundColor: '#f8f8f8',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'flex-start',
    paddingTop: '60px',
  },
  box: {
    backgroundColor: '#fff',
    padding: '30px',
    borderRadius: '10px',
    width: '90%',
    maxWidth: '600px',
    boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
  },
  title: {
    fontSize: '24px',
    marginBottom: '16px',
    textAlign: 'center',
  },
  instructions: {
    marginTop: '20px',
  },
  step: {
    marginBottom: '10px',
    lineHeight: 1.6,
  },
  button: {
    marginTop: '20px',
    padding: '10px 20px',
    backgroundColor: '#4CAF50',
    border: 'none',
    color: 'white',
    borderRadius: '6px',
    cursor: 'pointer',
  },
  error: {
    color: 'red',
    textAlign: 'center',
  },
  nutrition: {
    marginTop: '30px',
    padding: '15px',
    border: '1px solid #ddd',
    borderRadius: '8px',
    backgroundColor: '#f9f9f9',
  },
  nutritionList: {
    listStyleType: 'none',
    paddingLeft: 0,
    lineHeight: 1.8,
  }
};

export default RecipeDetailPage;
