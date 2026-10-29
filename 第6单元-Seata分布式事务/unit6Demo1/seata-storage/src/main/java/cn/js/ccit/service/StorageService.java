package cn.js.ccit.service;

public interface StorageService {

    /** 扣减库存 */
    void reduce(Long productId, Integer count);
}
