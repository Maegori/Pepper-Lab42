# Pepper Lab42

## Set up
```
$ docker build -t lab42 .
```

```
$ docker run -it --name pepper --net=host --env="DISPLAY" --volume="$HOME/.Xauthority:/root/.Xauthority:rw"  --device=/dev/input/ -v ${PWD}/source:/root/source lab42
```
## Starting environment
Expose $DISPLAY variable for GUI apps and attach a terminal
 to the container where behaviour scripts can be executed.
```
$ xhost +local:root
$ docker start pepper
$ docker attach pepper
# double ENTER

~/source# 
```

## Good to know

### Indices arm joints
0. ShoulderPitch
1. ShoulderRoll
2. ElbowYaw
3. ElbowRoll
4. WristYaw
5. Hand



## TODO

### Files
- Guide by hand
- Walk & talk
- Align and hit button
- Keyboard Nav

### Write ups

- Subscribe to events and connect callbacks 
- Webview, displaying content on Peppers tablet without internet connection
- ALProxy
- Input devices: Xbone & Keyboard
- Animation pipline
- Docker
- TLDR (What to do and what not to do)

(- Pepper copy)

### Misc

- Arnoud Walkthrough
- Labboek Final
- Splitten lab42 in sub scripts
- Write-ups

