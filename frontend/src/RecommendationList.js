import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

function RecommendationList() {
  const { state } = useLocation();
  const navigate = useNavigate();
  const recommendations = (state && state.recommendations) || [];

  const handleClick = (recipe) => {
    navigate('/recipe-detail', { state: { recipe } });
  };

  return (
    <div style={styles.container}>
      <div style={styles.box}>
        <h2 style={styles.title}>🍳 추천 레시피 목록</h2>
        {recommendations.length === 0 ? (
          <p style={styles.text}>추천 결과가 없습니다.</p>
        ) : (
          <ul style={styles.list}>
            {recommendations.map((rec, idx) => (
              <li
                key={idx}
                onClick={() => handleClick(rec)}
                style={styles.item}
              >
                <strong>{rec.recipe_name}</strong> (점수: {rec.score})<br />
                <span>부족한 재료: {rec.missing_ingredients}</span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

const styles = {
  container: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'flex-start',
    minHeight: '100vh',
    backgroundColor: '#f8f8f8',
    paddingTop: '60px',
  },
  box: {
    backgroundColor: '#ffffff',
    padding: '30px',
    borderRadius: '8px',
    boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
    width: '90%',
    maxWidth: '600px',
  },
  title: {
    textAlign: 'center',
    fontSize: '24px',
    marginBottom: '20px',
  },
  text: {
    textAlign: 'center',
    color: '#666',
  },
  list: {
    listStyle: 'none',
    padding: 0,
  },
  item: {
    padding: '12px',
    marginBottom: '12px',
    border: '1px solid #e0e0e0',
    borderRadius: '6px',
    cursor: 'pointer',
    backgroundColor: '#fafafa',
  },
};

export default RecommendationList;
