// src/components/CopyButton.tsx
import React from 'react';
import styled from 'styled-components';

interface CopyButtonProps {
    script: string;
}

const Button = styled.button`
    background-color: #007bff;
    color: white;
    border: none;
    padding: 0.75em 1.5em;
    border-radius: 4px;
    cursor: pointer;
    font-size: 1em;
    transition: all 0.001s ease-in;
    margin: 0 1em;

    &:hover {
        background-color: #0056b3;
    }

    &:focus {
        outline: none;
        box-shadow: 0 0 8px rgba(0, 91, 179, 0.6);
    }
`;

const CopyButton: React.FC<CopyButtonProps> = ({ script }) => {
    const copyToClipboard = () => {
        navigator.clipboard.writeText(script);
        alert('스크립트가 복사되었습니다.');
    };

    return <Button onClick={copyToClipboard}>스크립트 복사</Button>;
};

export default CopyButton;
