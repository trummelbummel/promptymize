from __future__ import annotations

import argparse
import json
import logging
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from auto_prompt.rest_api import RestApiService

logger = logging.getLogger(__name__)


def _build_service(context_path_arg: str | None) -> RestApiService:
    context_path = Path(context_path_arg).expanduser() if context_path_arg else None
    logger.info("Initializing REST backend service (context_path=%s)", context_path)
    return RestApiService(context_path=context_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run lightweight REST backend for local UI development.")
    parser.add_argument("--host", default="127.0.0.1", help="Bind host (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Bind port (default: 8000)")
    parser.add_argument(
        "--context-path",
        default=None,
        help="Optional path to prompt_methods_context.csv for agent/scoring routes.",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    service = _build_service(args.context_path)

    class Handler(BaseHTTPRequestHandler):
        def _send_json(self, status: int, payload: dict[str, Any]) -> None:
            body = json.dumps(payload).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.end_headers()
            self.wfile.write(body)

        def do_OPTIONS(self) -> None:  # noqa: N802
            self.send_response(HTTPStatus.NO_CONTENT)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.end_headers()

        def do_GET(self) -> None:  # noqa: N802
            if self.path == "/health":
                self._send_json(HTTPStatus.OK, {"status": "ok"})
                return
            status, payload = service.handle(method="GET", path=self.path, body={})
            self._send_json(status, payload)

        def do_POST(self) -> None:  # noqa: N802
            length = int(self.headers.get("Content-Length", "0"))
            body_raw = self.rfile.read(length) if length > 0 else b"{}"
            try:
                body = json.loads(body_raw.decode("utf-8")) if body_raw else {}
            except json.JSONDecodeError:
                self._send_json(HTTPStatus.BAD_REQUEST, {"error_code": "INVALID_JSON", "message": "Invalid JSON body."})
                return

            status, payload = service.handle(method="POST", path=self.path, body=body)
            self._send_json(status, payload)

    server = ThreadingHTTPServer((args.host, args.port), Handler)
    logger.info("Backend listening on http://%s:%d", args.host, args.port)
    server.serve_forever()


if __name__ == "__main__":
    main()

