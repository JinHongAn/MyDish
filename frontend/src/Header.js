// src/Header.js
import React from 'react';

const Header = () => {
  return (
    <header style={styles.header}>
      <h1 style={styles.title}>🍽️ MyDish</h1>
    </header>
  );
};

const styles = {
  header: {
    width: '100%',
    textAlign: 'center',
    padding: '20px 0',
    backgroundColor: '#fff',
    boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
    marginBottom: '20px'
  },
  title: {
    margin: 0,
    fontSize: '2rem',
    fontWeight: 'bold'
  }
};

export default Header;
