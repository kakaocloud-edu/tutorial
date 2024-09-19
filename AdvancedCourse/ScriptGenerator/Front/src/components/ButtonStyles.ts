// src/components/ButtonStyles.ts
import styled from 'styled-components';

export const SharedButton = styled.button`
    background-color: #e9e445;
    color: #000;
    border: none;
    padding: 0.4em 1em;
    margin-bottom: 0.5em;
    border-radius: 20px;
    cursor: pointer;
    font-size: 0.85em;
    transition: all 0.3s ease;
    box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);

    &:hover {
        background-color: #ffce00;
    }

    &:focus {
        outline: none;
        box-shadow: 0 0 8px rgba(255, 206, 0, 0.6);
    }
`;
