package cn.js.ccit.flowersmall.product;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Arrays;
import java.util.LinkedHashMap;
import java.util.Map;

@RestController
public class ProductController {

    @GetMapping("/products")
    public Map<String, Object> products() {
        Map<String, Object> rose = new LinkedHashMap<String, Object>();
        rose.put("name", "玫瑰花束");
        rose.put("price", 100);
        Map<String, Object> lily = new LinkedHashMap<String, Object>();
        lily.put("name", "百合花束");
        lily.put("price", 80);
        Map<String, Object> body = new LinkedHashMap<String, Object>();
        body.put("code", 200);
        body.put("success", true);
        body.put("data", Arrays.asList(rose, lily));
        return body;
    }
}
