FROM golang:latest
WORKDIR /app
COPY src/ .
RUN go build -o middleware .
RUN chmod +x middleware
EXPOSE 8080
CMD ["./middleware"]