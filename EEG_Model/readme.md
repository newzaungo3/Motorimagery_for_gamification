## Install cuda11.3

When build docker, you need to install torch with cuda 11.3 version by using

```sh
pipenv shell
pip3 install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu113
```

also
```
pipenv lock (to update pipfile and pipfile.lock)
``` 