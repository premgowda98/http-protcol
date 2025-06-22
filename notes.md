## Problem Statement

1. When client agent is running, both http and https proxy is enabled.
2. During this period, if you visit any browser and access site like `http://192.168.0.115:8000` you get 404 `Nothing matches uri`
3. To test in curl `curl -x http://localhost:58080 http://192.168.0.115:8000`

## Tech understanding

1. HTTP Proxies and URI Forms
   1. When a browser (or any HTTP client) detects an HTTP proxy, it changes the format of its requests:
   2. With proxy `GET http://example.com/some-path HTTP/1.1` (This is called absolute-form)
   3. Without proxy (direct request) `GET /some-path HTTP/1.1` (This is called origin-form)
2. By default browser and curl uses http1.1 for http requests
3.  How does browser know which protocol to use?
    1.  For HTTPS request ALPN (Application-Layer Protocol Negotiation) is used to determine the protocol.
        1.  The server responds with the protocol it supports, and the client uses that to establish a secure connection.
        2.  Can be see in wireshark, with example filter `tls.handshake.extensions_server_name == "example.com" || ip.addr==96.7.128.175`
            1.  Here look at client hello message, it will have `application_layer_protocol_negotiation` extension
    2.  For HTTP request the client, if cleints want a http2 connection it sends something like **prior knowledge**
        1. If server does not 