// src/components/ScriptDisplay.tsx
import React from 'react';
import styled from 'styled-components';

interface ScriptDisplayProps {
    script: string;
}

const TextArea = styled.textarea`
    width: 100%;
    height: 300px;
    padding: 1em;
    border: 1px solid #ccc;
    border-radius: 4px;
    margin-top: 1em;
    resize: none;
    font-family: 'Courier New', Courier, monospace;
    transition: all 0.3s ease;

    &:focus {
        border-color: #007bff;
        box-shadow: 0 0 8px rgba(0, 123, 255, 0.2);
        outline: none;
    }
`;

const ScriptDisplay: React.FC<ScriptDisplayProps> = ({ script }) => {
    return (
        <div>
            <TextArea value={script} readOnly />
        </div>
    );
};

export default ScriptDisplay;
