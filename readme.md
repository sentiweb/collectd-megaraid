# Collectd MegaRaid

Collect megaRAID disk state using storcli utility

## Usage

Default Path for storcli utility is /opt/MegaRAID/storcli/storcli64

To test the data extraction, the python script megaraid can be run.

It will output the metrics computed for collected and more detailled info about the disks

```bash
python -m collectd_megaraid.megaraid
```

## Configuration

To use with collectd you need collectd-python plugins

```
LoadPlugin python
<Plugin python>
    # Path where python module is located (if cloned, working copy path)
    ModulePath "/opt/collectd/collectd-megaraid"
    LogTraces true
    Interactive false
    Import "collectd_megaraid.collectd_plugin"
   <Module megaraid>
     Verbose True
     # StorCliPath "/path/to/storcli/bin"
   </Module>
</Plugin>
```