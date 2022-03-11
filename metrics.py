import logging, sys
from cdn import CDN
from collections.abc import Iterable
from config import settings
from prometheus_client import Gauge
from urllib.error import HTTPError

log = logging.getLogger("logger")

class Metrics():

    def __init__(self):
        self.cdn = CDN(
                username=settings.get("CDN_USERNAME"),
                password=settings.get("CDN_PASSWORD"),
                account_name=settings.get("CDN_ACCOUNT_NAME"),
                url=settings.get("CDN_URL"))
        self.resources_map = {}
        self.labels_map = {
            "http_status_percent": "code",
            "cache_status_percent_by_requests": "status",
            "cache_status_percent_by_volume": "status"
        }
        self.gauges = {}

        self.update_errors_count = 0
        self.update_resources()

    def update_resources(self):
        for resource in self.cdn.get_resource():
            self.resources_map[resource["id"]] = resource["name"]

    def clear_metrics(self):
        for gauge in self.gauges.values():
            gauge.clear()

    def update_metrics(self):
        metrics_data = self.cdn.get_realtimestat()
        for resource in metrics_data:
            for metric, data in resource.items():
                if not isinstance(data, Iterable):
                    if not metric in self.gauges:
                        self.gauges[metric] = Gauge(metric, metric, ["account", "resource_id", "resource_name"])
                    self.gauges[metric].labels(resource["account"], resource["resource"], self.resources_map[resource["resource"]]).set(data)
                elif not isinstance(data, str):
                    if not metric in self.gauges:
                        self.gauges[metric] = Gauge(metric, metric, ["account", "resource_id", "resource_name", self.labels_map[metric]])
                    for label, value in data.items():
                        self.gauges[metric].labels(resource["account"], resource["resource"], self.resources_map[resource["resource"]], label).set(value)

    def refresh_metrics(self):
        self.clear_metrics()
        try:
            self.update_metrics()
            self.update_errors_count = 0
        except HTTPError as e:
            if self.update_errors_count > 2:
                log.error(f'I can not update metrics. Error "{e}". Bye!')
                sys.exit(1)
            self.update_errors_count += 1
            log.info(f'#{self.update_errors_count} Update metrics error "{e}". I will try to update token and continue')
            self.metrics.cdn._refresh_token()
            self.refresh_metrics()
