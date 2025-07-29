#### SSE (Server sent event)
- Server-Sent Events (SSE) is a simple and efficient way for a server to push real-time updates to the browser over HTTP. 
- It uses a unidirectional channel from server to client — unlike WebSockets (which are bidirectional).
- Uses standard HTTP/1.1 (no special protocol upgrade)
- Client sends a request and keeps the connection open
- Server pushes messages (event:, data:, etc.) continuously
- Works best for live feeds, logs, status updates, etc.
- `pip install fastapi sse-starlette uvicorn`
  - **Run the server**: `uvicorn main:app --reload`  it starts a FASTAPI server and hosts an endpoint  /stream which returns a EventSourceResponse
    - **To Test**: 
      - Just go to browser and hit. `http://127.0.0.1:8000/stream`
      - Or From Js, or form browser console we can use below code to Create a `EventSource` connecting to `http://127.0.0.1:8000/stream`
    ```
    const sse = new EventSource("http://localhost:8000/stream");
    
      sse.onmessage = function(event) {
         console.log("Message:", event.data);
      };

       sse.onerror = function(err) {
           console.error("SSE error:", err);
        };

    ```
