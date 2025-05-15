---
date: 2018-08-13 16:57:38-04:00
layout: post
permalink: 2018-08-13-rpi-camera-part-3-a-few-incremental-fixes
thumbnail: /assets/images/thumbnails/sliding_window1.png
title: 'RPi camera, part 3: a few incremental fixes'
---

Round 3! Okay, this is where I try and polish it up in a couple ways.

Here are the things I said last time I needed to make better:

- Send pics more conventionally
- Fix detection sensitivity (still often picking up strong shade/sunlight quirks)
- Total design flaw: since the log file currently gets sent with each picture, but is updated when each picture is written, it is actually sometimes more updated than the pics in the folder. That is, if 30 pictures are created by the camera function, and those are immediately added to the log file, the log file is sent with the first of those 30, and it contains all 30 of them even though only one has been sent
- Better image classifier architecture
- Better labeled image dataset (32x32 is *tiny*)
- Sliding windows over detected images

##### Sliding windows

What is "sliding windows"? It's a pretty simple idea. Here's the motivating problem, first. When my convnet looks at an image I give it and tries to guess whether it has a car in it, it was trained on images where the car mostly filled the frame, so it will tend to only correctly classify images where the car also mostly fills the frame. If you have an image (like the one below) where there is a car but it's mostly in one corner, it may not get it (because it's looking for features bigger than that. There are a couple other effects too. One is that if we're only classifying 32x32 square images, then what I've been doing so far (resizing the image to have the smaller side be 32 and then squeezing the bigger side to also be 32) will distort the image, which will make it harder to classify. Lastly, you can imagine that if the actual image size we're giving it is something like 256x512, then even if it actually would have correctly classified it given these other problems, by the time it smooshes it down to 32x32, it might not have the resolution in the car region of the image to do it.

So what can fix a lot of these problems? You define a "window", a subset of the image, and "slide" it over the image in steps. Then, you pass this window subset to the classifier, so it's actually only classifying the subset. You might choose a stride for the sliding window such that you get M windows in the vertical dimension and N windows in the horizontal. So you're really doing MxN total classifications for the whole window, and then if one of them says "car!", you say that the image contains a car.

Here's a little illustration of mine, where the red grid over the green outlined window shows the windows being used (it's a little hard to tell them apart, but they're squares. There are three in the vertical direction):

![](/assets/images/sliding_window1.png)

There are of course a million little quirks and variants and choices to make with this. For example, I think it's common to choose two sizes for the window, which should let you look at two different "scales". Also, you have to choose some balance between having more sub windows and the computation time it will take to actually process them. I'm also pretty sure some convnets can have this built in by choosing different filter sizes (like, one that would group a block of pixels as a single pixel to make a larger "window").

Anyway, how does it work? Here are the results using my CIFAR-10 trained convnet from last time, on the same little group of detected images. I show the certainty distribution, which is the certainty that it thinks it detects a car.

No sliding windows:

![](/assets/images/certdist_2018-07-01_14-38-23_subset_noSW.png)

Detected:

![](/assets/images/gif_2018-07-20_11-04-57_noSW_detected.gif)

Not detected:

![](/assets/images/gif_2018-07-20_11-05-20_noSW_notdetected.gif)

Sliding windows:

![](/assets/images/certdist_2018-07-01_14-38-23_subset_SW.png)

Detected:

![](/assets/images/gif_2018-07-20_11-09-47_SW_detected.gif)

Not detected:

![](/assets/images/gif_2018-07-20_11-10-03_SW_notdetected.gif)

Definitely better! But still getting a ton of false positives, which is annoying. Honestly it may be because they're 32x32.

##### Fixing image sending

So I had a bit of a mystery on my hands. I was finding that after a while, my program was just...stopping. Not crashing, not giving any error, just stopping after about an hour. What I mean by stopping is that, while normally it outputs a line for each image it detects (on the RPi side), it would stop outputting anything, but not stop running. It took me embarrassingly long to figure out, but here's what I did. I first made a Debug class that basically logs *everything* the program does, right at the moment of doing it. This is actually a pretty handy thing to have around anyway, and basically doesn't slow it down. You'll notice that I'm periodically logging the CPU/Mem/temp, since I read somewhere that that can cause a problem, but all the values I've seen on mine are fine. Anyway, here was the first clue, you can see where it stops, after about an hour:

![](/assets/images/stopped_saving_rpi.png)

So you can see that it's saving them steadily for a while, and then stops saving them, but continues to send them. Welp, you probably guessed before I did, but while I was aware of how little space my RPi had on it (~700MB to play with), I thought that because I was removing the files right after sending them, I'd be okay. Howeverrrr:

![](/assets/images/rpi_memleft.png)

So I was running out of space!

One thing I did was immediately get a 32GB micro SD card and clone my RPi onto it, just to have a bit more wiggle room. To be honest, that might solve the problem, since I doubt I'd ever keep the program running long enough to generate that much data, but that would be not addressing the real problem here, which is that my files are sending *way too heckin' slow!*

My files are usually ~100kB, which should be easy to send and keep up with, even if something like 10 a second are being produced. For example, I know off the top of my head that when I send files via scp between my desktop and RPi, the transfer rate it shows is usually something like 1.5 MB/s. So what's going on?

