
#/opt/MegaRAID/storcli/storcli64   show J

from .collector import Fetcher, MetricCollector, Collector, PD_STATES, VD_STATES

class MegaraidError(Exception):
    pass

class Controller:

    def __init__(self, id):
        self.id = id
        self.disks = []
        self.virtual_drives = []

    def __str__(self):
        s = "Controller {}\n".format(self.id)
        s += "Virtual Drives\n"
        for v in self.virtual_drives:
            s += "- {}\n".format(v)
        s += "Disks:\n"
        for d in self.disks:
            s += " - {}\n".format(d)
        return s

class PhysicalDisk:

    STATES = {
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

    def __init__(self, data):
        eid = None
        slot = None
        if "EID:Slt" in data:
            eid, slot = data["EID:Slt"].split(':')
        self.enclosure = eid
        self.slot = slot
        self.device_id = data.get('DID')
        self.drive_group = data.get('DG')
        self.interface = data.get('Intf')
        self.media_type  = data.get('Med')
        self.type = data.get('Type')
        state = data.get('State')
        self.state = PD_STATES.get(state, state)
        self.size = data.get('Size')
        self.self_encryptive_drive = data.get('SED')
        self.sector_size = data.get('SeSz')
        self.pi_eligible = data.get('PI')
    
    def __str__(self):
        return "{eid}/{slot} {did} {media}/{interface} State={state} Size={size}".format(
                        eid=self.enclosure, 
                        slot=self.slot, 
                        did=self.device_id, 
                        media=self.media_type,
                        interface=self.interface,
                        state=self.state, 
                        size=self.size
                    )

class VirtualDrive:
   
    def __init__(self, data):
        ref = data['DG/VD']
        dg, vd = ref.split('/')
        self.drive_group = dg
        self.virtual_drive = vd
        self.type = data['TYPE']
        state = data["State"]
        self.state = VD_STATES.get(state, state)
        self.access = data['Access']
        self.consist = data['Consist'] == "Yes"
        self.cache = data['Cache']
        self.name = data['Name']
        self.scheduled_check = data['sCC']
        self.size = data['Size']  
        self.cachecade = data['Cac']
    
    def __str__(self):
        return "{dg}/{vd} {type} Name={name} State={state} Access={access} Consistent={consist} Size={size}".format(
                    dg=self.drive_group, 
                    vd=self.virtual_drive, 
                    type=self.type, 
                    name=self.name, 
                    state=self.state, 
                    access=self.access, 
                    consist=self.consist, 
                    size=self.size
                )

class ControllerCollector(Collector):

    def __init__(self):
        self.controllers = {}

    def get_controller(self, cid):
        if not cid in self.controllers:
            self.controllers[cid] = Controller(cid)
        return self.controllers[cid]

    def add_virtual_drive(self, c_id, data):
        c = self.get_controller(c_id)
        vd = VirtualDrive(data)
        c.virtual_drives.append(vd)
    
    def add_dg_drive(self, c_id, data):
        c = self.get_controller(c_id)
        vd = PhysicalDisk(data)
        c.disks.append(vd)

    def __str__(self):
        s = ""
        for idx, c in self.controllers.items():
            s += str(c)
        return s

class CompositeCollector(Collector):

    def __init__(self):
        self.metrics = MetricCollector()
        self.details = ControllerCollector()

    def add_virtual_drive(self, c_id, data):
        self.metrics.add_virtual_drive(c_id, data)
        self.details.add_virtual_drive(c_id, data)
    
    def add_dg_drive(self, c_id, data):
        self.metrics.add_dg_drive(c_id, data)
        self.details.add_dg_drive(c_id, data)
    
if __name__ == '__main__':
    fetcher = Fetcher()
    collector = CompositeCollector()
    fetcher.read_disks(collector)
    print(collector.metrics.collect())
    print(collector.details)