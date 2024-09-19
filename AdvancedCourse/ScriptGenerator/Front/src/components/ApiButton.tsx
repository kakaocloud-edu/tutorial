// src/components/ApiButton.tsx
import React from 'react';
import { SharedButton } from './ButtonStyles';
import styled from 'styled-components';

interface ApiButtonProps {
    id: string;
    label: string;
    onClick: (id: string) => void;
    isLoading: boolean;
    disabled?: boolean; // 추가된 부분
}

const Loader = styled.div`
    border: 4px solid rgba(255, 255, 255, 0.3);
    border-radius: 50%;
    border-top: 4px solid #fff;
    width: 16px;
    height: 16px;
    animation: spin 2s linear infinite;

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
`;

const ApiButton: React.FC<ApiButtonProps> = ({ id, label, onClick, isLoading, disabled = false }) => {
    const handleClick = () => {
        onClick(id);
    };

    return (
        <SharedButton onClick={handleClick} disabled={isLoading || disabled}>
            {isLoading ? <Loader /> : label}
        </SharedButton>
    );
};

export default ApiButton;
