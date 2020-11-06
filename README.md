# Pepper Lab42

## Setting up docker container
```
$ docker build -t lab42 .
$ docker run -it --name pepper --net=host --env="DISPLAY" --volume="$HOME/.Xauthority:/root/.Xauthority:rw"  --device=/dev/input/ -v ${PWD}/source:/root/source lab42
```
## Starting environment
Expose DISPLAY variable for GUI apps and attach a terminal
to the container where behaviour scripts can be executed.
```
$ xhost +local:root
$ docker start pepper
$ docker attach pepper
# double ENTER

~/source# 
```

## Running behaviours
While connected to the same network as Pepper behaviours can be executed in the docker terminal.

```
~/source# python behaviour.py --ip x.x.x.x --port 1234
```

## Good to know

### Indices arm joints
0. ShoulderPitch
1. ShoulderRoll
2. ElbowYaw
3. ElbowRoll
4. WristYaw
5. Hand
