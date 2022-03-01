docker container stop mininet mininet_mirror onos onos_mirror; docker container prune -f; docker image rm mininet mininet_mirror onos onos_mirror
#docker container stop mininet
#docker container stop onos
#docker container prune -f
#docker image rm mininet
#docker image rm onos
#rm -rf /Users/yanjing/Desktop/mininet/*.sh

docker-compose up -d
sleep 60

curl -X POST -u onos:rocks http://127.0.0.1:8181/onos/v1/applications/org.onosproject.fwd/active
curl -X POST -u onos:rocks http://127.0.0.1:8181/onos/v1/applications/org.onosproject.openflow/active

ONOS_IP=$(docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' onos)

#sed "s/onos_ip/${ONOS_IP}/g" ../create_linear_topo.sh > /Users/yanjing/Desktop/mininet/create_linear_topo.sh
#docker exec -it mininet sh /tmp/create_linear_topo.sh

#sed "s/onos_ip/${ONOS_IP}/g" ../create_tree_topo.sh > /Users/yanjing/Desktop/mininet/create_tree_topo.sh
#docker exec -it mininet sh /tmp/create_tree_topo.sh

sed "s/onos_ip/${ONOS_IP}/g" ../create_star_topo.sh > /Users/yanjing/Desktop/mininet/create_star_topo.sh
docker exec -it mininet sh /tmp/create_star_topo.sh
