JJRC's blue crab (H43WH) remote control and camera stream in Ubuntu

Explanation: The JJRC blue crab is a commercial toy drone that came with an Android app to control it, streaming the camera and allowing control. It was connected to the phone through wifi.
I developed this application by reverse engineering the wifi protocol, using Wireshark to intercept the packages. After doing some tests moving the individual controls I more or less guessed what part of the message did what.
Trust me, I'm a reverse engineer, I guess?
After reverse engineering the protocol, I made two python programs, one would stream the camera to the pc, the other one would connect to an XBOX controller and compose messages to send to the drone doing checksums and some crazy math, all in real time.

Video of my software working: https://www.youtube.com/watch?v=_I7nl1MVMT8

Random Youtube video showing the drone and Android app are: https://www.youtube.com/watch?v=sy-Ts9UX2gE&ab_channel=JDQuad

How to use: Run the watch_video_fluid.sh in an Ubuntu shell. This will open a window with the camera stream and run the shell program for sending controller commands.
This will most likely work. I don't have the drone anymore so I can't test which files were the right ones. If it doesn't, just run the two python lines inside the sh file separately and it should work.

Important note!!: This is a very old software project of mine, which I did before being a software developer professionally. This means the code may not be as easy to understand, even though I tried to translate the comments to english in the main files.

I added my research files as well, including messing with the libraries for real time, camera stream, the xbox controller library and some wireshark package captures I used to reverse engineer the protocol.
