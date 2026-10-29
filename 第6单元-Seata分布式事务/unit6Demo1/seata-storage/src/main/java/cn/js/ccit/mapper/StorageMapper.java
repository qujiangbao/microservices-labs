package cn.js.ccit.mapper;

import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

@Mapper
public interface StorageMapper {

    /** 扣减库存 */
    void reduce(@Param("productId") Long productId, @Param("count") Integer count);
}
