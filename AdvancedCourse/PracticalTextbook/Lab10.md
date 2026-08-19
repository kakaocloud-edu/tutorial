# DNS 서비스를 통해 도메인 주소 연결 (Demo로 진행)

DNS 서비스를 통해 Gateway Load Balancer의 Public IP로 접속하던 웹서비스를 도메인 주소로 연결합니다. DNS A 레코드가 도메인 이름을 Public IP로 변환하고, 요청이 Gateway와 HTTPRoute를 거쳐 애플리케이션에 도달하는지 확인하는 데모를 진행합니다.

## 1. DNS Zone 생성
1. 카카오 클라우드 콘솔 > Beyond Networking Service > DNS > DNS 영역
2. DNS 영역 생성 클릭

    - DNS Zone 이름: kakaocloud-edu.com
    - 생성 클릭

3. 만들어진 DNS Zone(kakaocloud-edu.com) 클릭
4. 레코드 생성 클릭

    - 레코드 타입: A
    - TTL: 60
    - 값: 연결하려는 Gateway Load Balancer의 Public IP 입력
    - 생성 버튼 클릭

   - A 레코드는 도메인 이름을 IPv4 주소에 연결합니다. TTL 60은 DNS 조회 결과를 60초 동안 캐시한다는 뜻입니다.

## 2. 네임서버 설정
1. 사용 도메인의 네임서버를 카카오클라우드의 네임서버로 바꿔주어야함
2. 도메인 구입처의 도메인 설정창에서 네임서버를 변경
3. 본 실습에서는 '가비아'라는 도메인 제공 서비스를 이용하였음

## 3. 서비스 동작 확인
1. 연결한 도메인을 브라우저 창에 입력
2. DNS 서비스 연결 확인
   - 도메인이 Gateway Load Balancer의 Public IP로 해석되고 Spring application 화면이 표시되는지 확인합니다.
   - 레코드를 만든 직후에는 DNS 전파와 캐시 갱신에 시간이 걸릴 수 있습니다.
