package cn.js.ccit.flowersmall.goldcoin;

import cn.js.ccit.common.dubbo.GoldCoinService;
import org.apache.dubbo.config.annotation.DubboService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@DubboService
public class GoldCoinServiceImpl implements GoldCoinService {

    private static final Logger log = LoggerFactory.getLogger(GoldCoinServiceImpl.class);

    @Override
    public void updateGoldCoin(String userName, Integer goldCoin, String orderNo) {
        log.info("[goldCoin] 发放金币 user={}, coin={}, orderNo={}", userName, goldCoin, orderNo);
    }
}
