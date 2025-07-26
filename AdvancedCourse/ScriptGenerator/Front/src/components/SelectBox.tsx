// src/components/SelectBox.tsx
import React from 'react';
import styled from 'styled-components';

interface SelectBoxProps {
    label: string;
    value: string;
    options: string[];
    onChange: (e: React.ChangeEvent<HTMLSelectElement>) => void;
    disabled?: boolean;
}

const Container = styled.div`
    margin-bottom: 2.1em;
    width: 100%;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    align-items: inherit;
    position: relative;
`;

const Label = styled.label`
    display: inline;
    margin-bottom: 0.5em;
    margin-right: 1em;
    font-weight: bold;
    color: white;
`;

const SelectWrapper = styled.div`
    position: relative;
    width: 100%;

    &::after {
        content: '▼';
        position: absolute;
        top: 50%;
        right: 10px; /* 화살표 위치 조정 */
        transform: translateY(-50%);
        pointer-events: none;
    }
`;

// ✅ $ 접두사 사용으로 DOM 전달 방지
const Select = styled.select<{ $isPlaceholder: boolean }>`
    width: 100%;
    padding: 0.75em;
    padding-right: 2em; /* 화살표와 겹치지 않도록 패딩 추가 */
    border: 1px solid #ccc;
    border-radius: 4px;
    transition: all 0.3s ease;
    height: auto;
    background-color: white;
    color: ${({ $isPlaceholder }) => ($isPlaceholder ? '#aaa' : 'black')}; /* ✅ $ 접두사 사용 */

    &:focus {
        border-color: #007bff;
        box-shadow: 0 0 8px rgba(0, 123, 255, 0.2);
        outline: none;
    }
`;

const SelectBox: React.FC<SelectBoxProps> = ({ label, value, options, onChange }) => {
    const isPlaceholder = value === '';

    return (
        <Container>
            <Label>{label}</Label>
            <SelectWrapper>
                <Select 
                    value={value} 
                    onChange={onChange} 
                    $isPlaceholder={isPlaceholder}
                >
                    <option value="" style={{ color: '#aaa' }}>
                        Select an option
                    </option>
                    {options.map((option, index) => (
                        <option key={index} value={option} style={{ color: 'black' }}>
                            {option}
                        </option>
                    ))}
                </Select>
            </SelectWrapper>
        </Container>
    );
};

export default SelectBox;
