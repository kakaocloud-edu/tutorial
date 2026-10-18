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
