## HTTP Server

1. To generate certificate

```bash
openssl req -x509 -newkey rsa:2048 -nodes \
  -keyout key.pem -out cert.pem -days 365 \
  -subj "/CN=192.168.0.110" \
  -addext "subjectAltName=IP:192.168.0.110"
```

### Test with curl

```bash
curl -v http://192.168.0.110:8080
curl -vk --http2 http://192.168.0.110:8080 --cacert cet.pem
curl -vk --http1.1 http://192.168.0.110:8080 --cacert cet.pem
```

| Agent Type           | Default HTTP Version                        |
| -------------------- | ------------------------------------------- |
| Modern Browsers      | **HTTP/2 or HTTP/1.1**                      |
| `curl`               | **HTTP/1.1** (unless overridden)            |
| Python `http.server` | **HTTP/1.0** (by default unless overridden) |
| Legacy Tools         | May use **HTTP/1.0**                        |


## Scenarios

Wireshark filter => `ip.src == 192.168.0.115 && ip.dst == 192.168.0.110` 

### Just HTTP without TLS

1. `python app.py`
2. `curl -v http://192.168.0.110:8080` from some other system
```bash
    *   Trying 192.168.0.110:8080...
    * Connected to 192.168.0.110 (192.168.0.110) port 8080
    > GET / HTTP/1.1
    > Host: 192.168.0.110:8080
    > User-Agent: curl/8.5.0
    > Accept: */*
    > 
    < HTTP/1.1 200 OK
    < date: Sun, 22 Jun 2025 15:00:06 GMT
    < server: uvicorn
    < content-length: 30
    < content-type: application/json
    < 
    * Connection #0 to host 192.168.0.110 left intact
    {"message":"Hello from root!"}(http-protcol) 
```
3. In wireshark everything is working fine.

### HTTP with TLS (Supporting HTTP/1.1) and HTTP/1.1 request

1. Copy the cert file to vm or system from where you send request
2. If the client sends ALNP protocol, and if server doesnot support it, the client will fall back to http/1.1
3. Fastapi with uvicron does not support this
4. `python app.py`
5. `curl -vk --http1.1 https://192.168.0.110:8443`
```bash
curl -vk --http1.1 https://192.168.0.110:8443
Note: Using embedded CA bundle (222971 bytes)
Note: Using embedded CA bundle, for proxies (222971 bytes)
*   Trying 192.168.0.110:8443...
* ALPN: curl offers http/1.1
* TLSv1.3 (OUT), TLS handshake, Client hello (1):
* TLSv1.3 (IN), TLS handshake, Server hello (2):
* TLSv1.3 (IN), TLS handshake, Unknown (8):
* TLSv1.3 (IN), TLS handshake, Certificate (11):
* TLSv1.3 (IN), TLS handshake, CERT verify (15):
* TLSv1.3 (IN), TLS handshake, Finished (20):
* TLSv1.3 (OUT), TLS handshake, Finished (20):
* SSL connection using TLSv1.3 / TLS_AES_256_GCM_SHA384 / [blank] / UNDEF
* ALPN: server accepted http/1.1
* Server certificate:
*  subject: CN=192.168.0.110
*  start date: Jun 22 14:49:25 2025 GMT
*  expire date: Jun 22 14:49:25 2026 GMT
*  issuer: CN=192.168.0.110
*  SSL certificate verify result: self signed certificate (18), continuing anyway.
*   Certificate level 0: Public key type ? (2048/112 Bits/secBits), signed using sha256WithRSAEncryption
* Connected to 192.168.0.110 (192.168.0.110) port 8443
* using HTTP/1.x
> GET / HTTP/1.1
> Host: 192.168.0.110:8443
> User-Agent: curl/8.14.1
> Accept: */*
>
* Request completely sent off
< HTTP/1.1 200
< content-length: 30
< content-type: application/json
< date: Sun, 22 Jun 2025 16:32:01 GMT
< server: hypercorn-h11
<
{"message":"Hello from root!"}* Connection #0 to host 192.168.0.110 left intact
```
### HTTP with TLS (Supporting HTTP/1.1) and HTTP2 request

1. Curl sends both http1.1 and 2 if http2 is set
2. Server accepts 1.1 and connection sis established
```bash
curl -vk --http1.1 https://192.168.0.110:8443
Note: Using embedded CA bundle (222971 bytes)
Note: Using embedded CA bundle, for proxies (222971 bytes)
*   Trying 192.168.0.110:8443...
* ALPN: curl offers http/1.1
* TLSv1.3 (OUT), TLS handshake, Client hello (1):
* TLSv1.3 (IN), TLS handshake, Server hello (2):
* TLSv1.3 (IN), TLS handshake, Unknown (8):
* TLSv1.3 (IN), TLS handshake, Certificate (11):
* TLSv1.3 (IN), TLS handshake, CERT verify (15):
* TLSv1.3 (IN), TLS handshake, Finished (20):
* TLSv1.3 (OUT), TLS handshake, Finished (20):
* SSL connection using TLSv1.3 / TLS_AES_256_GCM_SHA384 / [blank] / UNDEF
* ALPN: server did not agree on a protocol. Uses default.
* Server certificate:
*  subject: CN=192.168.0.110
*  start date: Jun 22 14:49:25 2025 GMT
*  expire date: Jun 22 14:49:25 2026 GMT
*  issuer: CN=192.168.0.110
*  SSL certificate verify result: self signed certificate (18), continuing anyway.
*   Certificate level 0: Public key type ? (2048/112 Bits/secBits), signed using sha256WithRSAEncryption
* Connected to 192.168.0.110 (192.168.0.110) port 8443
* using HTTP/1.x
> GET / HTTP/1.1
> Host: 192.168.0.110:8443
> User-Agent: curl/8.14.1
> Accept: */*
>
* Request completely sent off
< HTTP/1.1 200
< content-length: 30
< content-type: application/json
< date: Sun, 22 Jun 2025 16:39:06 GMT
< server: hypercorn-h11
<
{"message":"Hello from root!"}* Connection #0 to host 192.168.0.110 left intact
```

