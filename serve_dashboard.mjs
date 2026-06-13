import { createServer } from "node:http";
import { readFile } from "node:fs/promises";
import { extname, join, normalize } from "node:path";
import { fileURLToPath } from "node:url";

const root = fileURLToPath(new URL(".", import.meta.url));
const port = Number(process.env.PORT || 4173);

const types = {
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".csv": "text/csv; charset=utf-8",
  ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
};

createServer(async (req, res) => {
  const url = new URL(req.url || "/", `http://localhost:${port}`);
  const pathname = url.pathname === "/" ? "/mdss_dashboard.html" : url.pathname;
  const target = normalize(join(root, pathname.replace(/^\/+/, "")));

  if (!target.startsWith(root)) {
    res.writeHead(403);
    res.end("Forbidden");
    return;
  }

  try {
    const bytes = await readFile(target);
    res.writeHead(200, { "content-type": types[extname(target)] || "application/octet-stream" });
    res.end(bytes);
  } catch {
    res.writeHead(404);
    res.end("Not found");
  }
}).listen(port, "127.0.0.1", () => {
  console.log(`MDSS dashboard running at http://127.0.0.1:${port}/`);
});
