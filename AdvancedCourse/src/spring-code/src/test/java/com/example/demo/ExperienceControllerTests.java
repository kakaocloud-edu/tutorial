package com.example.demo;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.test.web.servlet.MvcResult;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.web.util.HtmlUtils;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import static org.assertj.core.api.Assertions.assertThat;
import static org.hamcrest.Matchers.not;
import static org.hamcrest.Matchers.emptyOrNullString;
import static org.mockito.Mockito.verifyNoInteractions;
import static org.mockito.Mockito.inOrder;
import static org.mockito.Mockito.verifyNoMoreInteractions;
import static org.mockito.Mockito.when;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.content;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.header;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.model;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.view;

@SpringBootTest
@AutoConfigureMockMvc
class ExperienceControllerTests {

    @Autowired
    private MockMvc mockMvc;

    @MockBean(name = "jdbcTemplate1")
    private JdbcTemplate primaryDatabase;

    @MockBean(name = "jdbcTemplate2")
    private JdbcTemplate secondaryDatabase;

    @Test
    void introductionRoutesRenderWithoutQueryingDatabases() throws Exception {
        for (String path : new String[]{"/experience", "/experience/"}) {
            mockMvc.perform(get(path))
                    .andExpect(status().isOk())
                    .andExpect(view().name("experience"));
        }

        verifyNoInteractions(primaryDatabase, secondaryDatabase);
    }

    @Test
    void originalLabRendersItsLiveModelWithTheEmbeddedStoryWithoutDatabaseCalls() throws Exception {
        MvcResult result = mockMvc.perform(get("/"))
                .andExpect(status().isOk())
                .andExpect(view().name("welcome"))
                .andExpect(model().attribute("welcomeMessage",
                        System.getenv().getOrDefault("WELCOME_MESSAGE", "Welcome to Kakao Cloud")))
                .andExpect(model().attribute("backgroundColor",
                        System.getenv().getOrDefault("BACKGROUND_COLOR", "#1a1a2e")))
                .andExpect(model().attribute("hostname", not(emptyOrNullString())))
                .andReturn();

        String html = result.getResponse().getContentAsString(java.nio.charset.StandardCharsets.UTF_8);
        String hostname = (String) result.getModelAndView().getModel().get("hostname");
        assertThat(html).contains("id=\"lab-story\"", "id=\"lab\"", "id=\"cloud-experience\"",
                "data-embedded=\"true\"", "href=\"#lab\"", "/experience/immersive.css",
                "/experience/immersive.js", "id=\"toggleContent\"", "id=\"dbinfo\"",
                "서버의 호스트 이름: " + HtmlUtils.htmlEscape(hostname));
        assertThat(html.indexOf("id=\"lab\""))
                .isLessThan(html.indexOf("id=\"cloud-experience\""));
        String activeMarkup = html.replaceAll("(?s)<noscript>.*?</noscript>", "");
        assertThat(activeMarkup).doesNotContainPattern("<(?:img|video|source)\\b[^>]*\\s(?:src|srcset)=[\"']/experience/(?:frames|film)/");
        assertThat(activeMarkup).doesNotContain("rel=\"preload\"", "rel=\"prefetch\"");
        assertThat(html).doesNotContain("href=\"/experience/experience.css\"",
                "src=\"/experience/experience.js\"");

        verifyNoInteractions(primaryDatabase, secondaryDatabase);
    }

    @Test
    void publishedFilmFramesAndPosterAreServedAndCanBeRevalidatedWithoutDatabaseCalls() throws Exception {
        String html = mockMvc.perform(get("/"))
                .andExpect(status().isOk())
                .andReturn().getResponse().getContentAsString(java.nio.charset.StandardCharsets.UTF_8);
        int count = Integer.parseInt(attribute(html, "data-frame-count"));
        String pattern = attribute(html, "data-frame-pattern");
        assertThat(count).isPositive();
        assertThat(pattern).startsWith("/experience/film/").contains("{index}.webp?v=");

        for (int index : new int[]{0, count / 2, count - 1}) {
            String path = pattern.replace("{index}", String.format("%03d", index));
            MvcResult frame = mockMvc.perform(get(path))
                    .andExpect(status().isOk())
                    .andExpect(content().contentType("image/webp"))
                    .andExpect(header().exists("Last-Modified"))
                    .andReturn();
            byte[] bytes = frame.getResponse().getContentAsByteArray();
            assertThat(bytes.length).isGreaterThan(12);
            assertThat(new String(bytes, 0, 4, java.nio.charset.StandardCharsets.US_ASCII)).isEqualTo("RIFF");
            assertThat(new String(bytes, 8, 4, java.nio.charset.StandardCharsets.US_ASCII)).isEqualTo("WEBP");
            mockMvc.perform(get(path).header("If-Modified-Since", frame.getResponse().getHeader("Last-Modified")))
                    .andExpect(status().isNotModified());
        }

        mockMvc.perform(get("/experience/film/poster.webp"))
                .andExpect(status().isOk())
                .andExpect(content().contentType("image/webp"));
        mockMvc.perform(get("/experience/film/manifest.json"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.count").value(count))
                .andExpect(jsonPath("$.width").value(Integer.parseInt(attribute(html, "data-frame-width"))))
                .andExpect(jsonPath("$.height").value(Integer.parseInt(attribute(html, "data-frame-height"))))
                .andExpect(jsonPath("$.attributionPreserved").value(false))
                .andExpect(jsonPath("$.visibleWatermarkRemoved").value(true))
                .andExpect(jsonPath("$.crop").value(false));
        verifyNoInteractions(primaryDatabase, secondaryDatabase);
    }

    @Test
    void firstAvailabilityZoneEndpointStillInsertsBeforeSelecting() throws Exception {
        when(primaryDatabase.queryForList("SELECT * FROM access"))
                .thenReturn(List.of(Map.of("date", "primary-result")));

        mockMvc.perform(get("/db1"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.dbConnection.URL").value(
                        System.getenv().getOrDefault("DB1_URL", "az-a.database.example.com")))
                .andExpect(jsonPath("$.data[0].date").value("primary-result"));

        var calls = inOrder(primaryDatabase);
        calls.verify(primaryDatabase).update(eq("INSERT INTO access (date) VALUES (?)"), any(LocalDateTime.class));
        calls.verify(primaryDatabase).queryForList("SELECT * FROM access");
        verifyNoMoreInteractions(primaryDatabase);
        verifyNoInteractions(secondaryDatabase);
    }

    @Test
    void secondAvailabilityZoneEndpointStillOnlySelects() throws Exception {
        when(secondaryDatabase.queryForList("SELECT * FROM access"))
                .thenReturn(List.of(Map.of("date", "secondary-result")));

        mockMvc.perform(get("/db2"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.dbConnection.URL").value(
                        System.getenv().getOrDefault("DB2_URL", "az-b.database.example.com")))
                .andExpect(jsonPath("$.data[0].date").value("secondary-result"));

        var calls = inOrder(secondaryDatabase);
        calls.verify(secondaryDatabase).queryForList("SELECT * FROM access");
        verifyNoMoreInteractions(secondaryDatabase);
        verifyNoInteractions(primaryDatabase);
    }

    private static String attribute(String html, String name) {
        Matcher match = Pattern.compile(Pattern.quote(name) + "=\"([^\"]+)\"").matcher(html);
        assertThat(match.find()).as("Rendered page contains %s", name).isTrue();
        return match.group(1);
    }
}
