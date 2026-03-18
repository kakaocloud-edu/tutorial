# YAML 이해 가이드

## 목표
이 문서를 통해 학생은 다음을 이해한다:

- YAML이 무엇인지
- YAML 문법과 구조
- 들여쓰기의 중요성
- 리스트, 딕셔너리 구조
- 실제 데이터 표현 방식

---

# 1. YAML이란 무엇인가?

👉 YAML = "YAML Ain't Markup Language"

👉 쉽게 말하면:
**사람이 읽기 쉬운 데이터 표현 방식**

---

## 왜 YAML을 쓰는가?

- 사람이 읽기 쉬움
- 설정 파일에 적합
- Kubernetes, Docker, CI/CD에서 널리 사용

---

## 한 줄 정리

👉 **YAML = 데이터를 구조적으로 표현하는 텍스트 포맷**

---

# 2. YAML의 핵심 개념

YAML은 단 3가지로 이루어져 있다:

1. Key-Value (속성)
2. List (목록)
3. Nesting (구조)

---

# 3. 기본 문법 (Key-Value)

```yaml
name: choonghee
age: 30
job: professor

👉 의미:

name → choonghee

age → 30

job → professor

⚠️ 매우 중요

👉 콜론(:) 뒤에는 반드시 공백

❌ 잘못된 예

name:choonghee
4. 들여쓰기 (🔥 가장 중요)

YAML에서 들여쓰기는 구조 자체이다.

person:
  name: choonghee
  age: 30

👉 의미:

person 안에 name, age가 있음

❗ 절대 규칙

공백(space)만 사용

tab 사용 ❌

들여쓰기 틀리면 오류 발생

5. List (목록)
hobbies:
  - soccer
  - music
  - coding

👉 의미:

hobbies = 리스트

Key + List
students:
  - name: kim
  - name: lee
6. Dictionary (객체)
person:
  name: choonghee
  age: 30

👉 Key 아래에 여러 속성이 들어감

7. List + Dictionary 조합
students:
  - name: kim
    age: 20
  - name: lee
    age: 22

👉 가장 많이 쓰이는 구조

8. 문자열, 숫자, 불린
name: choonghee
age: 30
isStudent: true

👉 자동으로 타입 인식

문자열 주의
value: "hello world"
value2: 'hello world'

👉 공백 있으면 따옴표 권장

9. 주석
# 이건 주석입니다
name: choonghee

10. 멀티라인 문자열
message: |
  Hello
  World

👉 줄바꿈 유지

11. YAML 구조를 그림으로 이해
person
 ├── name: choonghee
 ├── age: 30
 └── hobbies
      ├── soccer
      ├── music
      └── coding
12. JSON과 비교
JSON
{
  "name": "choonghee",
  "age": 30
}
YAML
name: choonghee
age: 30

👉 YAML이 훨씬 읽기 쉬움

13. YAML의 핵심 규칙 정리

👉 반드시 기억해야 할 5가지

들여쓰기가 구조를 결정한다

공백만 사용 (tab 금지)

Key: Value 형태

리스트는 - 사용

사람이 읽기 쉽게 작성

14. 실수 TOP 5

❌ 들여쓰기 틀림
❌ tab 사용
❌ 콜론 뒤 공백 없음
❌ 리스트 정렬 오류
❌ 구조 깨짐

15. 실습 예제

👉 다음 YAML을 해석해보세요

server:
  port: 8080
  users:
    - name: kim
      role: admin
    - name: lee
      role: user
✔️ 해석

server
port: 8080
users:
  kim (admin)
  lee (user)
