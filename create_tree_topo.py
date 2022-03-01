#!/usr/bin/python2.7
from mininet.net import Mininet
from mininet.node import Controller, OVSKernelSwitch, RemoteController
from mininet.cli import CLI
# Initiate the network topology
topo = Mininet(controller=RemoteController, switch=OVSKernelSwitch)
# Add controllers to the topology
c1 = topo.addController("c1", controller=RemoteController, ip="172.17.0.3", port=6653)
# Add hosts to the topology
h1 = topo.addHost("h1", ip="192.168.1.10" )
h2 = topo.addHost("h2", ip="192.168.1.20" )
h3 = topo.addHost("h3", ip="192.168.1.30" )
h4 = topo.addHost("h4", ip="192.168.1.40" )
h5 = topo.addHost("h5", ip="192.168.1.50" )
h6 = topo.addHost("h6", ip="192.168.1.60" )
# Add switches to the topology
s1 = topo.addSwitch("s1", protocols="OpenFlow14")
s2 = topo.addSwitch("s2", protocols="OpenFlow14")
s3 = topo.addSwitch("s3", protocols="OpenFlow14")
s4 = topo.addSwitch("s4", protocols="OpenFlow14")
# Set links between switches
s1.linkTo( s2 )
s1.linkTo( s3 )
s1.linkTo( s4 )
s1.linkTo( h5 )
s1.linkTo( h6 )
# Set links between switches and hosts
s2.linkTo( h1 )
s3.linkTo( h2 )
s3.linkTo( h3 )
s4.linkTo( h4 )
# Build and start the network topology with the hosts, switches, links and remote controllers above
topo.build()
c1.start()
s1.start( [c1] )
s2.start( [c1] )
s3.start( [c1] )
s4.start( [c1] )
topo.start()
# Test the arp, ping and iperf
topo.staticArp()
topo.pingAll()
topo.iperf()
CLI( topo )
# If you need to stop the network topology, uncomment the following sentence, otherwise, using "mn -c" to clear the network topology
# topo.stop()