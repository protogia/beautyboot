# beautyboot

## Info
Works on all unix-systems using plymouth for bootup-configuration

## install

### from source

```bash
git clone # repo
cd beautyboot
chmod +x .install.sh
sudo ./install.sh # creates venv, an entrypoint-script in /opt/ and link in /usr/local/bin
```

## run

```bash
# create custom theme called "mytheme" and set frame-count
beautyboot --framecount 128 --sourcepath ~/Download/mytheme-nice-picture.jpg --with-login-logo mytheme
```

## todos

- add visualisation of created animation
- add more customization-options for plymouth-config
- upload on pip 