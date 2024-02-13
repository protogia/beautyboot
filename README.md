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

Create custom theme from local image called ***mytheme*** and set frame-count

```bash
beautyboot --framecount 128 --sourcepath ~/Download/mytheme-nice-picture.jpg --with-login-logo mytheme
```

Create custom theme from given youtube-URL called ***myyt*** and set frame-count

```bash
beautyboot --framecount 100 --youtube <https://youtube-url-of-video> --with-login-logo myyt
# CLI will ask you for start-timestamp & end-timestamp during the process ... 
```


