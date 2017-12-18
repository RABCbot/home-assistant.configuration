for f in *.yaml
do
  curl -T $f ftp://admin:2putipus@192.168.101.113/stick/Padre/$f
done

for f in *.xml
do
  curl -T $f ftp://admin:2putipus@192.168.101.113/stick/Padre/$f
done
 
for f in custom_components/*.*
do
  curl -T $f ftp://admin:2putipus@192.168.101.113/stick/Padre/$f
done

for f in www/*.*
do
  curl -T $f ftp://admin:2putipus@192.168.101.113/stick/Padre/$f
done

for f in panels/*.*
do
  curl -T $f ftp://admin:2putipus@192.168.101.113/stick/Padre/$f
done

for f in automation/*.*
do
  curl -T $f ftp://admin:2putipus@192.168.101.113/stick/Padre/$f
done

for f in lights/*.*
do
  curl -T $f ftp://admin:2putipus@192.168.101.113/stick/Padre/$f
done

for f in scripts/*.*
do
  curl -T $f ftp://admin:2putipus@192.168.101.113/stick/Padre/$f
done

for f in sensors/*.*
do
  curl -T $f ftp://admin:2putipus@192.168.101.113/stick/Padre/$f
done

for f in switches/*.*
do
  curl -T $f ftp://admin:2putipus@192.168.101.113/stick/Padre/$f
done

curl -T /home/homeassistant/dasher/config/config.json ftp://admin:2putipus@192.168.101.113/stick/Padre/dasher/config.json

curl -T /etc/mosquitto/mosquitto.conf ftp://admin:2putipus@192.168.101.113/stick/Padre/mosquitto/mosquitto.conf

curl -T backup.sh ftp://admin:2putipus@192.168.101.113/stick/Padre/backup.sh

curl -T restore.sh ftp://admin:2putipus@192.168.101.113/stick/Padre/restore.sh



