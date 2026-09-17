FROM maven:3.9-eclipse-temurin-17-alpine AS builder
WORKDIR /app
COPY pom.xml .
COPY common/pom.xml common/
COPY service-admin/pom.xml service-admin/
COPY service-chat/pom.xml service-chat/
COPY scheduler/pom.xml scheduler/
COPY gateway/pom.xml gateway/
COPY common common
COPY service-admin service-admin
COPY service-chat service-chat
COPY scheduler scheduler
COPY gateway gateway
RUN mvn clean package -DskipTests

FROM eclipse-temurin:17-jre-alpine
WORKDIR /app
COPY --from=builder /app/gateway/target/*.jar app.jar
EXPOSE 8080
ENV JAVA_OPTS="-Xms512m -Xmx1024m"
ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -jar app.jar"]
