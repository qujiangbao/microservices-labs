package com.example.demo;

import org.springframework.web.client.RestTemplate;

import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class TestThread {
    public static void main(String[] args) {
        RestTemplate restTemplate = new RestTemplate();
        ExecutorService executorService = Executors.newFixedThreadPool(10);
        for (int i = 0; i < 50; i++) {
            executorService.submit(() -> {
                try {
                    System.out.println(restTemplate.getForObject(
                            "http://localhost:8089/hi", String.class));
                } catch (Exception e) {
                    System.out.println("exception: " + e.getMessage());
                }
            });
        }
        executorService.shutdown();
    }
}
