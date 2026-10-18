package com.example.demo;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class ExperienceController {

    @GetMapping({"/experience", "/experience/"})
    public String experience() {
        return "experience";
    }
}
