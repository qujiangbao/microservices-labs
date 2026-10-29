package cn.js.ccit;

import io.seata.spring.annotation.datasource.EnableAutoDataSourceProxy;
import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.client.discovery.EnableDiscoveryClient;
import org.springframework.cloud.openfeign.EnableFeignClients;

@EnableAutoDataSourceProxy //开启Seata的数据源自动代理
@MapperScan("cn.js.ccit.mapper")
@SpringBootApplication
@EnableDiscoveryClient
@EnableFeignClients
public class SeataStorageApplication {

    public static void main(String[] args) {
        SpringApplication.run(SeataStorageApplication.class, args);
    }
}
