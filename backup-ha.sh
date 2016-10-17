for f in *.yaml
do
  curl -T $f ftp://192.168.101.1/Stick/Padre/$f
done

for f in *.xml
do
  curl -T $f ftp://192.168.101.1/Stick/Padre/$f
done
 
for f in custom_components/*.*
do
  curl -T $f ftp://192.168.101.1/Stick/Padre/$f
done

for f in www/*.*
do
  curl -T $f ftp://192.168.101.1/Stick/Padre/$f
done

for f in panels/*.*
do
  curl -T $f ftp://192.168.101.1/Stick/Padre/$f
done

curl -T ../dasher/config/config.json ftp://192.168.101.1/Stick/Padre/dasher/config.json

curl -T backup-ha.sh ftp://192.168.101.1/Stick/Padre/backup-ha.sh


