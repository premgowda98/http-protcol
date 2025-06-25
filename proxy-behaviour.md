## Proxy

If any proxy does not implement RFC 7230 5.3.2, there will be issues in processing requests

1. IN HTTP with TLS there are no issues with http/1.1 and h2 irrespective of what server has
2. But in case of http requests, when passed through proxy, the request will be processed as http/1.1
   1. Since http2 is not supported on http request
   2. Now here, the proxy should re2rite the absolute-form to origin-form
   3. If the proxy does not do this, then the request will fail, Nothing Matches URI or like detail not found
3. It is not necessary that proxy has to rewrite, but according to RFC 7390 A server must accept the absolute-form request
   1. If the server does not accept absolute-form request, then it is a bug in the server
4. Here even a proxy is a server for client so it should rewrite the absolute-form to origin-form

### Why does HTTPS(s) does not have this issue of absolute-form?

## 🌐 1. HTTP Without TLS (Plain HTTP)

* When a client (like a browser) talks to a proxy over **plain HTTP**, it sends:

  ```
  GET http://example.com/path HTTP/1.1
  Host: example.com
  ```

  → This is called **absolute-form** (includes scheme and host in the path).

* The proxy reads this full request and either:

  * Forwards it as-is to the destination (if it's a forward proxy)
  * Or rewrites it to **origin-form**:

    ```
    GET /path HTTP/1.1
    Host: example.com
    ```

* But many lightweight origin servers (e.g. FastAPI, Go stdlib) do **not accept absolute-form** unless explicitly handled.

---

## 🔐 2. HTTPS (HTTP Over TLS)

* HTTPS encrypts all HTTP content, including paths and headers.
* A proxy cannot simply forward this — because it can’t read or modify encrypted traffic.
* So browsers use the **`CONNECT` method**:

### 🔁 CONNECT Flow:

1. **Client to Proxy**:

   ```
   CONNECT example.com:443 HTTP/1.1
   Host: example.com:443
   ```

2. **Proxy Response**:

   ```
   HTTP/1.1 200 Connection Established
   ```

3. Now the client and server perform a **TLS handshake** through the proxy (the proxy just tunnels TCP).

4. Inside this tunnel, the client sends:

   ```
   GET /path HTTP/2
   Host: example.com
   ```

   → This is **origin-form**, sent securely over TLS.

✅ So the origin server **always sees origin-form** with HTTPS.

---

## 📌 Key Differences

| Feature          | HTTP (No TLS)             | HTTPS (TLS)                 |
| ---------------- | ------------------------- | --------------------------- |
| Request Form     | `absolute-form`           | `origin-form`               |
| Proxy Visibility | Full request (path, body) | Only sees CONNECT           |
| Proxy Role       | Reads & forwards requests | Creates a TCP tunnel        |
| Security         | Unencrypted               | Encrypted (TLS)             |
| `CONNECT` Used?  | ❌ No                      | ✅ Yes                       |
| Server Sees      | Can receive absolute-form | Always receives origin-form |

---

## 🖼️ Diagram

```
                 HTTP (no TLS)                         HTTPS (with TLS)
             ────────────────────────             ────────────────────────────
Browser      GET http://example.com/path          CONNECT example.com:443
             ────────────────────────▶            ──────────────────────▶
                                                  HTTP/1.1 200 OK
Proxy        Reads full HTTP request              ──────────────────────▶
             May forward as-is                    Creates TCP tunnel
             or strip to origin-form              between client ↔ server
             ────────────────────────▶            ◀──────────────────────────
                                                  TLS Handshake
Server       Sees absolute-form (if not rewritten)GET /path HTTP/2
             Must handle or normalize             Inside encrypted tunnel
```

---




```bash
curl -X POST "http://localhost:8080/hello" \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice", "age": 30}'

curl -X POST "http://localhost:8080/upload" \
  -F "file=@/path/to/your/file.txt"
```