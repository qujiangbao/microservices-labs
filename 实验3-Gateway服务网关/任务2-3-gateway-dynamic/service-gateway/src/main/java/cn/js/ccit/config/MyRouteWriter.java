package cn.js.ccit.config;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.cloud.gateway.event.RefreshRoutesEvent;
import org.springframework.cloud.gateway.route.RouteDefinition;
import org.springframework.cloud.gateway.route.RouteDefinitionWriter;
import org.springframework.context.ApplicationEventPublisher;
import org.springframework.context.ApplicationEventPublisherAware;
import org.springframework.stereotype.Service;
import reactor.core.publisher.Mono;

// 访问 http://localhost:8002/actuator/gateway/routes 即可查看 当前网关服务站的路由列表
// 也可以通过该列表验证 服务启动后 是否已经正确加载路由的配置，以及路由配置更新之后  本地路由配置是否也准确地被更新了
@Service
public class MyRouteWriter implements ApplicationEventPublisherAware {

    @Autowired
    private RouteDefinitionWriter routeDefinitionWriter;

    private ApplicationEventPublisher publisher;

    @Override
    public void setApplicationEventPublisher(ApplicationEventPublisher applicationEventPublisher) {
        this.publisher = applicationEventPublisher;
    }

    /**添加路由
     *
     * @param definition 路由配置信息
     */
    public void add(RouteDefinition definition) {
        routeDefinitionWriter.save(Mono.just(definition)).block();
        this.publisher.publishEvent(new RefreshRoutesEvent(this));
    }


    /**更新路由
     *
     * @param definition 路由配置信息
     */
    public void update(RouteDefinition definition) {

        try {
            // 根据 routeId 删除现有路由。首次下发时路由还不存在，忽略 NotFound。
            // delete/save 返回的是 Mono，必须等它执行完再刷新，否则路由列表仍是旧的。
            this.routeDefinitionWriter.delete(Mono.just(definition.getId()))
                    .onErrorResume(e -> Mono.empty())
                    .then(this.routeDefinitionWriter.save(Mono.just(definition)))
                    .block();
            this.publisher.publishEvent(new RefreshRoutesEvent(this));
        }catch (Exception e) {
            e.printStackTrace();
        }
    }
}
