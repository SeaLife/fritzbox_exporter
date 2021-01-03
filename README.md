# Fritz!Box exporter for prometheus

![Gitlab pipeline status (self-hosted)](https://img.shields.io/gitlab/pipeline/SeaLife-Docker/fritzbox_exporter/master?gitlab_url=https%3A%2F%2Fgit.r3ktm8.de&style=flat-square)
![Docker Image Version (latest semver)](https://img.shields.io/docker/v/sealife/fritzbox-exporter?sort=semver&style=flat-square&label=docker%20release)
![GitHub release (latest by date including pre-releases)](https://img.shields.io/github/v/release/sealife/fritzbox_exporter?include_prereleases&label=software%20release&style=flat-square)

Simple and straight forward exporter for AVM Fritz!Box metrics. As of now this has tons of assumptions behind it, so it may or may not work against your Fritz!Box. It has been tested against an AVM Fritz!Box 7590 (DSL). If you have another box and data is missing, please file an issue or PR on GitHub.

## Building and running

### Requirements (non-docker)

* Python >=3.6
* fritzconnection >= 0.6.5
* prometheus-client >= 0.6.0

A requirements.txt file is included with the source. Install the requirements using `pip install -r requirements.txt`, preferably inside a virtual environment so your local python packages are not messed up.

### System Service
This exporter can directly be run from a shell.
Set the environment vars as describe in the configuration section of this README and run "python3 -m fritzbox_exporter" from the code directory.
PRs for systemd unit files will gladly be accepted ;-)

### Docker Compose

```yaml
version: '3'
services:
  fritzbox_exporter:
    image: docker.io/sealife/fritzbox-exporter:latest
    restart: unless-stopped
    ports:
      - 8765:8765
    environment:
      FRITZ_HOST: 192.168.178.1 # ip of your Fritz!Box
      FRITZ_USER: monitoring
      FRITZ_PASS: monitoring9987!
```

### Docker
The recommended way to run this exporter is from a docker container.
The included Dockerfile will build the exporter using an python:alpine container using python3.

There are also pre-built images ready at: [sealife/fritzbox-exporter](https://hub.docker.com/repository/docker/sealife/fritzbox-exporter)

To build execute

```docker build -t fritzbox_exporter:latest .```

from inside the source directory.

To run the resulting image use

```docker run -d --name fritzbox_exporter -p <PORT>:<FRITZ_EXPORTER_PORT> -e FRITZ_USER=<YOUR_FRITZ_USER> -e FRITZ_PASS=<YOUR_FRITZ_PASS> fritzbox_exporter:latest```

Verify correct operation:

```curl localhost:<FRITZ_EXPORTER_PORT>/metrics```

```# HELP python_gc_objects_collected_total Objects collected during gc
# TYPE python_gc_objects_collected_total counter
python_gc_objects_collected_total{generation="0"} 481.0
python_gc_objects_collected_total{generation="1"} 112.0
python_gc_objects_collected_total{generation="2"} 0.0
# HELP python_gc_objects_uncollectable_total Uncollectable object found during GC
# TYPE python_gc_objects_uncollectable_total counter
python_gc_objects_uncollectable_total{generation="0"} 0.0
python_gc_objects_uncollectable_total{generation="1"} 0.0
python_gc_objects_uncollectable_total{generation="2"} 0.0
...
```

## Configuration

Configuration is done completely via environment vars.

| Env variable | Description | Default |
|--------------|-------------|---------|
| FRITZ_HOST   | Hostname or IP where the Fritz!Box can be reached. | fritz.box |
| FRITZ_USER   | Username for authentication | none |
| FRITZ_PASS   | Password for authentication | none |
| FRITZ_EXPORTER_PORT | Listening port for the exporter | 8765 |

You can also bind-mount a `settings.json` at `/app/settings.json` to configure multiple Fritz!Box's at once:

```json
[
  {
    "host": "fritz.box",
    "username": "prometheus",
    "password": "prometheus"
  },
  {
    "host": "192.168.178.20",
    "username": "prometheus",
    "password": "prometheus"
  }
]
```

## Metrics

A example output of all metrics with a real Fritz!Box 7590.

```
# HELP python_gc_objects_collected_total Objects collected during gc
# TYPE python_gc_objects_collected_total counter
python_gc_objects_collected_total{generation="0"} 65.0
python_gc_objects_collected_total{generation="1"} 324.0
python_gc_objects_collected_total{generation="2"} 0.0
# HELP python_gc_objects_uncollectable_total Uncollectable object found during GC
# TYPE python_gc_objects_uncollectable_total counter
python_gc_objects_uncollectable_total{generation="0"} 0.0
python_gc_objects_uncollectable_total{generation="1"} 0.0
python_gc_objects_uncollectable_total{generation="2"} 0.0
# HELP python_gc_collections_total Number of times this generation was collected
# TYPE python_gc_collections_total counter
python_gc_collections_total{generation="0"} 70.0
python_gc_collections_total{generation="1"} 6.0
python_gc_collections_total{generation="2"} 0.0
# HELP python_info Python platform information
# TYPE python_info gauge
python_info{implementation="CPython",major="3",minor="8",patchlevel="5",version="3.8.5"} 1.0
# HELP process_virtual_memory_bytes Virtual memory size in bytes.
# TYPE process_virtual_memory_bytes gauge
process_virtual_memory_bytes 2.113536e+07
# HELP process_resident_memory_bytes Resident memory size in bytes.
# TYPE process_resident_memory_bytes gauge
process_resident_memory_bytes 6.934528e+06
# HELP process_start_time_seconds Start time of the process since unix epoch in seconds.
# TYPE process_start_time_seconds gauge
process_start_time_seconds 1.60951066263e+09
# HELP process_cpu_seconds_total Total user and system CPU time spent in seconds.
# TYPE process_cpu_seconds_total counter
process_cpu_seconds_total 2296.11
# HELP process_open_fds Number of open file descriptors.
# TYPE process_open_fds gauge
process_open_fds 7.0
# HELP process_max_fds Maximum number of open file descriptors.
# TYPE process_max_fds gauge
process_max_fds 1.048576e+06
# HELP fritzbox_uptime_total FritzBox uptime, system info in labels
# TYPE fritzbox_uptime_total counter
fritzbox_uptime_total{ModelName="FRITZ!Box 7590 (UI)",Serial="444E6DA5B6DC",SoftwareVersion="154.07.21"} 1.354167e+06
# HELP fritzbox_update_available FritzBox update available
# TYPE fritzbox_update_available gauge
fritzbox_update_available{NewSoftwareVersion="",Serial="444E6DA5B6DC"} 0.0
# HELP fritzbox_lan_status_enabled LAN Interface enabled
# TYPE fritzbox_lan_status_enabled gauge
fritzbox_lan_status_enabled{Serial="444E6DA5B6DC"} 1.0
# HELP fritzbox_lan_status LAN Interface status
# TYPE fritzbox_lan_status gauge
fritzbox_lan_status{Serial="444E6DA5B6DC"} 1.0
# HELP fritzbox_lan_received_bytes_total LAN bytes received
# TYPE fritzbox_lan_received_bytes_total counter
fritzbox_lan_received_bytes_total{Serial="444E6DA5B6DC"} 1.92994792e+08
# HELP fritzbox_lan_transmitted_bytes_total LAN bytes transmitted
# TYPE fritzbox_lan_transmitted_bytes_total counter
fritzbox_lan_transmitted_bytes_total{Serial="444E6DA5B6DC"} 4.03654825e+08
# HELP fritzbox_lan_received_packets_total LAN packets received
# TYPE fritzbox_lan_received_packets_total counter
fritzbox_lan_received_packets_total{Serial="444E6DA5B6DC"} 1.154094e+06
# HELP fritzbox_lan_transmitted_packets_total LAN packets transmitted
# TYPE fritzbox_lan_transmitted_packets_total counter
fritzbox_lan_transmitted_packets_total{Serial="444E6DA5B6DC"} 2.262441e+06
# HELP fritzbox_dsl_status_enabled DSL enabled
# TYPE fritzbox_dsl_status_enabled gauge
fritzbox_dsl_status_enabled{Serial="444E6DA5B6DC"} 1.0
# HELP fritzbox_dsl_status DSL status
# TYPE fritzbox_dsl_status gauge
fritzbox_dsl_status{Serial="444E6DA5B6DC"} 1.0
# HELP fritzbox_dsl_datarate_kbps DSL datarate in kbps
# TYPE fritzbox_dsl_datarate_kbps gauge
fritzbox_dsl_datarate_kbps{Direction="up",Serial="444E6DA5B6DC",Type="curr"} 23357.0
fritzbox_dsl_datarate_kbps{Direction="down",Serial="444E6DA5B6DC",Type="curr"} 124989.0
fritzbox_dsl_datarate_kbps{Direction="up",Serial="444E6DA5B6DC",Type="max"} 48515.0
fritzbox_dsl_datarate_kbps{Direction="down",Serial="444E6DA5B6DC",Type="max"} 192167.0
# HELP fritzbox_internet_online_monitor Online-Monitor stats
# TYPE fritzbox_internet_online_monitor gauge
fritzbox_internet_online_monitor{Direction="up",Serial="444E6DA5B6DC",SyncGroupMode="VDSL",SyncGroupName="sync_dsl"} 2.852375e+06
fritzbox_internet_online_monitor{Direction="down",Serial="444E6DA5B6DC",SyncGroupMode="VDSL",SyncGroupName="sync_dsl"} 1.5264125e+07
# HELP fritzbox_dsl_noise_margin_dB Noise Margin in dB
# TYPE fritzbox_dsl_noise_margin_dB gauge
fritzbox_dsl_noise_margin_dB{Direction="up",Serial="444E6DA5B6DC"} 23.0
fritzbox_dsl_noise_margin_dB{Direction="down",Serial="444E6DA5B6DC"} 18.0
# HELP fritzbox_dsl_attenuation_dB Line attenuation in dB
# TYPE fritzbox_dsl_attenuation_dB gauge
fritzbox_dsl_attenuation_dB{Direction="up",Serial="444E6DA5B6DC"} 15.0
fritzbox_dsl_attenuation_dB{Direction="down",Serial="444E6DA5B6DC"} 19.0
# HELP fritzbox_ppp_connection_uptime PPP connection uptime
# TYPE fritzbox_ppp_connection_uptime gauge
fritzbox_ppp_connection_uptime{Serial="444E6DA5B6DC"} 35563.0
# HELP fritzbox_ppp_conection_state PPP connection state
# TYPE fritzbox_ppp_conection_state gauge
fritzbox_ppp_conection_state{Serial="444E6DA5B6DC",last_error="ERROR_NONE"} 1.0
# HELP fritzbox_wan_data_bytes_total WAN data in bytes
# TYPE fritzbox_wan_data_bytes_total counter
fritzbox_wan_data_bytes_total{Direction="up",Serial="444E6DA5B6DC"} 2.6943626e+08
fritzbox_wan_data_bytes_total{Direction="down",Serial="444E6DA5B6DC"} 4.398142769e+09
# HELP fritzbox_wan_data_packets_total WAN data in packets
# TYPE fritzbox_wan_data_packets_total counter
fritzbox_wan_data_packets_total{Direction="up",Serial="444E6DA5B6DC"} 1.359935e+06
fritzbox_wan_data_packets_total{Direction="down",Serial="444E6DA5B6DC"} 1.093167e+06
# HELP fritzbox_dsl_errors_fec FEC errors
# TYPE fritzbox_dsl_errors_fec gauge
fritzbox_dsl_errors_fec{Serial="444E6DA5B6DC"} 0.0
# HELP fritzbox_dsl_errors_crc CRC Errors
# TYPE fritzbox_dsl_errors_crc gauge
fritzbox_dsl_errors_crc{Serial="444E6DA5B6DC"} 20129.0
# HELP fritzbox_dsl_power_upstream Upstream Power
# TYPE fritzbox_dsl_power_upstream gauge
fritzbox_dsl_power_upstream{Serial="444E6DA5B6DC"} 503.0
# HELP fritzbox_dsl_power_downstream Downstream Power
# TYPE fritzbox_dsl_power_downstream gauge
fritzbox_dsl_power_downstream{Serial="444E6DA5B6DC"} 514.0
```

All `fritzbox_dsl_*` metrics are only available if you'r using [DSL](https://de.wikipedia.org/wiki/Digital_Subscriber_Line).



## Copyright

Copyright 2019 Patrick Dreker <patrick@dreker.de>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
