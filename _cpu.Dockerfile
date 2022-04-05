FROM ubuntu:20.04

# like CD command in terminal. it will create directory if path is not existed
WORKDIR /root/EEG_Model

# Usual terminal commands for installing environment
RUN apt update && apt upgrade -y
RUN apt install python3 python3-pip -y
RUN apt install git -y
# I will use `pipenv` to dynamically controll my environment
# If you want to use `pip install`, just remove `pipenv` and continue with `pip install`
RUN pip3 install pipenv

RUN pipenv install

RUN pipenv install torch==1.11.0 torchvision==0.12.0 torchaudio==0.11.0 --ignore-pipfile

RUN pipenv install 'pillow' --ignore-pipfile
RUN pipenv install "opencv-python==4.5.3.56" --ignore-pipfile
RUN pipenv install "sklearn" --ignore-pipfile
RUN pipenv install "pandas" --ignore-pipfile
RUN pipenv install "seaborn" --ignore-pipfile
RUN pipenv install "matplotlib" --ignore-pipfile
RUN pipenv install "mne==0.23.4" --ignore-pipfile
RUN pipenv install "scipy==1.7.1" --ignore-pipfile
RUN pipenv install "torchsummary==1.5.1" --ignore-pipfile

CMD tail -f /dev/null