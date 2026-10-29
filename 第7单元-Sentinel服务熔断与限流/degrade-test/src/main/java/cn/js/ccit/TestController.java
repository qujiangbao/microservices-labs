package cn.js.ccit;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class TestController {
    @GetMapping("/degrade-rt")
    public String test_degrade_rt() throws InterruptedException {
        Thread.sleep(200);
        return "rt策略测试";
    }
}
