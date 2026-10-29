package cn.js.ccit.config;

import com.alibaba.fastjson.JSON;
import com.alibaba.nacos.api.NacosFactory;
import com.alibaba.nacos.api.config.ConfigService;
import com.alibaba.nacos.api.config.listener.Listener;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.cloud.gateway.route.RouteDefinition;
import org.springframework.stereotype.Component;

import javax.annotation.PostConstruct;
import java.util.concurrent.Executor;

// 负责 Nacos路由配置加载与监听
@Component
public class RouteNacos {

    public final String NACOS_SERVER_ADDR = "localhost:8848";
    public final String NACOS_DATA_ID = "gateway-route";
    public final String NACOS_DATA_GROUP = "GATEWAY_GROUP";

    @Autowired
    private MyRouteWriter myRouteWriter;

    /**
     * 服务启动后的处理逻辑
     * 1.连接 Nacos
     * 2.加载 Nacos 已有的路由配置
     * 3.监听 Nacos 路由配置的变化
     */
    @PostConstruct
    // 这个注解可以确保 上面的@Autowired注解完成了依赖注入 之后才执行这个方法
    // 这个时候 myRouteWriter对象才有值，否则 当 这个RouteNacos类的构造方法被执行时 myRouteWriter依赖还没被注入值呢！

    //    核心原因：Spring 创建 Bean 对象是分两步走的
    //    第一步：实例化（new对象）→ 调用构造方法
    //    第二步：依赖注入（给字段赋值）→ 处理@Autowired

    // 一句话：@Autowired 字段注入是在对象 new 出来之后，通过反射额外赋值的，所以构造方法里拿不到
    public void dynamicRoute() {

        try{
            // 1 连接 Nacos，用Nacos提供的API 构造 Nacos Config Service
            ConfigService configService = NacosFactory.createConfigService(NACOS_SERVER_ADDR);
            // 2 加载 Nacos中已有的路由配置信息，初始化路由配置
            initRoute(configService);
            // 3 设置 Nacos监听，路由配置变动之后更新本地配置
            configService.addListener(NACOS_DATA_ID, NACOS_DATA_GROUP, new NacosRouteListener());

        }catch (Exception e) {
            e.printStackTrace();
        }
    }

    private void initRoute(ConfigService configService) throws Exception {
        String config = configService.getConfig(NACOS_DATA_ID, NACOS_DATA_GROUP, 5000);
        System.out.println("---route config: " + config);
        if (config == null || config.trim().isEmpty()) {
            System.out.println("---route config is empty, skip init");
            return;
        }
        RouteDefinition routeDefinition = JSON.parseObject(config, RouteDefinition.class);
        myRouteWriter.add(routeDefinition);
    }
    // 自定义Nacos监听器
    class NacosRouteListener implements Listener {

        @Override
        public Executor getExecutor() {
            return null;
        }

        @Override
        public void receiveConfigInfo(String configInfo) {
            System.out.println("---route change: " + configInfo);
            RouteDefinition routeDefinition = JSON.parseObject(configInfo, RouteDefinition.class);
            myRouteWriter.update(routeDefinition);
        }
    }
}
