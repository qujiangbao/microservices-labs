package cn.js.ccit.service;

import cn.js.ccit.domain.CommonResult;
import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;

@FeignClient(value = "seata-storage")
public interface StorageService {

    /** 扣减库存 */
    @PostMapping(value = "/storage/reduce")
    CommonResult reduce(@RequestParam("productId") Long productId,
                        @RequestParam("count") Integer count);
}
