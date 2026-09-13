FROM rust:1-bookworm AS build
RUN apt-get update && apt-get install -y --no-install-recommends git cmake gcc g++ make pkg-config \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /src
RUN git clone --depth 1 --branch cuni-bank-0.1.0 https://github.com/ceedot-rock/cuni.git /src/cuni \
    && cd /src/cuni && cargo build --release --bin cuni
RUN git clone --depth 1 https://github.com/ceedot-rock/pccx.git /src/pccx \
    && cd /src/pccx && cargo build --release --bin pccx

FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
      ca-certificates python3 golang-go nodejs gcc g++ rustc \
    && rm -rf /var/lib/apt/lists/*
COPY --from=build /src/cuni/target/release/cuni /usr/local/bin/cuni
COPY --from=build /src/pccx/target/release/pccx /usr/local/bin/pccx
WORKDIR /app
COPY .well-known ./.well-known
COPY mcp ./mcp
COPY eval ./eval
COPY receipt.schema.json README.md server.py ./
ENV CUNI_BIN=/usr/local/bin/cuni \
    PCCX_BIN=/usr/local/bin/pccx \
    HOST=0.0.0.0 \
    PORT=8788 \
    PIN_CHECK=v0.1.10 \
    PIN_BANK=cuni-bank-0.1.0 \
    PIN_PCCX=e72528b
EXPOSE 8788
CMD ["python3", "server.py"]
