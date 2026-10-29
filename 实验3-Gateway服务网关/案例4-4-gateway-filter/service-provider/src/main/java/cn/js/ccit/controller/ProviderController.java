package cn.js.ccit.controller;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

@RestController
public class ProviderController {

    @Value("${server.port}")
    private Integer port;

    @GetMapping("/hello")
    public String hello(@RequestParam String name) {
        return "hello " + name + "!";
    }

    // AddRequestHeader 过滤器
    @GetMapping("/test/head")
    public String testGatewayHead(HttpServletRequest request, HttpServletResponse response) {
        String head = request.getHeader("X-Request-red");
        return "X-Request-red : " + head;
    }

    // AddRequestParameter 过滤器
    @GetMapping("/test/param")
    public String testGatewayParam(HttpServletRequest request, HttpServletResponse response) {
        String val = request.getParameter("red");
        return "param red : " + val;
    }

    // RemoveResponseHeader 过滤器
    @GetMapping("/test/reresheader")
    public String reresheader(HttpServletRequest request, HttpServletResponse response) {
        response.setHeader("X-Response-red", "blue");
        return "ok";
    }

    // LoadBalancerClientFilter 过滤器
    @GetMapping("/test/lb")
    public String testLb() {
        return "port: " + port;
    }
}
