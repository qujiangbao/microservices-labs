package cn.js.ccit.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class ProviderController {

    @GetMapping("/hello")
    public String hello(@RequestParam(defaultValue = "gateway") String name) {
        return "hello " + name + "!";
    }

    @GetMapping("/red/{segment}")
    public String red(@PathVariable String segment) {
        return "path red/" + segment;
    }

    @GetMapping("/blue/{segment}")
    public String blue(@PathVariable String segment) {
        return "path blue/" + segment;
    }
}
