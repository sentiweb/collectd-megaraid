import collectd
from megaraid_collectd import megaraid

class CollectdPlugin:

    def init(self):
        self.plugin_name = 'megaraid'
        self.verbose_logging = False
        self.interval = 28800
    
    def log_verbose(self, msg):
        if not self.verbose_logging:
            return
        collectd.info('%s plugin [verbose]: %s' % (self.plugin_name, msg))
   
    def store(self, key, val):
        if val != '':
            box = collectd.Values(type='gauge', plugin=self.plugin_name, type_instance=key, values=[val])
            box.dispatch()
            self.log_verbose('Sending value: %s:%s' % (key, val))
        else:
            self.log_verbose('Ignore empty value: %s:%s' % (key, val))
    
    def adpallinfo(self):
        ret = {}
        for line in self.getdata([self.megacli, '-AdpAllInfo', '-aALL', '-NoLog']):
            arr = line.split()
            if len(arr) > 2:
                if arr[0] == 'Degraded':
                    ret['virtual_drives_degraded'] = arr[2]
                elif arr[0] == 'Offline':
                    ret['virtual_drives_offline'] = arr[2]
                elif arr[0] == 'Disks':
                    ret['physical_devices_disks'] = arr[2]
                elif arr[0] == 'Virtual' and arr[1] == 'Drives':
                    ret['virtual_drives'] = arr[3]
                elif arr[0] == 'Physical' and arr[1] == 'Devices':
                    ret['physical_devices'] = arr[3]
                elif arr[0] == 'Critical':
                    ret['physical_devices_critical_disks'] = arr[3]
                elif arr[0] == 'Failed':
                    ret['physical_devices_failed_disks'] = arr[3]
                elif arr[0] == 'Memory':
                    if arr[1] == 'Correctable':
                        ret['memory_correctable_errors'] = arr[4]
                    elif arr[1] == 'Uncorrectable':
                        ret['memory_uncorrectable_errors'] = arr[4]
                elif arr[1] == 'temperature':
                    if arr[0] == 'ROC':
                        ret['temperature_roc'] = arr[3]
                    elif arr[0] == 'Controller':
                        ret['temperature_controller'] = arr[3]
        return ret
    def getbbustatus(self):
        ret = {}
        for line in self.getdata([self.megacli, '-AdpBbuCmd', '-GetBbuStatus', '-aALL', '-NoLog']):
            arr = line.split()
            if len(arr) > 2:
                if arr[0] == 'Voltage:':
                    ret['bbu_voltage'] = arr[1]
                elif arr[0] == 'Current:':
                    ret['bbu_current'] = arr[1]
                elif arr[0] == 'Temperature:':
                    ret['bbu_temperature'] = arr[1]
                elif arr[0] == 'Battery' and arr[1] == 'State:':
                    state = arr[2][0:8]
                    if state in self.bbu_states:
                        ret['bbu_state'] = self.bbu_states[state]
                elif arr[0] == 'Relative' and arr[1] == 'State':
                    ret['bbu_relative_state_of_charge'] = arr[4]
                elif arr[0] == 'Remaining' and arr[1] == 'Capacity:':
                    ret['bbu_remaining_capacity'] = arr[2]
                elif arr[0] == 'Full':
                    ret['bbu_full_charge_capacity'] = arr[3]
        return ret
    def ldinfo(self):
        ret = {}
        for line in self.getdata([self.megacli, '-LDInfo', '-Lall', '-aALL', '-NoLog']):
            arr = line.split()
            if len(arr) > 1:
                if arr[0] == 'Virtual':
                    vd = arr[2]
                elif arr[0] == 'State':
                    state = ' '.join(arr[2:])
                    if state in self.ld_states:
                        ret['vd%sstate' % vd] = self.ld_states[state]
                elif arr[0] == 'Bad':
                    ret['vd%sbad_blocks_exists' % vd] = int(arr[3] != 'No')
        return ret
    def pdlist(self):
        ret = {}
        for line in self.getdata([self.megacli, '-PDList', '-aALL', '-NoLog']):
            arr = line.split()
            if len(arr) > 2:
                if arr[0] == 'Slot':
                    slot = arr[2]
                elif arr[0] == 'Predictive':
                    ret['slot%spredictive_failure' % slot] = arr[3]
                elif arr[0] == 'Shield':
                    ret['slot%sshield' % slot] = arr[2]
                elif arr[0] == 'Firmware':
                    state = ' '.join(arr[2:])
                    if state in self.pd_states:
                        ret['slot%sstate' % slot] = self.pd_states[state]
                elif arr[1] == 'Linkspeed:':
                    if arr[2] in self.pd_linkspeeds:
                        ret['slot%slinkspeed' % slot] = self.pd_linkspeeds[arr[2]]
                elif arr[1] == 'Error':
                    if arr[0] == 'Media':
                        ret['slot%serror_media' % slot] = arr[3]
                    elif arr[0] == 'Other':
                        ret['slot%serror_other' % slot] = arr[3]
                elif arr[1] == 'Temperature':
                    ret['slot%s__temperature' % slot] = arr[2][1:-1]
        return ret
    
    def read(self):
        for key, value in self.adpallinfo().items():
            self.store(key, value)
        for key, value in self.getbbustatus().items():
            self.store(key, value)
        for key, value in self.ldinfo().items():
            self.store(key, value)
        for key, value in self.pdlist().items():
            self.store(key, value)
    
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

