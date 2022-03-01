import requests, json
from requests.auth import HTTPBasicAuth

url = 'http://127.0.0.1:8181/onos/v1/'

# Request the info of switches, and store the id info to switch_id_list
switch_id_list = []
res_devices = requests.get(url + "devices", auth=HTTPBasicAuth("onos", "rocks")).json()["devices"]
for index in range(0, len(res_devices)):
    switch_id_list.append(res_devices[index]["id"])
print("switch_id_list is: ", switch_id_list)

# Request the ports info of switches based on the id info obtained above, and store the name, id and ports info to switch_list
switch_list = []
for switch_id in switch_id_list:
    res_ports = requests.get(url + "devices/" + switch_id + "/ports", auth=HTTPBasicAuth("onos", "rocks")).json()["ports"]
    switch_ports = []
    for port in res_ports:
        if port["port"] == "local":
            switch_name = port["annotations"]["portName"]
        else:
            switch_ports.append((port["port"], port["annotations"]["portName"]))   
    switch_list.append({"switch_name": switch_name, "switch_id": switch_id, "switch_ports": switch_ports}) 

for switch in switch_list:
    print("Each switch info is: ", switch)

# Request the host_ip, host_locations info, and store the name, ip and location info to host_list
host_list = []
res_hosts = requests.get(url + "hosts", auth=HTTPBasicAuth("onos", "rocks")).json()["hosts"]
for index in range(1, len(res_hosts)+1):
    host_list.append({"host_name": "h%s" % index, "host_port": "h%s-eth1" % index, "host_ip": res_hosts[index-1]["ipAddresses"][0], "host_mac": res_hosts[index-1]["mac"], "host_switch_connection": res_hosts[index-1]["locations"][0]})

for host in host_list:
    print("Each host info is: ", host)

# Request the link info among switches, and store the src_switch_port and dst_switch_port to link_list
link_list = []
res_links = requests.get(url + "links", auth=HTTPBasicAuth("onos", "rocks")).json()["links"]
for link in res_links:
    for switch in switch_list:
        if link["src"]["device"] == switch["switch_id"]:
            for port in switch["switch_ports"]:
                if link["src"]["port"] == port[0]:
                    src_link = port[1]
    for switch in switch_list:
        if link["dst"]["device"] == switch["switch_id"]:
            for port in switch["switch_ports"]:
                if link["dst"]["port"] == port[0]:
                    dst_link = port[1]
    link_list.append(sorted((src_link, dst_link)))

valid_link_list = []
for link in link_list:
    if link not in valid_link_list:
        valid_link_list.append(link)
print("Connection info among switches is: ", valid_link_list)

# Generate the shell script for mirroring network topology
with open("./mirror_topo.sh", "w") as filename:
    filename.write("# 0. Clean the env\n")
    filename.write("mn -c\n")
    filename.write("\n")

    filename.write("# 1. Create namespaces\n")
    for index in range(1, len(res_hosts)+1):
        filename.write("ip netns add h%s\n" % index)
    filename.write("\n")

    filename.write("# 2. Create openvswitch\n")
    for switch in switch_list:
        filename.write("ovs-vsctl add-br %s\n" % switch["switch_name"])
        filename.write("ovs-vsctl set bridge %s protocols=OpenFlow14\n" % switch["switch_name"])
    filename.write("\n")

    filename.write("# 3.1 Create vethernet links among switches and hosts\n")
    for host in host_list:
        for switch in switch_list:
            if host["host_switch_connection"]["elementId"] == switch["switch_id"]:
                for port in switch["switch_ports"]:
                    if host["host_switch_connection"]["port"] == port[0]:
                        filename.write("ip link add %s type veth peer name %s\n" % (host["host_port"], port[1]))
    filename.write("\n")

    filename.write("# 3.2 Create vethernet links among switches and switches\n")
    for link in valid_link_list:
        filename.write("ip link add %s type veth peer name %s\n" % (link[0], link[1]))
    filename.write("\n")

    filename.write("# 4. Move host ports into namespaces\n")
    for host in host_list:
        filename.write("ip link set %s netns %s\n" % (host["host_port"], host["host_name"]))
    filename.write("\n")

    filename.write("# 5. Connect switch ports to OVS\n")
    for switch in switch_list:
        for port in switch["switch_ports"]:
            filename.write("ovs-vsctl add-port %s %s\n" % (switch["switch_name"], port[1]))
    filename.write("\n")

    filename.write("# 6. Connect controller to switch\n")
    for switch in switch_list:
        filename.write("ovs-vsctl set-controller %s tcp:onos_ip:6653\n" % switch["switch_name"])
    filename.write("\n")

    filename.write("# 7.1 Setup ip for hosts\n")
    for host in host_list:
        filename.write("ip netns exec %s ifconfig %s %s hw ether %s\n" % (host["host_name"], host["host_port"], host["host_ip"], host["host_mac"]))
        filename.write("ip netns exec %s ifconfig lo up\n" % host["host_name"])
    filename.write("\n")

    filename.write("# 7.2 Setup ip for switches\n")
    for switch in switch_list:
        for port in switch["switch_ports"]:
            filename.write("ifconfig %s up\n" % port[1])
    filename.write("\n")

    filename.write("# 8 Test connections between hosts\n")
    for host in host_list:
        filename.write("ip netns exec h1 ping -c1 %s\n" % host["host_ip"])
