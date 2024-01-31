#!/bin/bash

# create venv and install package
sudo poetry install

# enable autocompletion for cli
sudo activate-global-python-argcomplete

# create entrypoint-bash-script to run from commandline
read -r -d '' b_content <<EOF
#!/bin/bash
$HOME/.local/bin/poetry run -C $PWD python -m beautyboot
EOF

echo $b_content | sudo tee /opt/beautyboot

# make executable
sudo chmod +x /opt/beautyboot

# symlink it
sudo ln -s /opt/beautyboot /usr/local/bin/beautyboot