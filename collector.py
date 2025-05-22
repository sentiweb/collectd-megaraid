
import subprocess
import json

PD_STATES = {
    "UGood":"unconf_good", 
    "UBad":"unconf_bad", 
    "HSP":"hotspare", 
    "Offln":"offline", 
    "Onln":"online", 
    "Rbld":"rebuild", 
    "Failed":"failed", 
    "GHS":"global_hotspare", 
    "DHS":"dedicated_hotspare", 
}

VD_STATES = {
    "Optl":"optimal",
    "OfLn":"offline",
    "Pdgd":"partial_degraded",
    "Dgrd":"degraded"
}

VD_ACCESS = {
        'RO':'read_only',
        'RW': 'read_write',
        'HD':'hidden',
        'TRANS': 'transport_ready',
        'B':'blocked'
    }


class Collector:

    def add_virtual_drive(self, c_id, data):
        pass
    
    def add_dg_drive(self, c_id, data):
        pass

class StateMetrics:

    def __init__(self, instance):
        self.states = {}
        self.count = 0
        self.instance = instance
    
    def add_state(self, state):
        prev = self.states.get(state, 0)
        self.states[state] = prev + 1
        self.count += 1

    def collect(self, prefix,  o):
        for state, value in self.states.items():
            metric = "{}_{}".format(prefix, state)
            o.append((metric, self.instance, value))
        o.append(( "{}_count".format(prefix), self.instance, value))

class MetricCollector(Collector):

    def __init__(self):
        self.virtuals = {}
        self.drives = {}
    
    def add_virtual_drive(self, c_id, data):
        state = data["State"]
        if not c_id in self.virtuals:
            self.virtuals[c_id] = StateMetrics(c_id)
        m = self.virtuals[c_id]
        if state in VD_STATES:
            state = VD_STATES[state]
            m.add_state(state)
    
    def add_dg_drive(self, c_id, data):
        state = data["State"]
        dg = data["DG"]
        id = "c{}_d{}".format(c_id, dg)
        if not id in self.drives:
            self.drives[id] = StateMetrics(id)
        m = self.drives[id]
        if state in PD_STATES:
            state = PD_STATES.get(state)
            m.add_state(state)    

    def collect(self):
        o = []
        for cid, metrics in self.virtuals.items():
            metrics.collect('virtual_drive', o)
        for cid, metrics in self.drives.items():
            metrics.collect('drive', o)
        return o

class Fetcher:

    def __init__(self, storcli_bin=None):
        if storcli_bin is None:
            self.storcli_bin = "/opt/MegaRAID/storcli/storcli64"
        else:
            self.storcli_bin = storcli_bin

    def fetch(self, args):
        p = subprocess.run(args, capture_output=True)
        data = json.loads(p.stdout)
        return data

    def read_disks(self, collector:Collector, controller='all', disk='all'):
        opts = '/c{}/d{}'.format(controller, disk)
        cmd = [self.storcli_bin, opts, 'show', 'all', 'nolog', 'J' ]
        data = self.fetch(cmd)
        if not isinstance(data, dict):
            raise Exception("data is not a dict")
        if "Controllers" not in data:
            raise Exception("Unable to find 'Controllers entry'")
        for c_index, c_data in enumerate(data['Controllers']):
            c_info = c_data.get("Command Status")
            if c_info is None:
                raise Exception("Unable to find 'Controllers/{}/Command Status'".format(c_index))
            c_id = c_info['Controller']
            r = c_data.get('Response Data')
            # data is in Controllers/{idx}/Response Data/Response Data
            if r is None:
                raise Exception("Unable to find 'Controllers/{}/Response Data'".format(c_index))
            r = r.get('Response Data')
            if r is None:
                raise Exception("Unable to find 'Controllers/{}/Response Data/Response Data'".format(c_index))
            vd_list = r.get('VD LIST')
            if vd_list is not None:
                for vd_idx, vd_data in enumerate(vd_list):
                    try:
                        collector.add_virtual_drive(c_id, vd_data)
                    except Exception as e:
                        print("Error parsing vd {} in controller {}".format(vd_idx, c_index), e)
            dg_list = r.get('DG Drive LIST')
            if dg_list is not None:
                for dg_idx, dg_data in enumerate(dg_list):
                    try:
                        collector.add_dg_drive(c_id, dg_data)
                    except Exception as e:
                        print("Error parsing dg {} in controller {}".format(dg_idx, c_index), e)