FROM ubuntu:16.04
ENV OPENCV_VERSION 3.4.2

ENV DEBIAN_FRONTEND noninteractive
ENV USER root

# Install all dependencies for OpenCV
RUN apt-get -y update && \
        apt-get -y install \
        python2.7 \
        python2.7-dev \
        git \
        wget \
        unzip \
        cmake \
        build-essential \
        pkg-config \
        libatlas-base-dev \
        libjasper-dev \
        libgtk2.0-dev \
        libavcodec-dev \
        libavformat-dev \
        libswscale-dev \
        libjpeg-dev \
        libpng-dev \
        libtiff-dev \
        libjasper-dev \
        libv4l-dev \
        python-tk \
        ssh

RUN     wget https://bootstrap.pypa.io/get-pip.py && \
        python get-pip.py && \
        rm get-pip.py && \
        pip install numpy 

# Downlaod OpenCV
RUN     wget https://github.com/opencv/opencv/archive/$OPENCV_VERSION.zip -O opencv3.zip && \
        unzip -q opencv3.zip && \
        mv /opencv-$OPENCV_VERSION /opencv && \
        rm opencv3.zip && \
        wget https://github.com/opencv/opencv_contrib/archive/$OPENCV_VERSION.zip -O opencv_contrib3.zip && \
        unzip -q opencv_contrib3.zip && \
        mv /opencv_contrib-$OPENCV_VERSION /opencv_contrib && \
        rm opencv_contrib3.zip 

# Build OpenCV
RUN     mkdir /opencv/build && cd /opencv/build && \
        cmake   -D CMAKE_BUILD_TYPE=RELEASE \
        -D BUILD_PYTHON_SUPPORT=ON \
        -D CMAKE_INSTALL_PREFIX=/usr/local \
        -D OPENCV_EXTRA_MODULES_PATH=/opencv_contrib/modules \
        -D BUILD_EXAMPLES=OFF .. && \
        cd /opencv/build && \
        make -j$(nproc) && \
        make install && \
        ldconfig 

# Clean
RUN     apt-get -y remove \
        python2.7-dev \
        libatlas-base-dev \
        libjasper-dev \
        libgtk2.0-dev \
        libavcodec-dev \
        libavformat-dev \
        libswscale-dev \
        libjpeg-dev \
        libpng-dev \
        libtiff-dev \
        libjasper-dev \
        libv4l-dev \
        && \
        apt-get clean && \
        rm -rf /opencv /opencv_contrib /var/lib/apt/lists/*

# Install pynaoqi 2.5.5.5 library
RUN wget -P /root/ https://community-static.aldebaran.com/resources/2.5.10/Python%20SDK/pynaoqi-python2.7-2.5.7.1-linux64.tar.gz
RUN tar -xvzf /root/pynaoqi-python2.7-2.5.7.1-linux64.tar.gz -C /root/
RUN rm /root/pynaoqi-python2.7-2.5.7.1-linux64.tar.gz
ENV LD_LIBRARY_PATH /opt/Aldebaran/lib/
ENV PYTHONPATH="/root/pynaoqi-python2.7-2.5.7.1-linux64/lib/python2.7/site-packages"

COPY requirements.txt /root/requirements.txt
RUN pip install -r /root/requirements.txt

WORKDIR /root/source

# docker run -it --name pepper --net=host --env="DISPLAY" --volume="$HOME/.Xauthority:/root/.Xauthority:rw"  --device=/dev/input/ -v ${PWD}/source:/root/source lab42
# xhost  +local:root
# docker start pepper
# docker attach pepper