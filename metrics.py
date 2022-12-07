import logging, sys
from ad import AD
from prometheus_client import Gauge, Info
from urllib.error import HTTPError

log = logging.getLogger("logger")

class Metrics():

    def __init__(self, config):
        self.config = config
        self.gauges = {}
        self.info = {}
        self.update_errors_count = 0

    def clear_metrics(self):
        for gauge in self.gauges.values():
            gauge.clear()
        for inf in self.info.values():
            inf.clear()

    def update_metrics(self):
        for dom in self.config:
            ad = AD(username = dom['username'],
                    password = dom['passwd'],
                    domain = dom['domain'],
                    dc_list = dom['dc_list'],
                    host_port = dom['host_port'],
                    LDAP_Subtree = dom['LDAP_Subtree'],
                    reqLDAPattr = dom['reqLDAPattr'],
                    LDAP_SearchFilter = dom['LDAP_Filter'])
            metrics_data = self.ad.get_realtimestat()
            for resource in metrics_data:
                for metric, data in resource.items():
                    if not metric in self.gauges:
                        self.gauges[metric] = Gauge(metric, metric, ["AccountName"])
                    if isinstance(data, (int, float)):
                        self.gauges[metric].labels(resource["AccountName"]).set(data)
                    elif isinstance(data, list):
                        self.gauges[metric].labels(resource["AccountName"]).info({'description': data[0]})

    def refresh_metrics(self):
        self.clear_metrics()
        try:
            self.update_metrics()
            self.update_errors_count = 0
        except HTTPError as err:
            if self.update_errors_count > 2:
                log.error(f'I can not update metrics. Error "{err}". Bye!')
                sys.exit(1)
            self.update_errors_count += 1
            log.info(f'#{self.update_errors_count} Update metrics error "{err}". I will try to update token and continue')
            self.refresh_metrics()
