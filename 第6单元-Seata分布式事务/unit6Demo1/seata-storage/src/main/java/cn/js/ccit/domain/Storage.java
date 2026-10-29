package cn.js.ccit.domain;

import lombok.Data;

@Data
public class Storage {

    private Long id;

    /** 产品ID */
    private Long productId;

    /** 总库存 */
    private Integer total;

    /** 已用库存 */
    private Integer used;

    /** 剩余库存 */
    private Integer residue;
}
