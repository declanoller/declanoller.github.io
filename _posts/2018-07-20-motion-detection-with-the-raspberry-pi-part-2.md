---
date: 2018-07-20 14:01:57-04:00
layout: post
permalink: 2018-07-20-motion-detection-with-the-raspberry-pi-part-2
thumbnail: /assets/images/thumbnails/2018-07-01_14-41-57.642_0.jpg
title: Motion detection with the Raspberry Pi, part 2
---

Hi hi!

In this post, I'm really just going to concentrate on building the whole pipeline. It's going to be rife with inefficiencies, inaccuracies, and stuff I 100% plan on fixing, but I think it's good to get a working product, even if it's very flawed. Someone I once worked for told me that projects in the US gov't kind of work that way: there was high emphasis on getting a product out the door, even if it was hacky and awful (though hopefully not). I think that makes sense a lot of the time. It's probably more motivating to see a project that does *something* to completion, even if it's crappy, than a project that is partly carefully done, but still very incomplete. A crappy car is cooler than a really nice wheel. Also, it seems like iterative, smaller fixes are relatively easy.

ANYWAY, that said, [last time I left off]({{ site.baseurl }}/2018-06-25-motion-detection-with-the-raspberry-pi-part-1), I said that the things that needed to be done were:

- Fix the sending thing to do in parallel
- Make monitoring program on other side that adds the files, etc to a CSV file to be analyzed with pandas
- Use keras with CIFAR datasets to figure out if detected object is car, person, etc
- Attach lens to get better view of cars
- Make rain shield with PVC pipe so I can leave it out for days or weeks

In retrospect, a lot of these were obvious pretty incremental, silly things (like the lens and rain shield (I guess it was also a "someday in the future" list)). In this post, I'm actually gonna cover three main things:

- Sending detected images in parallel with the sensing
- Making a "monitoring" program on my desktop
- Using keras to recognize cars vs not cars in the images that are sent over

Here's an extremely bootleg flowchart of how stuff is connected:

![](/assets/images/project_flowchart.jpg)

##### Parallel image detection and sending

At the end of last time, I mentioned that the images being detected and sent over weren't great because it was detecting stuff immediately, but taking a while to send, which, in the meantime prevented new images from being detected. This is called "blocking", since the sending is "blocking" the program from continuing until it's done sending. There are a few solutions to this, but the one that intuitively appealed to me was using multiple processes, one responsible for capturing and saving the images, and the other for sending them to my desktop. You could also just spawn a new process for each time you want to send, I think, but I went for this.

I was a little worried that this wouldn't speed stuff up much, because this would still be saving the image inside the camera/detection part of the program, which I assumed would be a slow operation. But, I timed it, and a whole iteration of detecting/image manipulation/saving/etc is about 30ms! So it's a huge speedup.

So, I won't paste the whole code because it's large, but here are the new/instrumental parts:

```python
def processFile(fName,remoteHost,remotePath):
  remoteHostPath = '{}:{}'.format(remoteHost,remotePath)
  subprocess.check_call(['scp','-q',fName,remoteHostPath])
  subprocess.check_call(['rm',fName])

def fileMonitor(logFileName,localPath,remoteHost,remotePath):
  print('entering filemonitor')
  processedFiles = []

  while True:
    #files = os.listdir(dir)
    files = glob(localPath+'/'+'*.jpg')
    if len(files)>0:
      #print('sending these files:',files)
      [processFile(file,remoteHost,remotePath) for file in files if file not in processedFiles]
      [processedFiles.append(file) for file in files if file not in processedFiles]
      remoteHostPath = '{}:{}'.format(remoteHost,remotePath)
      time.sleep(0.5)
      subprocess.check_call(['scp','-q',localPath+'/'+logFileName,remoteHostPath])

def cameraStream(logFileName,localPath,startDateTimeString):
  #Camera stuff
  #............................
  tempFName = dateString + '_' + str(boxCounter)
  tempPicName = tempFName + ext
  cv2.imwrite(localPath + '/' + tempPicName,frameDraw)

  fLog = open(localPath + '/' + logFileName,'a')
  fLog.write("{}\t{}\t{}\t{}\t{}\n".format(tempFName,x,y,x + w,y + h))
  fLog.close()

#Main section

pool = Pool(processes=2)
p1 = pool.apply_async(fileMonitor,args=(logFileName,localPath,remoteHost,remotePath))
p2 = pool.apply_async(cameraStream,args=(logFileName,localPath,startDateTimeString))

print(p1.get(timeout=3600))
print(p2.get(timeout=3600))
```

