docker-ubuntu-vnc-desktop
=========================

From Docker Index
```
docker pull dockerhost:5000/lijla02/uvd
```

Build yourself
```
docker build --rm -t dockerhost:5000/lijla02/uvd images/uvd
```

Run
```
docker run -i -t -p 6080:6080 dockerhost:5000/lijla02/uvd
```

Browse http://127.0.0.1:6080/vnc.html

<img src="https://raw.github.com/fcwu/docker-ubuntu-vnc-desktop/master/screenshots/lxde.png" width=400/>


Reference
==================

https://github.com/fcwu/docker-ubuntu-vnc-desktop.git
