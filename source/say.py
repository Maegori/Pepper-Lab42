from naoqi import ALProxy
tts = ALProxy("ALTextToSpeech", "146.50.60.38", 9559)
tts.say("Hello, world!")