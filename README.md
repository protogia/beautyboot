# bootup-screen-cusomizer

## Info
Works on all unix-systems using plymouth for bootup-configuration

## install

### via pip
```bash
pipx install beautybooti
```

### from source
```bash
git clone # repo
cd beautybooti
poetry install

# enable autocompletion for cli
sudo activate-global-python-argcomplete
```

### infos/troubleshooting autocomplete
- [https://stackoverflow.com/questions/63705161/autocomplete-commands-with-argcomplete-and-poetry](autocomplete-commands-with-argcomplete-and-poetry)
- [https://pypi.org/project/argcomplete/#activating-global-completion](pypi-argcomplete)


## run
```bash
# set preeinstalled theme and show visualisation via --test 
beautybooti --theme preinstalled --test 

# create custom theme called "jim" and set frame-count
beautybooti --theme customized --framecount 256 jim --sourcepath ~/Download/jims-nice-picture.jpg
```