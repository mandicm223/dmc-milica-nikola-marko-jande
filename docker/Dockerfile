FROM swaggerapi/swagger-ui:latest
ENV PORT=80
COPY swagger.json /app/
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]