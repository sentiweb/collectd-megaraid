import collectd

from .collector import MetricCollector, Fetcher

class CollectdPlugin:

    def init(self):
        self.plugin_name = 'megaraid'
        self.verbose_logging = False
        self.interval = 28800
        self.fetcher = Fetcher()
    
    def log_verbose(self, msg):
        if not self.verbose_logging:
            return
        collectd.info('%s plugin [verbose]: %s' % (self.plugin_name, msg))
   
    def store(self, key, value, plugin_instance=None):
        if value != '':
            box = collectd.Values(type='gauge', plugin=self.plugin_name, type_instance=key, values=[value], plugin_instance=plugin_instance)
            box.dispatch()
            self.log_verbose('Sending value: %s:%s' % (key, value))
        else:
            self.log_verbose('Ignore empty value: %s:%s' % (key, value))

    def read(self):
        try:
            collector = MetricCollector()
            self.fetcher.read_disks(collector)
            for m in collector.collect():
                self.store(m[0], m[2], plugin_instance=m[1])
        except Exception e:
            collectd.info("{} plugin : error reading disks info {}".format(self.plugin_name, e))
    
    def configure_callback(self, conf):
        for node in conf.children:
            vals = [str(v) for v in node.values]
            if node.key == 'Verbose':
                self.verbose_logging = (vals[0].lower() == 'true')
            elif node.key == 'Interval':
                self.interval = float(vals[0])
            else:
                raise ValueError('%s plugin: Unknown config key: %s' % (self.plugin_name, node.key))
        collectd.register_read(self.read, self.interval)
        self.log_verbose('configured with interval=%s' % self.interval)

plugin = CollectdPlugin()
collectd.register_config(plugin.configure_callback)

