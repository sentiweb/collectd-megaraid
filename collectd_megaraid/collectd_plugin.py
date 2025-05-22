import collectd

from .collector import MetricCollector, Fetcher

PLUGIN_NAME = 'megaraid'

class Config:

    def __init__(self):
        self.verbose = False
        self.fetcher = Fetcher()

    def set(self, key, values):
        if key == 'verbose':
            self.verbose = (vals[0].lower() == 'true')
            return True
        if key == 'storclipath':
            self.fetcher.storcli_bin = vals[0]
            return True
        return False

CONFIG = Config()

def log_verbose(msg):
    if not CONFIG.verbose:
        return
    collectd.info('%s plugin [verbose]: %s' % (PLUGIN_NAME, msg))
   
def store(key, value, plugin_instance=None):
    if value != '':
        box = collectd.Values(type='gauge', plugin=PLUGIN_NAME, type_instance=key, values=[value], plugin_instance=plugin_instance)
        box.dispatch()
        log_verbose('Sending value: %s:%s' % (key, value))
    else:
        log_verbose('Ignore empty value: %s:%s' % (key, value))

def read():
    try:
        collector = MetricCollector()
        CONFIG.fetcher.read_disks(collector)
        for m in collector.collect():
            store(m[0], m[2], plugin_instance=str(m[1]))
    except Exception as e:
        collectd.info("{} plugin : error reading disks info {}".format(PLUGIN_NAME, e))
    
def configure(conf):
    for node in conf.children:
        vals = [str(v) for v in node.values]
        key = node.key.lower()
        if not CONFIG.set(key, vals):
            raise ValueError('%s plugin: Unknown config key: %s' % (PLUGIN_NAME, node.key))
    log_verbose('configured')

collectd.register_config(configure)
collectd.register_read(read)

