package cn.js.ccit.controller;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.cloud.context.config.annotation.RefreshScope;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RefreshScope
@RestController
public class ProviderController {

    @Value("${shared.nacos-addr:未读取到共享配置}")
    private String nacosAddr;

    @Value("${server.port}")
    private String port;

    @GetMapping("/work")
    public String work() {
        return "当前是陈汭在工作，我的端口号是" + port + "，共享配置中的Nacos地址是" + nacosAddr;
    }
}