### HTTP with TLS (Supporting HTTP2) and HTTP/1.1 request

1. Curl sends http/1.1, but server has only h2
2. Server will not agress, and curl witches to default http/1.1
```bash
curl -vk --http2 https://192.168.0.110:8443
Note: Using embedded CA bundle (222971 bytes)
Note: Using embedded CA bundle, for proxies (222971 bytes)
*   Trying 192.168.0.110:8443...
* ALPN: curl offers h2,http/1.1
* TLSv1.3 (OUT), TLS handshake, Client hello (1):
* TLSv1.3 (IN), TLS handshake, Server hello (2):
* TLSv1.3 (IN), TLS handshake, Unknown (8):
* TLSv1.3 (IN), TLS handshake, Certificate (11):
* TLSv1.3 (IN), TLS handshake, CERT verify (15):
* TLSv1.3 (IN), TLS handshake, Finished (20):
* TLSv1.3 (OUT), TLS handshake, Finished (20):
* SSL connection using TLSv1.3 / TLS_AES_256_GCM_SHA384 / [blank] / UNDEF
* ALPN: server accepted http/1.1
* Server certificate:
*  subject: CN=192.168.0.110
*  start date: Jun 22 14:49:25 2025 GMT
*  expire date: Jun 22 14:49:25 2026 GMT
*  issuer: CN=192.168.0.110
*  SSL certificate verify result: self signed certificate (18), continuing anyway.
*   Certificate level 0: Public key type ? (2048/112 Bits/secBits), signed using sha256WithRSAEncryption
* Connected to 192.168.0.110 (192.168.0.110) port 8443
* using HTTP/1.x
> GET / HTTP/1.1
> Host: 192.168.0.110:8443
> User-Agent: curl/8.14.1
> Accept: */*
>
* Request completely sent off
< HTTP/1.1 200
< content-length: 30
< content-type: application/json
< date: Sun, 22 Jun 2025 16:34:20 GMT
< server: hypercorn-h11
<
{"message":"Hello from root!"}* Connection #0 to host 192.168.0.110 left intact
```



### HTTP with TLS (Supporting HTTP2) and HTTP2 request

```bash
curl -vk --http2 https://192.168.0.110:8443
Note: Using embedded CA bundle (222971 bytes)
Note: Using embedded CA bundle, for proxies (222971 bytes)
*   Trying 192.168.0.110:8443...
* ALPN: curl offers h2,http/1.1
* TLSv1.3 (OUT), TLS handshake, Client hello (1):
* TLSv1.3 (IN), TLS handshake, Server hello (2):
* TLSv1.3 (IN), TLS handshake, Unknown (8):
* TLSv1.3 (IN), TLS handshake, Certificate (11):
* TLSv1.3 (IN), TLS handshake, CERT verify (15):
* TLSv1.3 (IN), TLS handshake, Finished (20):
* TLSv1.3 (OUT), TLS handshake, Finished (20):
* SSL connection using TLSv1.3 / TLS_AES_256_GCM_SHA384 / [blank] / UNDEF
* ALPN: server accepted h2
* Server certificate:
*  subject: CN=192.168.0.110
*  start date: Jun 22 14:49:25 2025 GMT
*  expire date: Jun 22 14:49:25 2026 GMT
*  issuer: CN=192.168.0.110
*  SSL certificate verify result: self signed certificate (18), continuing anyway.
*   Certificate level 0: Public key type ? (2048/112 Bits/secBits), signed using sha256WithRSAEncryption
* Connected to 192.168.0.110 (192.168.0.110) port 8443
* using HTTP/2
* [HTTP/2] [1] OPENED stream for https://192.168.0.110:8443/
* [HTTP/2] [1] [:method: GET]
* [HTTP/2] [1] [:scheme: https]
* [HTTP/2] [1] [:authority: 192.168.0.110:8443]
* [HTTP/2] [1] [:path: /]
* [HTTP/2] [1] [user-agent: curl/8.14.1]
* [HTTP/2] [1] [accept: */*]
> GET / HTTP/2
> Host: 192.168.0.110:8443
> User-Agent: curl/8.14.1
> Accept: */*
>
* Request completely sent off
< HTTP/2 200
< content-length: 30
< content-type: application/json
< date: Sun, 22 Jun 2025 16:40:40 GMT
< server: hypercorn-h2
<
{"message":"Hello from root!"}* Connection #0 to host 192.168.0.110 left intact
```
