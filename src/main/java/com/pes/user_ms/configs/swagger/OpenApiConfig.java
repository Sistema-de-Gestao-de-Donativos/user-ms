package com.pes.user_ms.configs.swagger;

import io.swagger.v3.oas.annotations.OpenAPIDefinition;
import io.swagger.v3.oas.annotations.info.Info;
import org.springframework.context.annotation.Configuration;

@Configuration
@OpenAPIDefinition(
    info = @Info(
        title = "API de Usuarios",
        version = "1.0.0",
        description = "API para os serviços de usuaro"
))
public class OpenApiConfig {
    // Outras configurações específicas podem ser adicionadas aqui.
}
