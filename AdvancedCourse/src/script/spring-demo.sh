#!/bin/bash

# Spring Boot 프로젝트 생성
curl https://start.spring.io/starter.zip \
     -d dependencies=web,thymeleaf,jdbc,mysql \
     -d javaVersion=${JAVA_VERSION} \
     -d bootVersion=${SPRING_BOOT_VERSION} \
     -d groupId=com.example \
     -d artifactId=demo \
     -d name=demo \
     -d description="Demo project for Spring Boot" \
     -d packageName=com.example.demo \
     -d type=maven-project \
     -o demo.zip
unzip -o demo.zip

# Main 웹 페이지
mkdir -p src/main/resources/templates
cat <<EOF > src/main/resources/templates/welcome.html
<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org">
<head>
    <title>Welcome</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            color: white;
            margin: 0;
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            background: linear-gradient(145deg, #5d7404, #0d0956);
            overflow: hidden;
        }
        .content {
            text-align: center;
            z-index: 10;
        }
        .background-shape {
            position: absolute;
            top: 0;
            right: 0;
            bottom: 0;
            left: 0;
            width: 200px;
            height: 200px;
            background: #1119ba;
            border-radius: 50%;
        }
        .shape1 {
            top: -50px;
            right: -50px;
        }
        .shape2 {
            bottom: -80px;
            left: -80px;
            background: #e9e445;
        }
        h1 {
            font-size: 2.5em;
            margin-bottom: 0.5em;
        }
        p {
            margin-bottom: 2em;
        }

        .db-row {
            margin-bottom: 0; /* 추가된 클래스 스타일 */
        }

        .server-name {
            font-size: 1.2em;
            padding: 0.5em 1em;
            border: 2px solid #e9e445;
            border-radius: 4px;
            background: transparent;
            margin-bottom: 2em;
            max-height: 500px;
            overflow-y: auto; 
        }

        .animated-circle {
            position: absolute;
            border-radius: 50%;
            animation: pulseAnimation 2s infinite ease-in-out;
        }

        @keyframes pulseAnimation {
            0% { transform: scale(1); }
            50% { transform: scale(1.1); }
            100% { transform: scale(1); }
        }

        ul {
            list-style-type: none; /* Removes default bullets */
            padding-left: 0; /* Removes default padding */
        }

        ul li {
            background: #e9e445; /* Same background as buttons */
            color: white; /* Text color */
            padding: 0.5em 1em; /* Same padding as buttons */
            margin: 0.5em 0; /* Space between list items */
            border-radius: 4px; /* Rounded corners */
            cursor: pointer; /* Cursor changes on hover */
            transition: background 0.3s ease; /* Smooth background transition */
        }

        ul li:hover {
            background: #a33741; /* Hover effect similar to buttons */
        }

        /* New styles for button container */
        .button-container {
            display: flex; /* Aligns buttons horizontally */
            justify-content: space-around; /* Spaces out buttons evenly */
            margin: 1em 0; /* Margin above and below the container */
        }

        /* Styles for buttons (if not already styled) */
        .btn {
            padding: 0.5em 1em; /* Padding */
            background: #e9e445; /* Background color */
            border: none; /* No border */
            border-radius: 4px; /* Rounded corners */
            color: black; /* Text color */
            cursor: pointer; /* Cursor changes on hover */
            transition: background 0.3s ease; /* Smooth background transition */
        }

        .btn:hover {
            background: #a33741; /* Hover effect */
        }

    </style>
</head>
<body th:style="'background: linear-gradient(145deg, #1a1a2e,' + \${backgroundColor} + ');'">
    <div class="background-shape shape1 animated-circle"></div>
    <div class="background-shape shape2 animated-circle"></div>
    <div class="content">
        <h1 th:text="\${welcomeMessage}">Welcome to kakaocloud</h1>
        <p>카카오클라우드의 Kubernetes Engine 서비스를 기반으로 하는 실습 중심의 3-티어 웹서비스 구축 교육입니다.</p>
        <div class="server-name " th:text="'서버의 호스트 이름: ' + \${hostname}">서버의 호스트 이름</div>

        <button class="btn" onclick="toggleVisibility()">가용 영역별 DB 연동 열기/닫기</button>

        <!-- Container for the content to show/hide -->
        <div id="toggleContent" style="display: none;">
            <div class="button-container">
                <button class="btn" onclick="loadDbInfo('/db1')">첫 번째 가용 영역 DB에 데이터 삽입 및 조회</button>
                <button class="btn" onclick="loadDbInfo('/db2')">두 번째 가용 영역 DB에 데이터 단순 조회</button>
            </div>
            <p class="server-name" id="dbinfo">위의 두 버튼 중 하나를 클릭하세요.</p>

        </div>

        <script>
            function toggleVisibility() {
                var content = document.getElementById("toggleContent");
                content.style.display = content.style.display === "none" ? "block" : "none";
            }

            function loadDbInfo(endpoint) {
                fetch(endpoint)
                    .then(response => response.json())
                    .then(data => {
                        var dbInfoElement = document.getElementById("dbinfo");
                        var dbConnection = 'Endpoint: ' + data.dbConnection.URL + ', Port: ' + data.dbConnection.Port;
                        var formattedData = data.data.map(item => JSON.stringify(item)).join(',<br>');
                        dbInfoElement.innerHTML = dbConnection + '<br><br>' + formattedData;
                    })
                    .catch(error => console.error('Error:', error));
            }
    </script>
    </div>
</body>
</html>
EOF


