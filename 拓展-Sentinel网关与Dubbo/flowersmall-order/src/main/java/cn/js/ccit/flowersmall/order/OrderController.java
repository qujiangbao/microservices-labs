package cn.js.ccit.flowersmall.order;

import cn.js.ccit.common.dubbo.GoldCoinService;
import org.apache.dubbo.config.annotation.DubboReference;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
public class OrderController {

    @DubboReference(url = "dubbo://127.0.0.1:20880", check = false)
    private GoldCoinService goldCoinService;

    @PostMapping("/order")
    public String order(@RequestBody Map<String, Object> body) {
        String orderNo = "NO" + System.nanoTime();
        goldCoinService.updateGoldCoin("zhangsan", 10, orderNo);
        return "ok";
    }
}
