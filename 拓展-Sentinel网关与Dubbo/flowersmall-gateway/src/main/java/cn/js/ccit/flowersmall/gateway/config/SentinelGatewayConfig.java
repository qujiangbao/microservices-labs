package cn.js.ccit.flowersmall.gateway.config;

import com.alibaba.csp.sentinel.adapter.gateway.common.SentinelGatewayConstants;
import com.alibaba.csp.sentinel.adapter.gateway.common.rule.GatewayFlowRule;
import com.alibaba.csp.sentinel.adapter.gateway.common.rule.GatewayRuleManager;
import com.alibaba.csp.sentinel.adapter.gateway.sc.callback.GatewayCallbackManager;
import com.alibaba.csp.sentinel.slots.block.RuleConstant;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.web.reactive.function.server.ServerResponse;

import javax.annotation.PostConstruct;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

@Configuration
public class SentinelGatewayConfig {

    private static final Logger log = LoggerFactory.getLogger(SentinelGatewayConfig.class);

    /** 商品服务在网关中的路由 id（= 注册到 nacos 的服务名 product） */
    private static final String PRODUCT_ROUTE_ID = "product";

    @PostConstruct
    public void init() {
        initGatewayRules();
        initBlockHandler();
    }

    /** 网关流控规则：商品查询路由每秒最多放行 5 个请求，超过直接拒绝 */
    private void initGatewayRules() {
        Set<GatewayFlowRule> rules = new HashSet<>();

        GatewayFlowRule productRule = new GatewayFlowRule();
        productRule.setResource(PRODUCT_ROUTE_ID);
        productRule.setResourceMode(SentinelGatewayConstants.RESOURCE_MODE_ROUTE_ID);
        productRule.setGrade(RuleConstant.FLOW_GRADE_QPS);
        productRule.setCount(5);
        productRule.setIntervalSec(1);
        rules.add(productRule);

        GatewayRuleManager.loadRules(rules);
        log.info("[Sentinel-Gateway] 已加载网关流控规则: {}", rules);
    }

    /** 自定义限流响应：触发限流时返回 429 + 友好 JSON */
    private void initBlockHandler() {
        GatewayCallbackManager.setBlockHandler((exchange, t) -> {
            Map<String, Object> body = new HashMap<>(4);
            body.put("code", HttpStatus.TOO_MANY_REQUESTS.value());
            body.put("success", false);
            body.put("message", "当前访问人数过多，请稍后再试（Sentinel 网关限流）");
            body.put("path", exchange.getRequest().getPath().value());

            log.warn("[Sentinel-Gateway] 请求被限流: path={}", exchange.getRequest().getPath().value());

            return ServerResponse.status(HttpStatus.TOO_MANY_REQUESTS)
                    .contentType(MediaType.APPLICATION_JSON)
                    .bodyValue(body);
        });
    }
}
