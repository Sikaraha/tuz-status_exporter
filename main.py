import logging, sys, prometheus_client
from config import settings
from http.server import HTTPServer
from metrics import Metrics

conf = settings().read()
log = logging.getLogger("logger")
# log.setLevel(settings.get("LOGLEVEL", "INFO"))
log.setLevel(logging.DEBUG)
log.addHandler(logging.StreamHandler(sys.stderr))
prometheus_client.REGISTRY.unregister(prometheus_client.PROCESS_COLLECTOR)
prometheus_client.REGISTRY.unregister(prometheus_client.PLATFORM_COLLECTOR)
prometheus_client.REGISTRY.unregister(prometheus_client.GC_COLLECTOR)


class HttpHandler(prometheus_client.MetricsHandler):

    try:
        metrics = Metrics(config=conf['MONITIRIONG_OBJ'])
    except Exception as err:
        log.error("Metrics initialization failed")
        raise err

    def do_GET(self):
        if self.path == "/metrics":
            self.metrics.refresh_metrics()
            super().do_GET()
        else:
            self.send_error(404)

if __name__ == "__main__":
    log.info(f"Starting web server at port {conf['EXPORTER_PORT']}")
    HTTPServer(("0.0.0.0", conf['EXPORTER_PORT']), HttpHandler).serve_forever()
