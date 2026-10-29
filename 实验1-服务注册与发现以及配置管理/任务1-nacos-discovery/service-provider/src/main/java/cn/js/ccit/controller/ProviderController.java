package cn.js.ccit.controller;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class ProviderController {

    @Value("${server.port}")
    private String port;

    @GetMapping("/work")
    public String work() {
        return "当前是林潼在工作，我的端口号是" + port;
    }
}
