package cn.js.ccit.auth;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.crypto.factory.PasswordEncoderFactories;
import org.springframework.security.oauth2.config.annotation.configurers.ClientDetailsServiceConfigurer;
import org.springframework.security.oauth2.config.annotation.web.configuration.AuthorizationServerConfigurerAdapter;
import org.springframework.security.oauth2.config.annotation.web.configurers.AuthorizationServerEndpointsConfigurer;
import org.springframework.security.oauth2.config.annotation.web.configurers.AuthorizationServerSecurityConfigurer;

@Configuration
public class AuthServerConfig extends AuthorizationServerConfigurerAdapter {
    @Autowired
    private AuthenticationManager authenticationManager;

    @Override
    public void configure(ClientDetailsServiceConfigurer clients) throws Exception {
        // 添加客户端凭证（为方便测试，这里设置四种授权方式）
        clients.inMemory()
                .withClient("client1")
                .secret(PasswordEncoderFactories.createDelegatingPasswordEncoder().encode("123"))
                .authorizedGrantTypes("authorization_code", "implicit", "password", "client_credentials")
                .scopes("test")
                .redirectUris("http://www.baidu.com");
    }

    @Override
    public void configure(AuthorizationServerSecurityConfigurer security) throws Exception {
        // 打开 OAuth 2.0 端点
        security.tokenKeyAccess("permitAll()")
                .checkTokenAccess("isAuthenticated()")
                .allowFormAuthenticationForClients();
    }

    // 使用密码方式，必须重写此方法，并调用授权管理器
    @Override
    public void configure(AuthorizationServerEndpointsConfigurer endpoints) throws Exception {
        endpoints.authenticationManager(authenticationManager);
    }
}
