import logging, sys
from config import settings
from http.server import HTTPServer
from metrics import Metrics
from prometheus_client import MetricsHandler

log = logging.getLogger("logger")
log.setLevel(settings.get("LOGLEVEL", "INFO"))
log.addHandler(logging.StreamHandler(sys.stderr))

class HttpHandler(MetricsHandler):

    try:
        metrics = Metrics()
    except Exception as e:
        log.error("Metrics initialization failed")
        raise e

    def do_GET(self):
        if self.path == "/metrics":
            self.metrics.refresh_metrics()
            super().do_GET()
        else:
            self.send_error(404)

if __name__ == "__main__":
    log.info(f"Starting web server at port {settings.get('WEB_PORT', 8080)}")
    HTTPServer(("0.0.0.0", settings.get("WEB_PORT", 8080)), HttpHandler).serve_forever()
