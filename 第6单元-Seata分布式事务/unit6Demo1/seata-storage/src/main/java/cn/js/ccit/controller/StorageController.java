package cn.js.ccit.controller;

import cn.js.ccit.domain.CommonResult;
import cn.js.ccit.service.StorageService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class StorageController {

    @Autowired
    private StorageService storageService;

    /** 扣减库存 */
    @RequestMapping("/storage/reduce")
    public CommonResult reduce(Long productId, Integer count) {
        storageService.reduce(productId, count);
        return new CommonResult(200, "扣减库存成功！");
    }
}
