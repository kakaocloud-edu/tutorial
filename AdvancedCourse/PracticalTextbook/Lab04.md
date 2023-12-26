# Container Image 만들기

Spring Boot 프로젝트를 생성해 간단한 웹 페이지를 생성합니다. 생성한 프로젝트를 Docker Image 파일로 만들어 Kakao Cloud Container Registry에 업로드하는 실습을 진행합니다.


## 1. Spring 어플리케이션 구현

1. 접속 중인 Bastion VM 인스턴스에 명령어 입력

   #### **lab4-1-1**

   curl https://start.spring.io/starter.zip \
   -d dependencies=web,thymeleaf \
   -d javaVersion=11 \
   -d bootVersion=3.1.0 \
   -d groupId=com.example \
   -d artifactId=demo \
   -d name=demo \
   -d description="Demo project for Spring Boot" \
   -d packageName=com.example.demo \
   -d type=maven-project \
   -o demo.zip

    unzip -o demo.zip

2. 접속 중인 Bastion VM 인스턴스에 명령어 입력

   #### **lab4-1-2**

   mkdir -p src/main/resources/templates
   
   cat <<EOF > src/main/resources/templates/welcome.html 
   <!DOCTYPE html> <html xmlns:th="http://www.thymeleaf.org"> <head> <title>Welcome</title> <style> body { font-family: 'Arial', sans-serif; color: white; margin: 0; height: 100vh; display: flex; justify-content: center; align-items: center; background: linear-gradient(145deg, #1a2e1b, #1b1a2e); overflow: hidden; } .content { text-align: center; z-index: 10; } .background-shape { position: absolute; top: 0; right: 0; bottom: 0; left: 0; width: 200px; height: 200px; background: #1119ba; border-radius: 50%; } .shape1 { top: -50px; right: -50px; } .shape2 { bottom: -80px; left: -80px; background: #e9e445; } h1 { font-size: 2.5em; margin-bottom: 0.5em; } p { margin-bottom: 2em; } .ip-address { font-size: 1.2em; padding: 0.5em 1em; border: 2px solid #e9e445; border-radius: 4px; background: transparent; } .btn { padding: 0.5em 1em; background: #e9e445; border: none; border-radius: 4px; color: white; cursor: pointer; transition: background 0.3s ease; } .btn:hover { background: #a33741; } </style> </head> <body th:style="'background: linear-gradient(145deg, #1a1a2e,' + \${backgroundColor} + ');'"> <div class="background-shape shape1"></div> <div class="background-shape shape2"></div> <div class="content"> <h1 th:text="\${welcomeMessage}">Welcome to Kakao Cloud</h1> <p>카카오클라우드의 쿠버네티스엔진 기반의 환경에서 3-티어 웹서비스를 구축하는 실습 기반 교육입니다. </p> <div class="ip-address" th:text="'현재 서버: ' + \${hostname}">현재 서버: 호스트명 </div> <button class="btn">INTO THE WORLD!</button> </div> </body> </html> 
   EOF

3. 접속 중인 Bastion VM 인스턴스에 명령어 입력

   #### **lab4-1-3**

   cat <<EOF > src/main/java/com/example/demo/HelloController.java 
   package com.example.demo; import org.springframework.stereotype.Controller; import org.springframework.ui.Model; import org.springframework.web.bind.annotation.GetMapping; import org.springframework.beans.factory.annotation.Value; import java.net.InetAddress; import java.net.UnknownHostException; import jakarta.servlet.http.HttpServletRequest; @Controller public class HelloController { @GetMapping("/") public String hello(HttpServletRequest request, Model model) { String welcomeMessage = System.getenv().getOrDefault("WELCOME_MESSAGE", "Welcome to Kakao Cloud"); String backgroundColor = System.getenv().getOrDefault("BACKGROUND_COLOR", "#1a1a2e"); String hostname = "Unknown"; try { hostname = InetAddress.getLocalHost().getHostName(); } catch (UnknownHostException e) { e.printStackTrace(); } model.addAttribute("hostname", hostname); model.addAttribute("welcomeMessage", welcomeMessage); model.addAttribute("backgroundColor", backgroundColor); return "welcome"; } } 
   EOF 

4. 접속 중인 Bastion VM 인스턴스에 명령어 입력
  
   #### **lab4-1-3**

   if ./mvnw package; then 
    # Docker 이미지 생성. 
    cat <<EOF > Dockerfile
    FROM openjdk:17-jdk-slim 
    RUN apt-get update && apt-get install -y curl 
    COPY target/demo-0.0.1-SNAPSHOT.jar 
    demo.jar ENTRYPOINT ["java","-jar","/demo.jar"] 
   EOF

    sudo docker build -t demo-spring-boot . 
   else 
    echo "Maven build failed. Docker image will not be built." 
    exit 1 
   fi 

## 2. Spring 어플리케이션을 Container 이미지로 만들기

1. 접속 중인 Bastion VM 인스턴스에 명령어 입력

   #### **lab4-2-1**

   Docker images

## 3. Container Registry 인증 설정

1. 카카오 클라우드 콘솔 > 전체 서비스 > Container Registry > Repository 접속
2. 생성 된 Repository 클릭 
3. 권한 설정 클릭
4. ID 입력란에 사용자 계정 입력
5. 사용자 계정 입력 후 확인 버튼 클릭
6. 커맨드 보기 클릭
7. 커맨드 보기 클릭 후 나온 각 명령어 메모장에 복사

## 4. Container 레지스트리에 이미지 업로드

1. 접속 중인 Bastion VM 인스턴스에 명령어 입력 

   #### **lab4-4-1**

   docker login kakaocloud.kr-central-2.kcr.dev --username {사용자 액세스 키 ID} --password {사용자 액세스 보안 키}

2. 로그인 성공 시 Login Succeeded 출력
3. 접속 중인 Bastion VM 인스턴스에 명령어 입력 

   #### **lab4-4-3**

   docker tag {소스 이미지} kakaocloud.kr-central-2.kcr.dev/k8s-repo/{이미지 이름}:{태그 이름}

4. 이미지 태그 확인
5. 접속 중인 Bastion VM 인스턴스에 명령어 입력

   #### **lab4-4-5**

   Docker imaes

6. 이미지가 정상적으로 태그되었는지 확인
7. 접속 중인 Bastion VM 인스턴스에 명령어 입력

   #### **lab4-4-7**

   docker push kakaocloud.kr-central-2.kcr.dev/k8s-repo/{이미지 이름}:{태그 이름}

8. 카카오 클라우드 콘솔 > 전체 서비스 > Container Registry > Repository 접속
9. 생성된 Repository 클릭 
10. 이미지 업로드 상태 확인