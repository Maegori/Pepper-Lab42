# Pepper Lab42

## Build Image
```
sudo docker build -t lab42 .
```

## Run container 
```
sudo docker run -it -v ${PWD}/source:/root/source lab42
```
// Expose $DISPLAY variable for GUI apps
```
sudo docker run -it --name pepper --net=host --env="DISPLAY" --volume="$HOME/.Xauthority:/root/.Xauthority:rw"  --device=/dev/input/ -v ${PWD}/source:/root/source lab42
```



## TODO
- Refine Handle / Hammer 
- Make post-hit behaviour
- Integrate voicelines
- Hand-holding
- Toggle guided mode <-> remote controlled

