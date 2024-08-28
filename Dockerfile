# Etapa de construção
FROM maven:3.8.5-openjdk-17 AS build
WORKDIR /app
COPY . .
RUN mvn clean package -DskipTests

# Etapa de execução
FROM openjdk:17

# Diretório de trabalho dentro do contêiner
WORKDIR /app

# Copie o JAR da sua aplicação para o contêiner (o nome do arquivo JAR pode variar)
COPY --from=build /app/target/user-ms-0.0.1-SNAPSHOT.jar /app/app.jar

# Exponha a porta que a aplicação Spring Boot está usando (por padrão, muitas vezes é 8080)
EXPOSE 8080

# Comando para iniciar a aplicação quando o contêiner for executado
CMD ["java", "-jar", "app.jar"]