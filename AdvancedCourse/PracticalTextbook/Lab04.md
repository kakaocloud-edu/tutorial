# Container Image 만들기

Spring Boot 프로젝트를 생성해 간단한 웹 페이지를 생성합니다. 생성한 프로젝트를 Docker Image 파일로 만들어 Kakao Cloud Container Registry에 업로드하는 실습을 진행합니다.


## 1. Container Registry 생성

1. 카카오 클라우드 콘솔 > 전체 서비스 > Container Registry 접속
2. 리포지토리 생성 버튼 클릭
   - 공개 여부: 비공개
   - 리포지토리 이름 : `kakao-registry`
     - **Note**: 원활한 실습 진행을 위해 반드시 `kakao-registry`로 이름을 넣어주세요.
   - 태그 덮어쓰기 : 가능
   - 이미지 스캔 : 자동
3. 생성 버튼 클릭
4. Container Registry 생성 확인
    
## 2. Spring 어플리케이션을 Container 이미지로 만들기

1. bastion VM에 접속하여 Spring 어플리케이션이 있는 경로로 이동
   #### **lab4-2-1**
   - 접속 중인 Bastion VM 인스턴스에 명령어 입력
   ```
   cd /home/ubuntu/spring
   ```
   
2. Spring 어플리케이션 패키징 및 빌드
  
   #### **lab4-2-2-1**
   - 접속 중인 Bastion VM 인스턴스에 명령어 입력
   ```
   if sudo ./mvnw clean package; then
      echo "Maven build successful."
   else
      echo "Maven build failed."
      exit 1
   fi
   ```

    #### **lab4-2-2-2**
   - Docker 이미지 빌드에 필요한 Dockerfile 생성
   ```
   sudo bash -c "cat <<EOF > Dockerfile
   FROM openjdk:${DOCKER_JAVA_VERSION}
   RUN apt-get update && apt-get install -y curl
   COPY target/demo-0.0.1-SNAPSHOT.jar demo.jar
   ENTRYPOINT [\"java\",\"-jar\",\"/demo.jar\"]
   EOF"
   ```

   #### **lab4-2-2-3**
   - Docker 이미지 생성
   ```
   sudo docker build -t ${DOCKER_IMAGE_NAME} .    
   ```

   #### **lab4-2-2-4**
   - 빌드 된 Docker 이미지 확인
   ```
   sudo docker images
   ```
   
3. Spring 어플리케이션 패키징 및 빌드 확인

   #### **lab4-2-3**
   - 빌드 된 Docker 이미지 실행
   ```
   sudo docker run -p 8080:8080 ${DOCKER_IMAGE_NAME}
   ```

4. bastion의 Public IP 복사
5. 브라우저 주소창에 {복사한 IP 주소}:8080 입력
6. 이미지 실행 확인

## 3. Container 레지스트리에 이미지 업로드

1. 도커 로그인
   - 접속 중인 Bastion VM 인스턴스에 명령어 입력
   #### **lab4-3-1**
   ```
   docker login ${PROJECT_NAME}.kr-central-2.kcr.dev --username ${ACC_KEY} --password ${SEC_KEY}
   ```

2. Spring 어플리케이션 이미지 Push를 위한 태깅(tag)
   #### **lab4-3-2**
   ```
   docker tag ${DOCKER_IMAGE_NAME} ${PROJECT_NAME}.kr-central-2.kcr.dev/kakao-registry/${DOCKER_IMAGE_NAME}:1.0
   ```

3. 이미지 태그 확인
   #### **lab4-3-3**
   ```
   docker images
   ```
   - 현재 두 개의 이미지가 정상적으로 출력되는지 확인
   
     
4. Spring 어플리케이션 이미지 Push

   #### **lab4-3-4**
   ```
   docker push ${PROJECT_NAME}.kr-central-2.kcr.dev/kakao-registry/${DOCKER_IMAGE_NAME}:1.0
   ```
5. 카카오 클라우드 콘솔 > 전체 서비스 > Container Registry > Repository 접속
6. 생성한 Repository `kakao-registry` 클릭
7. 이미지 업로드 상태 확인


