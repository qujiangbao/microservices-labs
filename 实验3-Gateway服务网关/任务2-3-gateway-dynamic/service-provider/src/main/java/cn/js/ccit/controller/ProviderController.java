package cn.js.ccit.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.time.ZoneId;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;

@RestController
public class ProviderController {

    @GetMapping("/hello")
    public String hello(@RequestParam String name) {
        String now = ZonedDateTime.now(ZoneId.of("Asia/Shanghai"))
                .format(DateTimeFormatter.ISO_ZONED_DATE_TIME);
        return "hello" + name + now;
    }
}
