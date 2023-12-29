# Container Image 만들기

Spring Boot 프로젝트를 생성해 간단한 웹 페이지를 생성합니다. 생성한 프로젝트를 Docker Image 파일로 만들어 Kakao Cloud Container Registry에 업로드하는 실습을 진행합니다.


## 1. Spring 어플리케이션 구현

1. Spring 어플리케이션 다운로드
   - 접속 중인 Bastion VM 인스턴스 터미널에 명령어 입력
   #### **lab4-1-1**
   ```
   wget https://github.com/kakaocloud-edu/tutorial/raw/main/AdvancedCourse/src/demo.zip
   ```

2. 다운로드한 Spring 어플리케이션 압축 해제

   - 접속 중인 Bastion VM 인스턴스 터미널에 명령어 입력
   #### **lab4-1-2**
   ```
   unzip -o demo.zip
   ```
    
## 2. Spring 어플리케이션을 Container 이미지로 만들기

   
1. Spring 어플리케이션 패키징 및 빌드
  
   #### **lab4-2-1**
   - 접속 중인 Bastion VM 인스턴스에 명령어 입력
   ```
   if ./mvnw clean package; then
      echo "Maven build successful."
   else
      echo "Maven build failed."
      exit 1
   fi
   ```

    #### **lab4-2-2**
   - 접속 중인 Bastion VM 인스턴스에 명령어 입력
   ```
   cat <<EOF > Dockerfile
   FROM openjdk:${DOCKER_JAVA_VERSION}
   RUN apt-get update && apt-get install -y curl
   COPY target/demo-0.0.1-SNAPSHOT.jar demo.jar
   ENTRYPOINT ["java","-jar","/demo.jar"]
   EOF
   ```

   #### **lab4-2-3**
   - 접속 중인 Bastion VM 인스턴스에 명령어 입력
   ```
   sudo docker build -t ${DOCKER_IMAGE_NAME} .    
   ```

## 3. Container Registry에 업로드

1. 카카오 클라우드 콘솔 > 전체 서비스 > Container Registry > Repository 접속
2. 생성 된 Repository 클릭 
3. 권한 설정 클릭
4. ID 입력란에 사용자 계정 입력
5. 사용자 계정 입력 후 확인 버튼 클릭
6. 커맨드 보기 클릭
7. 커맨드 보기 클릭 후 나온 각 명령어 메모장에 복사

## 4. Container 레지스트리에 이미지 업로드

1. 도커 로그인
   - 접속 중인 Bastion VM 인스턴스에 명령어 입력 
   #### **lab4-4-1**
   ```
   docker login {프로젝트 이름}.kr-central-2.kcr.dev --username {사용자 액세스 키 ID} --password {사용자 액세스 보안 키}
   ```

2. 로그인 성공 시 출력되는 `Login Succeeded` 확인
3. 생성한 이미지 태그하기
   - 접속 중인 Bastion VM 인스턴스에 명령어 입력 
   #### **lab4-4-3**
   ```
   docker tag demo-spring-boot {프로젝트 이름}.kr-central-2.kcr.dev/kakao-registry/demo-spring-boot:1.0
   ```

4. 이미지 태그 확인
   - 접속 중인 Bastion VM 인스턴스에 명령어 입력
   #### **lab4-4-5**
   - 현재 두 개의 이미지가 정상적으로 출력되는지 확인
   ```
   docker images
   ```
   
6. 이미지가 정상적으로 태그되었는지 확인
7. 이미지 업로드하기
   - 접속 중인 Bastion VM 인스턴스에 명령어 입력 
   #### **lab4-4-7**
   ```
   docker push {프로젝트 이름}.kr-central-2.kcr.dev/kakao-registry/demo-spring-boot:1.0
   ```
8. 카카오 클라우드 콘솔 > 전체 서비스 > Container Registry > Repository 접속
9. 생성한 Repository `kakao-registry` 클릭
10. 이미지 업로드 상태 확인
