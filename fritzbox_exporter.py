# Copyright 2019 Patrick Dreker <patrick@dreker.de>
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#   http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import time
import json
import fritzconnection as fc
import prometheus_client
from prometheus_client.core import GaugeMetricFamily, CounterMetricFamily, REGISTRY


class FritzBoxConnection:
    def __init__(self, host, user, passwd):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.conn = None

    def connect(self):
        self.conn = fc.FritzConnection(address=self.host, user=self.user, password=self.passwd)


class FritzBoxCollector(object):
    def get_fritzbox_list(self):
        boxlist = list()

        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as fh:
                json_config = json.loads(fh.read())

            if json_config is None or type(json_config) is not list:
                raise ValueError("Failed to read json data from configuration")

            for json_entry in json_config:
                boxlist.append(FritzBoxConnection(
                    json_entry['host'],
                    json_entry['username'],
                    json_entry['password'],
                ))

        if os.getenv('FRITZ_USER') is not None and os.getenv('FRITZ_PASS') is not None:
            boxlist.append(FritzBoxConnection(
                os.getenv('FRITZ_HOST', 'fritz.box'),
                os.getenv('FRITZ_USER'),
                os.getenv('FRITZ_PASS')
            ))

        for box in boxlist:
            box.connect()

        return boxlist

    def __init__(self, config_file):
        self.config_file = config_file
        self.boxes = self.get_fritzbox_list()

    def collect(self):
        if len(self.boxes) == 0:
            print("Skipping collect(), no boxes configured!")
            return

        fritzbox_uptime = CounterMetricFamily('fritzbox_uptime', 'FritzBox uptime, system info in labels',
                                              labels=['ModelName', 'SoftwareVersion', 'Serial'])
        fritzbox_update = GaugeMetricFamily('fritzbox_update_available', 'FritzBox update available',
                                            labels=['Serial', 'NewSoftwareVersion'])
        fritzbox_lanenable = GaugeMetricFamily('fritzbox_lan_status_enabled', 'LAN Interface enabled',
                                               labels=['Serial'])
        fritzbox_lanstatus = GaugeMetricFamily('fritzbox_lan_status', 'LAN Interface status', labels=['Serial'])
        fritzbox_lan_brx = CounterMetricFamily('fritzbox_lan_received_bytes', 'LAN bytes received', labels=['Serial'])
        fritzbox_lan_btx = CounterMetricFamily('fritzbox_lan_transmitted_bytes', 'LAN bytes transmitted',
                                               labels=['Serial'])
        fritzbox_lan_prx = CounterMetricFamily('fritzbox_lan_received_packets_total', 'LAN packets received',
                                               labels=['Serial'])
        fritzbox_lan_ptx = CounterMetricFamily('fritzbox_lan_transmitted_packets_total', 'LAN packets transmitted',
                                               labels=['Serial'])
        fritzbox_dsl_enable = GaugeMetricFamily('fritzbox_dsl_status_enabled', 'DSL enabled', labels=['Serial'])
        fritzbox_dsl_status = GaugeMetricFamily('fritzbox_dsl_status', 'DSL status', labels=['Serial'])
        fritzbox_dsl_datarate = GaugeMetricFamily('fritzbox_dsl_datarate_kbps', 'DSL datarate in kbps',
                                                  labels=['Serial', 'Direction', 'Type'])
        fritzbox_dsl_noisemargin = GaugeMetricFamily('fritzbox_dsl_noise_margin_dB', 'Noise Margin in dB',
                                                     labels=['Serial', 'Direction'])
        fritzbox_dsl_attenuation = GaugeMetricFamily('fritzbox_dsl_attenuation_dB', 'Line attenuation in dB',
                                                     labels=['Serial', 'Direction'])
        fritzbox_ppp_uptime = GaugeMetricFamily('fritzbox_ppp_connection_uptime', 'PPP connection uptime',
                                                labels=['Serial'])
        fritzbox_ppp_connected = GaugeMetricFamily('fritzbox_ppp_conection_state', 'PPP connection state',
                                                   labels=['Serial', 'last_error'])
        fritzbox_wan_data = CounterMetricFamily('fritzbox_wan_data_bytes', 'WAN data in bytes',
                                                labels=['Serial', 'Direction'])
        fritzbox_wan_packets = CounterMetricFamily('fritzbox_wan_data_packets', 'WAN data in packets',
                                                   labels=['Serial', 'Direction'])

        for box in self.boxes:
            connection = box.conn
            info_result = connection.call_action('DeviceInfo:1', 'GetInfo')
            fb_serial = info_result['NewSerialNumber']

            # fritzbox_uptime
            fritzbox_uptime.add_metric(
                [info_result['NewModelName'], info_result['NewSoftwareVersion'], fb_serial], info_result['NewUpTime']
            )

            # fritzbox_update_available
            update_result = connection.call_action('UserInterface:1', 'GetInfo')
            upd_available = 1 if update_result['NewUpgradeAvailable'] == '1' else 0
            new_software_version = "n/a" if update_result['NewX_AVM-DE_Version'] is None else update_result[
                'NewX_AVM-DE_Version']

            fritzbox_update.add_metric([fb_serial, new_software_version], upd_available)

            # fritzbox_lan_status_enabled
            lanstatus_result = connection.call_action('LANEthernetInterfaceConfig:1', 'GetInfo')
            fritzbox_lanenable.add_metric([fb_serial], lanstatus_result['NewEnable'])

            # fritzbox_lan_status
            lanstatus = 1 if lanstatus_result['NewStatus'] == 'Up' else 0
            fritzbox_lanstatus.add_metric([fb_serial], lanstatus)

            # fritzbox_lan_received_bytes
            # fritzbox_lan_transmitted_bytes
            # fritzbox_lan_received_packets_total
            # fritzbox_lan_transmitted_packets_total
            lanstats_result = connection.call_action('LANEthernetInterfaceConfig:1', 'GetStatistics')
            fritzbox_lan_brx.add_metric([fb_serial], lanstats_result['NewBytesReceived'])
            fritzbox_lan_btx.add_metric([fb_serial], lanstats_result['NewBytesSent'])
            fritzbox_lan_prx.add_metric([fb_serial], lanstats_result['NewPacketsReceived'])
            fritzbox_lan_ptx.add_metric([fb_serial], lanstats_result['NewPacketsSent'])

            # fritzbox_dsl_status_enabled
            # fritzbox_dsl_status
            fritzbox_dslinfo_result = connection.call_action('WANDSLInterfaceConfig:1', 'GetInfo')
            fritzbox_dsl_enable.add_metric([fb_serial], fritzbox_dslinfo_result['NewEnable'])
            dslstatus = 1 if fritzbox_dslinfo_result['NewStatus'] == 'Up' else 0
            fritzbox_dsl_status.add_metric([fb_serial], dslstatus)

            # fritzbox_dsl_datarate_kbps
            fritzbox_dsl_datarate.add_metric([fb_serial, 'up', 'curr'],
                                             fritzbox_dslinfo_result['NewUpstreamCurrRate'])
            fritzbox_dsl_datarate.add_metric([fb_serial, 'down', 'curr'],
                                             fritzbox_dslinfo_result['NewDownstreamCurrRate'])
            fritzbox_dsl_datarate.add_metric([fb_serial, 'up', 'max'],
                                             fritzbox_dslinfo_result['NewUpstreamMaxRate'])
            fritzbox_dsl_datarate.add_metric([fb_serial, 'down', 'max'],
                                             fritzbox_dslinfo_result['NewDownstreamMaxRate'])

            # fritzbox_dsl_noise_margin_dB
            fritzbox_dsl_noisemargin.add_metric([fb_serial, 'up'],
                                                fritzbox_dslinfo_result['NewUpstreamNoiseMargin'] / 10)
            fritzbox_dsl_noisemargin.add_metric([fb_serial, 'down'],
                                                fritzbox_dslinfo_result['NewDownstreamNoiseMargin'] / 10)

            # fritzbox_dsl_attenuation_dB
            fritzbox_dsl_attenuation.add_metric([fb_serial, 'up'],
                                                fritzbox_dslinfo_result['NewUpstreamAttenuation'] / 10)
            fritzbox_dsl_attenuation.add_metric([fb_serial, 'down'],
                                                fritzbox_dslinfo_result['NewDownstreamAttenuation'] / 10)

            # fritzbox_ppp_connection_uptime
            # fritzbox_ppp_conection_state
            fritzbox_pppstatus_result = connection.call_action('WANPPPConnection:1', 'GetStatusInfo')
            pppconnected = 1 if fritzbox_pppstatus_result['NewConnectionStatus'] == 'Connected' else 0
            fritzbox_ppp_uptime.add_metric([fb_serial], fritzbox_pppstatus_result['NewUptime'])
            fritzbox_ppp_connected.add_metric([fb_serial, fritzbox_pppstatus_result['NewLastConnectionError']],
                                              pppconnected)

            # fritzbox_wan_data_bytes
            fritzbox_wan_result = connection.call_action('WANCommonIFC1', 'GetAddonInfos')
            wan_bytes_rx = fritzbox_wan_result['NewX_AVM_DE_TotalBytesReceived64']
            wan_bytes_tx = fritzbox_wan_result['NewX_AVM_DE_TotalBytesSent64']
            fritzbox_wan_data.add_metric([fb_serial, 'up'], wan_bytes_tx)
            fritzbox_wan_data.add_metric([fb_serial, 'down'], wan_bytes_rx)

            # fritzbox_wan_data_packets
            fritzbox_wan_result = connection.call_action('WANCommonInterfaceConfig:1', 'GetTotalPacketsReceived')
            wan_packets_rx = fritzbox_wan_result['NewTotalPacketsReceived']
            fritzbox_wan_result = connection.call_action('WANCommonInterfaceConfig:1', 'GetTotalPacketsSent')
            wan_packets_tx = fritzbox_wan_result['NewTotalPacketsSent']
            fritzbox_wan_packets.add_metric([fb_serial, 'up'], wan_packets_tx)
            fritzbox_wan_packets.add_metric([fb_serial, 'down'], wan_packets_rx)

        yield fritzbox_uptime
        yield fritzbox_update
        yield fritzbox_lanenable
        yield fritzbox_lanstatus
        yield fritzbox_lan_brx
        yield fritzbox_lan_btx
        yield fritzbox_lan_prx
        yield fritzbox_lan_ptx
        yield fritzbox_dsl_enable
        yield fritzbox_dsl_status
        yield fritzbox_dsl_datarate
        yield fritzbox_dsl_noisemargin
        yield fritzbox_dsl_attenuation
        yield fritzbox_ppp_uptime
        yield fritzbox_ppp_connected
        yield fritzbox_wan_data
        yield fritzbox_wan_packets


def get_configuration():
    collectors = list()

    if os.path.exists('settings.json'):
        with open('settings.json', 'r') as fh:
            configuration = json.loads(fh.read())

        if configuration is not None:
            if type(configuration) is list:
                for entry in configuration:
                    if 'host' in entry and 'username' in entry and 'password' in entry:
                        collectors.append(
                            FritzBoxCollector(entry['host'], entry['username'], entry['password']))

    if os.getenv('FRITZ_USER') is not None and os.getenv('FRITZ_PASS') is not None:
        collectors.append(
            FritzBoxCollector(os.getenv('FRITZ_HOST', 'fritz.box'), os.getenv('FRITZ_USER'), os.getenv('FRITZ_PASS')))

    return collectors


if __name__ == '__main__':

    REGISTRY.register(FritzBoxCollector('settings.json'))

    # Start up the server to expose the metrics.
    print("Starting Server at " + str(os.getenv('FRITZ_EXPORTER_PORT', 8765)))
    prometheus_client.start_http_server(os.getenv('FRITZ_EXPORTER_PORT', 8765))
    while True:
        time.sleep(10000)
