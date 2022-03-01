#docker container stop mininet_mirror
#docker container stop onos_mirror
#docker container prune -f
#docker image rm mininet_mirror
#docker image rm onos_mirror
#rm -rf mirror_topo.sh
#rm -rf /Users/yanjing/Desktop/mininet/mirror_topo.sh

docker-compose up -d
sleep 60

curl -X POST -u onos:rocks http://127.0.0.1:8182/onos/v1/applications/org.onosproject.fwd/active
curl -X POST -u onos:rocks http://127.0.0.1:8182/onos/v1/applications/org.onosproject.openflow/active

cp ../detect_topo_shell.py ./
python3 detect_topo_shell.py 

ONOS_IP=$(docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' onos_mirror)

sed "s/onos_ip/${ONOS_IP}/g" ./mirror_topo.sh > /Users/yanjing/Desktop/mininet/mirror_topo.sh
docker exec -it mininet_mirror sh /tmp/mirror_topo.sh
