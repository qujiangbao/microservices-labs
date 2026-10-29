package cn.js.ccit.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.cloud.context.config.annotation.RefreshScope;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestTemplate;

@RefreshScope
@RestController
public class ConsumerController {

    @Autowired
    private RestTemplate restTemplate;

    @Value("${shared.nacos-addr:未读取到共享配置}")
    private String nacosAddr;

    @GetMapping("/work")
    public String work() {
        String providerResult = restTemplate.getForObject("http://share-provider/work", String.class);
        return "消费者读到的共享配置：" + nacosAddr + "；提供者返回：" + providerResult;
    }
}