Very messy, obviously. processFile() is for sending a single file via scp, and then using the rm command to remove it after its sent (so they don't accumulate and clog up my RPi). I've been told since last time that os.system() is actually a deprecated way to make system calls. subprocess.check_call() *should* be blocking, I think, which is what I want in this case -- since scp takes a second and I think rm tends to go very quickly, it would be bad if rm ran while scp was running. I actually got some glitchy files sent over the old method, and that might've been what was happening. So I hope check_call() doesn't proceed until the command in it is done.

I'm also pretty sure I'm not supposed to do system calls for stuff like this. I think you're probably supposed to use stuff within python, like something that sends data, and something like os.remove() instead of rm. But! We're doing main ideas, not small fixes, today.

fileMonitor() is pretty straightforward. It has a list of files it has already processed, which starts out empty. In an infinite loop, it uses glob() to get a list of all the .jpg files in our directory. If this list isn't empty, it does processFile() to each one if it's not in processedFiles already, then adds it to processedFiles, and then sends the log file. The idea here is that we want the log file's contents to match the files that have been sent, so we should make sure to send the latest log file at the same time as any pic.

cameraStream() is pretty much the same as before, except now it's not sending the files in it, just saving them to disk. I think if I wanted to make an improvement, I'd probably want to just keep them in data or something, I'm guessing. But this seems to work fine for now.

Then, we use multiprocessing.Pool to create a "pool" of two workers, and make them run asynchronously with apply_async(). I gave them a timeout of an hour, but you don't have to.

And it works! You get several frames for each car:

![](/assets/images/gif_2018-07-12_16-15-12.gif)

##### Desktop monitoring program

This part was fun! I wanted a program that could run independently on my desktop, where the images are after being sent, that would prepare them for whatever I want to to with them. I wanted a couple specific things, though: I wanted it to be able to run and update in realtime (i.e., while images are still being sent), or not, like after the camera has stopped. I also wanted to make it so you could easily rebuild the "database" if you messed it up or anything.

So here's what I did. The program starts off by checking if the TSV (which will be our database) file with the expected name already exists (it should have the same base name as the dir). If it is, it assumes we have already ran this in the past, reads it into a pandas DataFrame, and takes the filenames into the processedFiles list. If it doesn't exist, it creates one.

Then, inside a big loop, it reads the log file repeatedly, and takes its number of entries. If that number is more than the length of processedFiles, there must be new files to process. So, it gets the ones that aren't in processedFiles and puts them onto a queue. Then, inside a while loop based on the queue, it pops them off one by one, does whatever action to them (see below), and adds them to the DataFrame, which is immediately saved.

So, it will sit there and churn through new files until there are no new ones, and then it will sit and wait for new ones. You might point out at this point that essentially all it has done is recreate the LogFile, and you'd be right. But the point is to prepare it for doing something else.

##### Keras, CNN, CIFAR, recognizing cars

And now this is the really fun part of it! Getting Keras to work with the CIFAR images and recognize cars in my images. The [CIFAR images](https://www.cs.toronto.edu/~kriz/cifar.html) are a very famous free, labeled dataset of (32px)^2 images, of 10 "classes". One of the classes is cars, so that's what we'll be using to train our convolutional neural net (CNN) to recognize. The first step is just to train the CNN on the CIFAR images.

I think I mostly copied the code [from here](https://keras.io/getting-started/sequential-model-guide/) and maybe some random blogs, though there are a million simple examples of CNNs in Keras. I had to change the code for classifying other CIFAR10 or MNIST datasets in two parts because (at this stage, anyway) I'm only doing a binary classifier, not a 10-way image classifier. The two parts are (1) the activation function for the final dense layer. For the 10-way ones, it's softmax. For a binary classifier, you only have a single output node that can vary between 0 and 1, so you just use sigmoid. (2) The loss function for a multi class classifier is categorical_crossentropy, but we just use binary_crossentropy.

I actually had it working pretty easily at first, and then must've changed something, cause it wasn't working...

I went back, compared it to a few tutorials online, and tried to see if I could find a difference. As far as I can tell, most people do a pretty identical Conv2D -> MaxPool -> Conv2D -> MaxPool -> Dense -> Output architecture, like I was doing, so that probably wasn't it. I noticed that I was using 100 filters in the first Conv layer and 200 in the second, while most people were using 25/50 or something much less. I think I started (when I copied the code from somewhere) with a more typical number, and then naively increased the number of filters to try to increase the accuracy. I was getting ~90% accuracy, which I realized is what you would expect, since the train dataset is 90% non-car images and 10% car images, so it was just learning to predict that there are no cars. Now I'm getting ~97%  accuracy after ~10 epochs.

Anyway, that's about it! I saved the model produced from this training, and made it load when my desktop monitoring program begins. Now, I have a function that takes the detected image and the coordinates of the green box drawn around it, crops that box out, resizes it to 32x32, and runs it through the classifier model! It then takes the classification certainty and saves that into the TSV file.

It's actually remarkably good, doing the bare minimum. I did a long run, getting ~2,000 (detected) images over about the course of an hour. I then made a little program that takes the CSV file into a pandas DataFrame, and selects for the entries with the Certainty field > some threshold. I started by using a threshold of 0.3, which divided the images into ~1,700 "no car" images and ~80 car images.

Here's a gif of all the ones that were classified as a car:

![](/assets/images/gif_2018-07-01_15-32-42.gif)

And the non-car classified set:

![](/assets/images/gif_2018-07-01_15-34-35.gif)

You can see that the first one is getting pretty much 100% cars (with a false positive of a biker (maybe it's picking up the wheels?)), which is cool, but the bottom one has a bunch of cars. Let's see if lowering the threshold to, say, 0.1 helps?

It increases the number of car ones to ~140 and decreases the non-car ones to ~1,670, but to be honest I'm not sure the results are better.

Car:

![](/assets/images/gif_2018-07-01_15-54-49.gif)

No car:

![](/assets/images/gif_2018-07-01_15-53-28.gif)

It seems like the car ones now have a lot more false positives (like the leaves in the corner), while the non-car ones still have a decent number of cars in them. Though I'll say, it seems like it *has* decreased the number of misclassifications of "really obvious" cars, like when they're in the middle of the road. To be honest, in that last gif, it's not exactly surprising that it's not getting that black car at the top that is pulling out. The way I'm resizing the image (naively) to fit the CNN is to just squish the box to 32x32 (distorting, not cropping). Therefore, if the box is long, the car will be squished into a tiny sliver, in an already tiny image. I'll talk about fixes for this later.

Here's a distribution of the certainty for all the frames of this run:

![](/assets/images/cert1.png)

That's probably not great, since there are a significant number in between 0.1 and 0.9 that might actually be cars it's just not sure about.

So that's it! I kind of have the whole pipeline set up, or at least, the parts of it I've decided on so far. I say that because I haven't really decided what I'll actually *do* with the data.

What's there left to do? Holy hell, so much. Many, many improvements:

- Send pics more conventionally
- Fix detection sensitivity (still often picking up strong shade/sunlight quirks)
- Total design flaw: since the log file currently gets sent with each picture, but is updated when each picture is written, it is actually sometimes more updated than the pics in the folder. That is, if 30 pictures are created by the camera function, and those are immediately added to the log file, the log file is sent with the first of those 30, and it contains all 30 of them even though only one has been sent
- Better image classifier architecture
- Better labeled image dataset (32x32 is*tiny*)
- Sliding windows over detected images

Smell ya later!
