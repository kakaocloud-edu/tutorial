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
