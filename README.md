# beautyboot

## Info
Works on all unix-systems using plymouth for bootup-configuration

## install

### from source

```bash
git clone # repo
cd beautyboot
poetry install

# enable autocompletion for cli
sudo activate-global-python-argcomplete
```

### infos/troubleshooting autocomplete

- [https://stackoverflow.com/questions/63705161/autocomplete-commands-with-argcomplete-and-poetry](autocomplete-commands-with-argcomplete-and-poetry)
- [https://pypi.org/project/argcomplete/#activating-global-completion](pypi-argcomplete)

## run

```bash
# activate venv
poetry shell

# create custom theme called "mytheme" and set frame-count
python -m beautyboot --framecount 128 --sourcepath ~/Download/mytheme-nice-picture.jpg --with-login-logo mytheme
```

## todos

- fix console-entrypoint-support
- add visualisation of created animation
- add more customization-options for plymouth-config
- upload on pip 