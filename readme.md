
## Virtual Disk

{
    "DG/VD" : "0/0",
    "TYPE" : "RAID1",
    "State" : "Optl",
    "Access" : "RW",
    "Consist" : "Yes",
    "Cache" : "RWBD",
    "Cac" : "-",
    "sCC" : "OFF",
    "Size" : "278.875 GB",
    "Name" : "OS"
} 

State: OfLn=OffLine|Pdgd=Partially Degraded|Dgrd=Degraded|Optl=Optimal
Access: RO=Read Only|RW=Read Write|HD=Hidden|TRANS=TransportReady|B=Blocked

VD=Virtual Drive| DG=Drive Group|Rec=Recovery
Cac=CacheCade|Rec=Recovery||dflt=Default||Consist=Consistent|R=Read Ahead Always|NR=No Read Ahead|WB=WriteBack
FWB=Force WriteBack|WT=WriteThrough|C=Cached IO|D=Direct IO|sCC=Scheduled
Check Consistency


virtual-drive-config-schema.json
"properties": {
    "DG/VD" : {"type": "string", "pattern": "^(\\d{1}|\\d{2})/(\\d{1}|\\d{2}|\\d{3})$" },
    "TYPE" : { "type": "string", "pattern": "^((RAID(\\d{1}|\\d{2}))|(NytroCache(\\d{1}|\\d{2}))|(Cac(\\d{1}|\\d{2}))| (Rec(\\d{1}|\\d{2}))|(Nytro(\\d{1}|\\d{2})))$" },
    "State" : {"type": "string", "enum": ["OfLn", "Pdgd", "Dgrd", "Optl"]},
    "Access" : {"type": "string", "enum": ["B", "RO", "HD", "TRANS", "RW"]},
    "Consist" : {"type": "string", "enum": ["Yes", "No"]},
    "Cache" : {"type": "string", "pattern": "^((R|NR)(FWB|AWB|WB|WT)(C|D))$"},
    "Cac" : {"type": "string", "enum": ["RW", "R", "-"]},
    "sCC" : {"type": "string", "enum": ["ON", "OFF", "-"]},
    "Size" : { "$ref": "common-schema.json#/definitions/size" },
    "Name" : {"type": "string"}
}

## Physical Disk

EID=Enclosure Device ID|Slt=Slot No|DID=Device ID|DG=DriveGroup
DHS=Dedicated Hot Spare|UGood=Unconfigured Good|GHS=Global Hotspare
UBad=Unconfigured Bad|Sntze=Sanitize|Onln=Online|Offln=Offline|Intf=Interface
Med=Media Type|SED=Self Encryptive Drive|PI=PI Eligible
SeSz=Sector Size|Sp=Spun|U=Up|D=Down|T=Transition|F=Foreign
UGUnsp=UGood Unsupported|UGShld=UGood shielded|HSPShld=Hotspare shielded
CFShld=Configured shielded|Cpybck=CopyBack|CBShld=Copyback Shielded
UBUnsp=UBad Unsupported|Rbld=Rebuild

# enclosure-drive-schema.json
"EID:Slt" : {
    "oneOf": [
        { "type": "string", "pattern": "^(((\\d{1}|\\d{2}|\\d{3}):(\\d{1}|\\d{2}|\\d{3}))|-)$"},
        { "type": "string", "pattern": "^(( :(\\d{1}|\\d{2}|\\d{3}))|-)$"}
    ]
},				
"DID" : {
    "oneOf": [
        {"type": "number", "minimum": 0},
        {"type": "string", "pattern": "^-$"}
    ]
},
"State" : { "$ref": "common-schema.json#/definitions/drive-state" },
"DG" : {
    "oneOf": [
        {"type": "number", "minimum": 0},
        {"type": "string", "pattern": "^-|F$"}
    ]
},
"Size" : { "$ref": "common-schema.json#/definitions/size" },
"Intf" : {"type": "string", "enum": ["Parallel SCSI", "SAS", "SATA", "FC", "NVMe", "Unknown"] },
"Med" : {"type": "string", "enum": ["SSD", "HDD", "NytroSFM", "Nytro Flash", "DFF", "TAPE", "Unknown"] },
"SED" : {"type": "string", "enum": ["Y", "N"]},
"PI" : {"type": "string", "enum": ["Y", "N"]},
"SeSz" : { "$ref": "common-schema.json#/definitions/size" },
"Model" : {"type": "string"},
"Sp" : {"type": "string", "enum": ["U", "T", "D", "-"]},
"Type" : {"type": "string", "enum":["EPD", "JBOD", "-"] }

Drive state
"drive-state": {
             "type": "string",
             "enum": [ "UGood", "UBad", "HSP", "Offln", "Onln", "Rbld", "Failed", "Cpybck", "JBOD",
                       "GHS", "DHS", "UGUnsp", "UGShld", "HSPShld", "CFShld", "CBShld", "-", "Offline", "Online", "Missing", "UBUnsp" ] 
        }