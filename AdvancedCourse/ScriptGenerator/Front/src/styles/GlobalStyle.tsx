// src/styles/GlobalStyle.tsx
import { createGlobalStyle } from 'styled-components';

const GlobalStyle = createGlobalStyle`
    body {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
        font-family: 'Arial', sans-serif;
        background: linear-gradient(145deg, #5d7404, #0d0956);
        color: white;
        height: 100vh;
        overflow: auto;
        background-attachment: fixed; // 이 줄을 추가하여 배경이 고정되지 않도록 설정
        background-size: cover; // 배경 이미지가 전체를 덮도록 설정
    }

    * {
        box-sizing: inherit;
    }

    h1, h2, h3, h4, h5, h6, p {
        margin: 0;
    }

    .background-shape {
        position: fixed;
        width: 200px;
        height: 200px;
        background: #1119ba;
        border-radius: 50%;
    }

    .shape1 {
        top: -50px;
        right: -50px;
    }

    .shape2 {
        bottom: -80px;
        left: -80px;
        background: #ffce00;
    }

    .animated-circle {
        position: fixed;
        border-radius: 50%;
        animation: pulseAnimation 2s infinite ease-in-out;
    }

    @keyframes pulseAnimation {
        0% { transform: scale(1); }
        50% { transform: scale(1.1); }
        100% { transform: scale(1); }
    }
`;

export default GlobalStyle;