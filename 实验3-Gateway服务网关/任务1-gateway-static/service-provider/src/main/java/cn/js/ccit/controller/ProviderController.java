package cn.js.ccit.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class ProviderController {
    @GetMapping("/hello") // @RequestParam 注解用于拿到URL后拼接的参数，
    // 如localhost:8080/hello?name=zhangsan ==> hello方法的参数name会被绑定数值zhangsan
    public String hello(@RequestParam String name) {
        return "hello " + name + "!";
    }
}
