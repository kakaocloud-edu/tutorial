// src/App.tsx
import React from 'react';
import MainPage from './pages/MainPage';
import GlobalStyle from './styles/GlobalStyle';

const App: React.FC = () => {
    return (
        <div className="App" style={{ padding:'1px' }} >
            <GlobalStyle />
            <MainPage />
        </div>
    );
};

export default App;