cat <<EOF > src/main/java/com/example/demo/DatabaseConfig.java
package com.example.demo;

import org.springframework.jdbc.datasource.DriverManagerDataSource;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.jdbc.core.JdbcTemplate;
import javax.sql.DataSource;

@Configuration
public class DatabaseConfig {

    @Bean
    public String db1Url() {
        return System.getenv().getOrDefault("DB1_URL", "az-a.database.example.com");
    }

    @Bean
    public String db1Port() {
        return System.getenv().getOrDefault("DB1_PORT", "3306");
    }

    @Bean
    public String db2Url() {
        return System.getenv().getOrDefault("DB2_URL", "az-b.database.example.com");
    }

    @Bean
    public String db2Port() {
        return System.getenv().getOrDefault("DB2_PORT", "3307");
    }

    @Bean
    public DataSource dataSource1() {
        return new DriverManagerDataSource() {{
            setDriverClassName("com.mysql.cj.jdbc.Driver");
            setUrl("jdbc:mysql://" + db1Url() + ":" + db1Port() + "/history");
            setUsername(System.getenv().getOrDefault("DB1_ID", "id1"));
            setPassword(System.getenv().getOrDefault("DB1_PW", "password1"));
        }};
    }

    @Bean
    public DataSource dataSource2() {
        return new DriverManagerDataSource() {{
            setDriverClassName("com.mysql.cj.jdbc.Driver");
            setUrl("jdbc:mysql://" + db2Url() + ":" + db2Port() + "/history");
            setUsername(System.getenv().getOrDefault("DB2_ID", "id2"));
            setPassword(System.getenv().getOrDefault("DB2_PW", "password2"));
        }};
    }

    // dataSource1을 사용하는 JdbcTemplate 인스턴스를 생성합니다.
    @Bean
    public JdbcTemplate jdbcTemplate1(DataSource dataSource1) {
        return new JdbcTemplate(dataSource1);
    }

    // dataSource2를 사용하는 JdbcTemplate 인스턴스를 생성합니다.
    @Bean
    public JdbcTemplate jdbcTemplate2(DataSource dataSource2) {
        return new JdbcTemplate(dataSource2);
    }

}
EOF


cat <<EOF > src/main/java/com/example/demo/HelloController.java
package com.example.demo;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import java.net.InetAddress;
import java.net.UnknownHostException;

@Controller
public class HelloController {

    @GetMapping("/")
    public String hello(Model model) {
        String welcomeMessage = System.getenv().getOrDefault("WELCOME_MESSAGE", "Welcome to Kakao Cloud");
        String backgroundColor = System.getenv().getOrDefault("BACKGROUND_COLOR", "#1a1a2e");

        String hostname = "Unknown";
        try {
            hostname = InetAddress.getLocalHost().getHostName();
        } catch (UnknownHostException e) {
            e.printStackTrace();
        }

        model.addAttribute("hostname", hostname);
        model.addAttribute("welcomeMessage", welcomeMessage);
        model.addAttribute("backgroundColor", backgroundColor);

        return "welcome";
    }
}
EOF

cat <<EOF > src/main/java/com/example/demo/DatabaseApiController.java
package com.example.demo;

import org.springframework.web.bind.annotation.RestController;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.beans.factory.annotation.Qualifier;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import java.util.HashMap;


@RestController
public class DatabaseApiController {

    private JdbcTemplate jdbcTemplate1;
    private JdbcTemplate jdbcTemplate2;
    private String db1Url;
    private String db1Port;
    private String db2Url;
    private String db2Port;

    @Autowired
    public DatabaseApiController(JdbcTemplate jdbcTemplate1, JdbcTemplate jdbcTemplate2,
                                 @Qualifier("db1Url") String db1Url, @Qualifier("db1Port") String db1Port,
                                 @Qualifier("db2Url") String db2Url, @Qualifier("db2Port") String db2Port) {
        this.jdbcTemplate1 = jdbcTemplate1;
        this.jdbcTemplate2 = jdbcTemplate2;
        this.db1Url = db1Url;
        this.db1Port = db1Port;
        this.db2Url = db2Url;
        this.db2Port = db2Port;
    }


    // Add methods to get database connection details
    private Map<String, String> getDbConnectionDetails(JdbcTemplate jdbcTemplate, String dbUrl, String dbPort) {
        Map<String, String> details = new HashMap<>();
        details.put("URL", dbUrl);
        details.put("Port", dbPort);
        return details;
    }

    @GetMapping("/db1")
    public Map<String, Object> getDb1Data() {
        insertDatabase(jdbcTemplate1);
        Map<String, Object> response = new HashMap<>();
        response.put("dbConnection", getDbConnectionDetails(jdbcTemplate1, db1Url, db1Port));
        response.put("data", selectDatabase(jdbcTemplate1));
        return response;
    }

    @GetMapping("/db2")
    public Map<String, Object> getDb2Data() {
        Map<String, Object> response = new HashMap<>();
        response.put("dbConnection", getDbConnectionDetails(jdbcTemplate2, db2Url, db2Port));
        response.put("data", selectDatabase(jdbcTemplate2));
        return response;
    }

    private void insertDatabase(JdbcTemplate jdbcTemplate) {
        LocalDateTime now = LocalDateTime.now(ZoneId.of("Asia/Seoul"));
        jdbcTemplate.update("INSERT INTO access (date) VALUES (?)", now);
    }

    private List<Map<String, Object>> selectDatabase(JdbcTemplate jdbcTemplate) {
        return jdbcTemplate.queryForList("SELECT * FROM access");
    }
}
EOF
