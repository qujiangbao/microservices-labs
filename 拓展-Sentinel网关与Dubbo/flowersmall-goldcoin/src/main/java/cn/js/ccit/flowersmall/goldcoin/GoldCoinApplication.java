package cn.js.ccit.flowersmall.goldcoin;

import org.apache.dubbo.config.spring.context.annotation.EnableDubbo;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
@EnableDubbo
public class GoldCoinApplication {

    public static void main(String[] args) {
        SpringApplication.run(GoldCoinApplication.class, args);
    }
}
