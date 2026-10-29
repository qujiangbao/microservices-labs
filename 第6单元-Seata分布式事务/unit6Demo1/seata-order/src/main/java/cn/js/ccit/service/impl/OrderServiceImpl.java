package cn.js.ccit.service.impl;

import cn.js.ccit.domain.Order;
import cn.js.ccit.mapper.OrderMapper;
import cn.js.ccit.service.OrderService;
import cn.js.ccit.service.StorageService;
import io.seata.spring.annotation.GlobalTransactional;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import javax.annotation.Resource;

@Service
@Slf4j
public class OrderServiceImpl implements OrderService {

    @Resource
    private OrderMapper orderMapper;

    @Resource
    private StorageService storageService;

    /** 创建订单 -> 调用库存服务扣减库存 -> 修改订单状态 */
    @Override
    @GlobalTransactional
    public void create(Order order) {
        log.info("========>下单开始");
        // 创建订单
        orderMapper.create(order);

        // 远程调用库存服务扣减库存
        storageService.reduce(order.getProductId(), order.getCount());

        // 修改订单状态为已完成
        orderMapper.update(order.getUserId(), 0);
        log.info("========>下单结束");
    }
}
