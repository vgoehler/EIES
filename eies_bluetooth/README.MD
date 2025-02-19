# Bluetooth Connection between Raspi and Base

- Client has a Listener that switches Devices on the Raspi
- Server sents calls to the client

## Bluetooth

### PyBluez

- don't use pip package install from git: 
  ```shell
  pip install git+https://github.com/pybluez/pybluez.git#egg=pybluez
  ```
- also! bluetooth dev packages
 ```shell
  sudo apt-get install libbluetooth-dev
  ```

#### no advertisable device on pc

- this causes bluetooth.btcommon.BluetoothError: no advertisable device

- [Solution on Stack Overflow](https://stackoverflow.com/questions/37913796/bluetooth-error-no-advertisable-device)

- ``bash sudo hciconfig hci0 piscan``

- this causes BluethoothError: No such file or directory

- [Solution on stack overflow](https://stackoverflow.com/questions/36675931/bluetooth-btcommon-bluetootherror-2-no-such-file-or-directory)

- Compat Mode; in  /etc/systemd/system/dbus-org.bluez.service change

ExecStart=/usr/lib/bluetooth/bluetoothd

into

ExecStart=/usr/lib/bluetooth/bluetoothd -C

- restart Service
- ``bash sudo systemctl daemon-reload``
- ``bash sudo service bluetooth restart``

- this causes bluetooth.btcommon.BluetoothError: [Errno 13] Permission denied

- [solution on stack overflow](https://stackoverflow.com/questions/34599703/rfcomm-bluetooth-permission-denied-error-raspberry-pi)

- check for group bluetooth
- ``bash cat /etc/group | grep bluetooth``
- add user if not allready in there
- ``bash sudo usermod -G bluetooth -a vgoehler``
- change group of sdp file (for compat mode)
- ``bash sudo chgrp bluetooth /var/run/sdp``

##### Persistency

- create /etc/systemd/system/var-run-sdp.path
```config
[Unit]
Description=Monitor /var/run/sdp

[Install]
WantedBy=bluetooth.service

[Path]
PathExists=/var/run/sdp
Unit=var-run-sdp.service
```
- create /etc/systemd/system/var-run-sdp.service
```config
[Unit]
Description=Set permission of /var/run/sdp

[Install]
RequiredBy=var-run-sdp.path

[Service]
Type=simple
ExecStart=/bin/chgrp bluetooth /var/run/sdp
```
- then start it all up
- ``bash sudo systemctl daemon-reload``
- ``bash sudo systemctl enable var-run-sdp.path``
- ``bash sudo systemctl enable var-run-sdp.service``
- ``bash sudo systemctl start var-run-sdp.path``