It turns out that that "S" that stands for "secure" in SCP (or SSH, which it's based on) is pretty important! As [they discuss in this thread](https://unix.stackexchange.com/questions/112287/copy-files-without-encryption-ssh-in-local-network) where it seems like the person was having exactly my problem, there's actually some pretty nasty overhead involved in encrypting the file you're going to send. Of course, I don't care about that! I'm just sending stuff I don't care about over my LAN.

So one option in that thread was using a weaker cipher, while another was to use the rcp command, which is kind of like a totally unencrypted scp. I'm going to do a little diversion for a minute here because I wanted to know just how much these compared.

What I did was create a few dummy files, smallfile.txt (100 kB), mediumfile.txt (1 MB), and bigfile.txt (5 MB). First I just sent smallfile.txt 10 times to get a rough sense of the speed and overhead:

```python
for i in range(10):
    file = files[0]
    print('processing file',file)
    start = time()
    subprocess.check_call(['scp',file,remoteHostPath])
    total = time()-start
    print('time elapsed:',total)
    times.append(total)

print('done')
print(times)
```

![](/assets/images/smallfile_repeated_regularSCP.png)

Since it's apparently actually *transferring* at about 1.5 MB, an 88 kB file should take roughly 0.05 s, but you can see that it typically takes about 10x that. So SCP is definitely slowing it down.

Same when I send all of them:

![](/assets/images/allfiles_regSCP.png)

If you do the math, you can see that they each have ~0.5 s of overhead, like the small ones above. What if we do the weaker encryption? As they mention [here](http://www.sgvulcan.com/2014/10/21/latest-openssh-disables-arcfour-and-blowfish-cbc/), apparently in the latest release of Ubuntu, they've disabled weaker encryptions by default.

Well, let me cut to the chase. It's a pain to get those legacy ciphers working, but they mentioned in the comments of the SE thread above that the aes128-gcm@openssh.com cipher should be "blazingly fast" if you have the right CPU chipset or something. So, I tried that (which is still supported in Ubuntu 18.04), and it was no faster. I also tried rcp (which was actually very easy to set up at least), and it too was no faster.

So, the greater lesson I'm learning here is that there's something kind of inherent to setting up a connection across a LAN where you're not going to avoid about 0.5 s of overhead, even if the actual transfer is very fast.

At this point I have two paths forward in mind (other than just leaving it the way it is). The first is setting up my own thing, with python sockets and stuff. This might be doable, but seems like it would take a while to debug and stuff. The other that I've seen suggested a bunch is to mount a network drive on the RPi. This means that it will actually mount a folder from my desktop so it will look like a local directory to my RPi, in which case I won't have to (explicitly) deal with sending stuff at all. I'm a little paranoid about the whole mounting process (I know with physical media you have to be careful when mounting/unmounting), but I'm going to try this.

Welp, it's done. It actually didn't take that much redoing of my code, and it's a TON neater. I also took the opportunity to divide most of my code up into 4 main classes, which do most of their stuff internally: FileTools (which mounts the remote dir to the pi and creates the run dir), LogFile (which just creates and interfaces with the log file), Debugfile (same but for debug), and CameraTools (which handles the actual image detection and stuff). I also made a function in my main code that watches the keyboard for inputs, so you can enter a 'q' to quit. This is actually *remarkably* hard to figure out how to do properly when you have other processes running in parallel, especially if you want to make those processes able to exit cleanly (for example, in my case, unmount the filesystem as opposed to just killing the whole process).

So here's the code from the main section now:

```python
def watchKB(event,stdin):
    print('start kb loop')
    while True:
        k = stdin.readline().strip()
        #print(k)
        if k=='q':
            print('\n\nyou pressed q!')
            event.set()
            return(0)

#Get CLI arguments for notes for a run
if len(sys.argv)>1:
  notes = sys.argv[1]
else:
  notes = "no notes"

#Get event manager to close nicely
m = Manager()
close_event = m.Event()

ft = FileTools(notes,close_event)
lf = LogFile(ft)
df = DebugFile(ft)
ct = CameraTools(ft)

pool = Pool(processes=2)
p1 = pool.apply_async(ct.cameraStream,args=(ft,lf,df))
p2 = pool.apply_async(df.debugUpdateLoop)

watchKB(close_event,sys.stdin)

timeout_hours = 10
timeout_s = timeout_hours*3600
p1.get(timeout=timeout_s)
p2.get(timeout=timeout_s)
```

The functional part here is the close_event = m.Event(), which I then pass to the subprocesses that are created. It acts as a kind of global variable, which I can "set" in the main loop so that it will be detected in the subprocess. The subprocess is checking for "close_event.is_set()", which will tell it to shut down nicely.

How does it work? Pretty great! And it feels a lot cleaner than making a million scp calls.

Well, that's all for now. I have a couple more things already in the works, but I'll just put them in the next post. Here are the things that still obviously need to be done:

- It's still just getting a lot of shade problems. I think if I did this carefully and smartly I could actually make this not happen by just changing how the background average is taken. Related to that but slightly different, looking at it in not just grayscale might do it. That is, when an alternating shady/bright spot changes, it's currently sensing the change in intensity, but it's actually mostly the same hue. So if I kept the colors and looked at the different in the different channels, actual object movement (that changes the color as well as the intensity) might still trigger it, but not things like the sun getting brighter or the shade of leaves moving in the wind.
- Use a different convnet architecture -- I've actually already gotten a pre-trained VGGNet working with it, which is trained on a *wayyyy* huger dataset, and larger images. So hopefully it will be able to use my images that are larger (than 32x32) anyway, and be better trained that the dinky thing I did with the CIFAR-10.
- Relatedly, have it detect things like people, or bicycles: the VGGNet dataset has the most crazily specific classes.

Till next time!
