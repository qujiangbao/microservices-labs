package com.example.demo;

import com.alibaba.csp.sentinel.annotation.SentinelResource;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class TestController {
    @GetMapping({"/", "/hi"})
    public String hi() {
        return "hi";
    }

    @GetMapping("/hello")
    public String hello(@RequestParam String name) {
        return "Hello " + name + "!";
    }

    @GetMapping("/hotpoint")
    @SentinelResource("hotpoint")
    public String hotpoint(String type, String name) {
        return "type: " + type + ", name: " + name + "\n";
    }

    @GetMapping("/test-sys-rt")
    public String testRT() throws InterruptedException {
        Thread.sleep(200);
        return "test sys rt";
    }

    @GetMapping("/test-sys-qps1")
    public String testQps1() {
        return "test qps 1";
    }

    @GetMapping("/test-sys-qps2")
    public String testQps2() {
        return "test qps 2";
    }

    @GetMapping("/test-sys-qps3")
    public String testQps3() {
        return "test qps 3";
    }
}
