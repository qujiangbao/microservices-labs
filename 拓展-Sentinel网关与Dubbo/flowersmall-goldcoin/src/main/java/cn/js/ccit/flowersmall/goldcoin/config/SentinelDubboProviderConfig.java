package cn.js.ccit.flowersmall.goldcoin.config;

import com.alibaba.csp.sentinel.adapter.dubbo.config.DubboAdapterGlobalConfig;
import com.alibaba.csp.sentinel.slots.block.RuleConstant;
import com.alibaba.csp.sentinel.slots.block.flow.FlowRule;
import com.alibaba.csp.sentinel.slots.block.flow.FlowRuleManager;
import org.apache.dubbo.rpc.AsyncRpcResult;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.context.annotation.Configuration;

import javax.annotation.PostConstruct;
import java.util.Collections;

@Configuration
public class SentinelDubboProviderConfig {

    private static final Logger log = LoggerFactory.getLogger(SentinelDubboProviderConfig.class);

    private static final String GOLD_COIN_RESOURCE =
            "cn.js.ccit.common.dubbo.GoldCoinService:updateGoldCoin(java.lang.String,java.lang.Integer,java.lang.String)";

    @PostConstruct
    public void init() {
        initFlowRules();
        initProviderFallback();
    }

    /** 提供方入口流控：updateGoldCoin 每秒最多处理 5 次（自我保护上限） */
    private void initFlowRules() {
        FlowRule rule = new FlowRule();
        rule.setResource(GOLD_COIN_RESOURCE);
        rule.setGrade(RuleConstant.FLOW_GRADE_QPS);
        rule.setCount(5);
        rule.setLimitApp("default");
        FlowRuleManager.loadRules(Collections.singletonList(rule));
        log.info("[Sentinel-Dubbo-Provider] 已加载提供方流控规则: {}", rule);
    }

    /** 提供方 fallback：被限流时优雅返回，不向上抛异常，避免误触发上游全局事务回滚 */
    private void initProviderFallback() {
        DubboAdapterGlobalConfig.setProviderFallback((invoker, invocation, ex) -> {
            log.warn("[Sentinel-Dubbo-Provider] goldCoin 被限流: method={}, rule={}",
                    invocation.getMethodName(),
                    ex.getRule() == null ? ex.getClass().getSimpleName() : ex.getRule());
            return AsyncRpcResult.newDefaultAsyncResult((Object) null, invocation);
        });
    }
}
