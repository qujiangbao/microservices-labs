package cn.js.ccit.mapper;

import cn.js.ccit.domain.Order;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

@Mapper
public interface OrderMapper {

    /** 创建订单 */
    void create(Order order);

    /** 更新订单状态 */
    void update(@Param("userId") Long userId, @Param("status") Integer status);
}
