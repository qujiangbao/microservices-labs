package cn.js.ccit.flowersmall.order.config;

import com.alibaba.csp.sentinel.adapter.dubbo.config.DubboAdapterGlobalConfig;
import com.alibaba.csp.sentinel.slots.block.RuleConstant;
import com.alibaba.csp.sentinel.slots.block.degrade.circuitbreaker.CircuitBreakerStrategy;
import com.alibaba.csp.sentinel.slots.block.degrade.DegradeRule;
import com.alibaba.csp.sentinel.slots.block.degrade.DegradeRuleManager;
import com.alibaba.csp.sentinel.slots.block.flow.FlowRule;
import com.alibaba.csp.sentinel.slots.block.flow.FlowRuleManager;
import org.apache.dubbo.rpc.AsyncRpcResult;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.context.annotation.Configuration;

import javax.annotation.PostConstruct;
import java.util.Collections;

@Configuration
public class SentinelDubboConfig {

    private static final Logger log = LoggerFactory.getLogger(SentinelDubboConfig.class);

    private static final String GOLD_COIN_RESOURCE =
            "cn.js.ccit.common.dubbo.GoldCoinService:updateGoldCoin(java.lang.String,java.lang.Integer,java.lang.String)";

    @PostConstruct
    public void init() {
        initFlowRules();
        initDegradeRules();
        initConsumerFallback();
    }

    /** 流控：下单发金币 QPS 超过 2 直接拒绝（演示阈值） */
    private void initFlowRules() {
        FlowRule rule = new FlowRule();
        rule.setResource(GOLD_COIN_RESOURCE);
        rule.setGrade(RuleConstant.FLOW_GRADE_QPS);
        rule.setCount(2);
        rule.setLimitApp("default");
        FlowRuleManager.loadRules(Collections.singletonList(rule));
        log.info("[Sentinel-Dubbo] 已加载流控规则: {}", rule);
    }

    /** 熔断降级：10s 内请求数>=5 且异常比例>50% 时熔断 10s */
    private void initDegradeRules() {
        DegradeRule rule = new DegradeRule();
        rule.setResource(GOLD_COIN_RESOURCE);
        rule.setGrade(CircuitBreakerStrategy.ERROR_RATIO.getType());
        rule.setCount(0.5);
        rule.setMinRequestAmount(5);
        rule.setStatIntervalMs(10000);
        rule.setTimeWindow(10);
        DegradeRuleManager.loadRules(Collections.singletonList(rule));
        log.info("[Sentinel-Dubbo] 已加载熔断降级规则: resource={}", GOLD_COIN_RESOURCE);
    }

    /** 消费端 fallback：被限流/熔断时优雅降级（void 返回 null），下单不报错 */
    private void initConsumerFallback() {
        DubboAdapterGlobalConfig.setConsumerFallback((invoker, invocation, ex) -> {
            log.warn("[Sentinel-Dubbo] 下单发金币被拦截(限流/熔断): method={}, rule={}",
                    invocation.getMethodName(),
                    ex.getRule() == null ? ex.getClass().getSimpleName() : ex.getRule());
            return AsyncRpcResult.newDefaultAsyncResult((Object) null, invocation);
        });
    }
}
