// The backend of the demo fixture. No dependencies: `node apps/api/src/server.js`.
const http = require("node:http");

const allowed = ["http://localhost:5173", "http://localhost:5174"];

http
  .createServer((request, response) => {
    const origin = request.headers.origin;
    if (request.url !== "/api/health") {
      response.writeHead(404).end();
    } else if (!allowed.includes(origin)) {
      response.writeHead(403).end(`Origin ${origin} not permitted`);
    } else {
      response.writeHead(200, { "Access-Control-Allow-Origin": origin }).end('{"status":"ok"}');
    }
  })
  .listen(4000, "127.0.0.1");
