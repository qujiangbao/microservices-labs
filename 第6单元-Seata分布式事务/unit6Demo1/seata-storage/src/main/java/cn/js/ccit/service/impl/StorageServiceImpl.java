package cn.js.ccit.service.impl;

import cn.js.ccit.mapper.StorageMapper;
import cn.js.ccit.service.StorageService;
import org.springframework.stereotype.Service;

import javax.annotation.Resource;

@Service
public class StorageServiceImpl implements StorageService {

    @Resource
    private StorageMapper storageMapper;

    /** 扣减库存 */
    @Override
    public void reduce(Long productId, Integer count) {
        storageMapper.reduce(productId, count);
    }
}
