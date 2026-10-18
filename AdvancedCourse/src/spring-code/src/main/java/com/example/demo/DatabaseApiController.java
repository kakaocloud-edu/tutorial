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
