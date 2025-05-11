---
date: 2017-07-22 04:21:46-04:00
layout: post
title: Servo controller box
---

Woowee, this is a long one.

This is actually something I did for my job. Here's the deal: I have this electrochemical bath that has a sample in it; one electrode is a piece of graphite, the other electrode is the sample itself. Don't worry about what the bath does for now, but it's important that the longer the sample is in the bath, the more the effect of the bath is on the sample. It's pretty much linear with time.

Now, I often want to see the effect of different lengths of time in the bath, with all other variables staying the same. The way I've done this in the past was to paint nail polish over parts of the sample (nail polish protects the covered part of the sample from the effect of the bath), put it in the bath for some amount of time, then take it out, either remove that nail polish, or add more, and put the sample back in for more time, etc. So basically you can have different length times on the same piece, which is useful for consistency and visually looks good.

However, this always bugged me, for two reasons.

The first is that it's just pretty time wasting. Each sample removal/rinsing/N2 drying/nail polish painting/putting back/etc takes several minutes, so if you want to see 10 different bath times on the same sample, it could end up taking an hour of work that's slightly more fun than eating a handful of drywall screws.

The second reason is better. The property I'm looking at can actually be *very* dependent on the length of time in the bath, and we don't actually have *that great* precision for the bath time (there are tons of things that can affect it: the sample size, human error, bath concentration, etc). So it's hard to make these samples consistently get the same exact thing. For example, if I made 5 different samples, each with bath times of 0-100s in increments of 10s, each sample would have noticeably different values.

So, laziness and curiosity (my motivation for probably 100% of what I do in life) led me to do what I had been meaning to do for a while now: I made a "sample puller".

"What is that", you almost certainly don't ask?

It basically solves both of these problems. The idea is to slowly pull the sample out of the bath, so that the effect is continuously changing along the length of the sample.

Let's look at the hardware side first.

I considered a couple ways of doing this: using either a motor, or a servo. A motor has some advantages, but ultimately I decided that it would be kind of hard to pull something up vertically. You could use a string that gets wound around the axle as it turns, pulling it up. You could make it so it pulls something up through a small tube, so it's constrained in a vertical direction but... I dunno. That seemed like it could be a real pain in the ass to make work nicely.

So I ended up going for a servo, which seemed like it would work more easily, and I also didn't have much experience with, so I wanted to learn about. Here's the rough schematic of my idea:

![puller schematic.PNG](/assets/images/puller-schematic.png)

I hope the idea here is clear. There's an arm attached to the servo, and the part where the wire holding the sample up (the vertical black line) meets the servo arm, it is tight enough to conduct current (important for the electrochemical process!), but loose enough to allow the sample to always hang vertically, from just its own weight.

This, of course, has some immediately obvious flaws. First, the sample will have some horizontal motion as the servo arm turns. As the angle from the vertical approaches 90 degrees, the horizontal distance from the servo increases, and then decreases after 90 degrees. Another problem is that, if the servo is moving with the same angular speed throughout the range, the speed of the sample in the vertical direction will be dependent on the angle it's at. An issue with a similar cause but different effect is that, depending on the angle, the servo will also have a lot more force on it. When the arm is 90 degrees from the vertical, it will need to use a ton of torque, while when it's near 0 degrees, it will have to use very little torque, because the angle between the arm and force of gravity is nearly 0 ($latex  \vec{\tau} = \vec{r} \times \vec{F} \approx 0 $).

Honestly, though, these problems are pretty minor. First of all, it's not really going through much of a angular range (the sample is only 2-3"), so the horizontal motion isn't much, and it actually doesn't matter a whole lot anyway for this application. With regards to the speed, it's also not a huge deal. It's still going through the whole range, just faster in some parts. Lastly, the extra torque required at bigger angles to the vertical shouldn't really matter, as long as the power supply can..err, supply it.

Anyway, here's a photo of this part of it in practice. I must warn you, it looks ghetto as all hell. I made it out of scrap metal we had lying around, and it's not really meant to look that pretty. Also, please ignore the death-tempting, devil-may-care, oh-god-don't-touch-any-surfaces-without-wearing-gloves fume hood.

![puller photo.PNG](/assets/images/puller-photo.png)

You can see the bath there, currently covered. You can also see an orange wire connected to the alligator clip on the servo arm; this is because the sample acts as the other electrode in the bath, so it needs a lead to it. It can actually end up drawing a decent amount of current (~1A @ 40V), and can get a little bit warm. Luckily, it's never running for long, and it hasn't been a problem... yet. We shall see!

Let's now look at the electrical/software side, and you can decide if it's more or less of a trainwreck than what you just saw.

First, an aside on servos.

Servos work in a kind of strange way, in my opinion. While a regular DC motor basically just has plus and minus rotation directions, a servo has a clever feedback mechanism inside of it that allows you to specify an actual *angle*, which is obviously really useful. However, that's also going to need a bit more complicated control than the DC motor. The way I would have intuitively guessed that it would work would be that you supply a variable voltage within some range, and the voltage determines the angle.

The way it works is by supplying it with a PWM signal, which actually kind of makes more sense than what I guessed. A PWM signal is pretty easy to produce digitally, while a variable voltage can be a bit of a pain. Yeahhh, you can make a voltage divider with a pot... but my understanding is that simple voltage dividers are often pretty dependent on their load. Maybe you could use an Arduino or an external module to produce a variable voltage, but... I dunno, PWM signals are pretty easy to produce, even with something like a 555 circuit.

Okay, but it's actually a little more complicated than that. Normally PWM works by having a certain percentage of the signal on, known as the duty cycle. So to devices that depend on that, a signal with 1ms on out of a total period of 10ms (a 10% duty cycle at frequency 100Hz) would have the same effect as a signal with 2ms on out of a total period of 20ms (a 10% duty cycle at frequency 50Hz). That's normal PWM. However, servos are slightly different. They're expecting an alternating pulse wave (same type as typical PWM), but they look at the total *length* of the on signal, within a certain range. What that means is that, as long as the frequency (inverse of time between "on" signals) is in the acceptable range, you can change the angle by changing either the duty cycle *or* the frequency (or both, I guess). Let me quote the Wikipedia article on Servo Control for a minute:

> With many RC servos, as long as the refresh rate (how many times per second the pulse is sent, aka the pulse repetition rate) is in a range of 40 Hz to 200 Hz, the exact value of the refresh rate is irrelevant.

So, using the values I said above, the 1ms ON/10ms signal and the 2ms ON/20ms signal would *not* correspond to the same position! Same duty cycle, but different frequency. This is actually how I controlled the "first generation" of this project, when I just wanted to see if the concept worked without having to build a dedicated circuit: I used a function generator to produce a pulse wave with a duty cycle of 2% and then swept the *frequency*, keeping the duty cycle constant, because it didn't have the capability to sweep the duty cycle (which I would prefer; I think most people consider that more intuitive).

That being said, it hardly matters for this project, because I'm using an Arduino, and thus it has a "servo control" library easily available and easy to use. Let's get to the software part now.

Another motivation for this project was that I had a single color LCD screen (with an Arduino breakout module) lying around that I really wanted to use. I dunno, it just feels *so cool* when words you chose show up on that LCD screen in a standalone piece of equipment. Remember the excitement you got the first time you ever ran Hello World and it worked, and you saw the words in the terminal or IDE or whatever? The LCD version of Hello World makes that feel as exciting as naming types of screws.

Yet another motivation was that I wanted to learn about Arduinos a little. I knew what they were, basically, and had done some microcontroller stuff a *looooong* time ago, but I hadn't really used them, and I wanted to have at least a good starting point if I ever thought of a project, so I wouldn't have to spend a week floundering around to even begin.

So with these two components in mind, I put together the following device:

![img_20160901_181353082](/assets/images/img_20160901_181353082.jpg)![img_20160901_181409251](/assets/images/img_20160901_181409251.jpg)

Again, you'll notice some "were you drunk when you made this?" shoddy construction details. I grabbed these three big red momentary push buttons I had lying around, which is why it looks like a detonator a cartoon coyote would use or something. The hole for the LCD screen was roughly cut out with a jigsaw, so it's not that smooth or flush. The screws are very visible and obviously clash with the black color of the box. The bolt heads for the nylon standoffs on the bottom stick out.  My point is, I wasn't really going for cosmetics here.

Here are the outputs that go to the servo, which you plug banana plugs into:

![img_20160901_181252977](/assets/images/img_20160901_181252977.jpg)

Here it is with the screen on:

![img_20160901_181517730](/assets/images/img_20160901_181517730.jpg)

I'm actually a little proud of how well this works. I made it have a bit of a "user interface", where you go through several steps. First, you press the top two buttons to increase/decrease the total time in increments of 5 seconds. Then, you press the bottom button ("sel" = select) to go forward. It asks you if you're happy with your selection, and lets you proceed, or return. If you choose to proceed, it walks you through this little process that needs to be done.

See, the samples are often slightly different sizes, and you want to start the process with the sample lowered as far down into the bath as it can be without having the alligator clip touch the fluid. So, it tells you to raise the whole bar holding the servo mechanism up (the horizontal bar in the above picture of the mechanism), then you press "sel" when you've done that, it drops the servo arm, at which point you attach your sample and lower the horizontal bar such that the sample is where you want it to start the process. From here, you press "sel" one more time, and it begins the pulling process, which I've masterfully illustrated with a cutting edge graphics program:

![process](/assets/images/process1.png)

The code is probably badly written and *really* of no interest to anyone who isn't me, so I won't bother posting it. Here is something I wonder about though. In what I just described above, there are these "stages" to the user interface that basically form a [Finite State Machine](https://en.wikipedia.org/wiki/Finite-state_machine). At every stage, there are options for the buttons that you can press that will affect what state the thing is in. Now, I made it work, but the code was very quickly becoming cumbersome, because at each stage I had to check for different button presses, and send it back to various places in the code, and such. I'm wondering if there's a smarter way to do this... There probably is.

I'll finish with a couple of guts shots:

![img_20160901_175253037](/assets/images/img_20160901_175253037.jpg)

As you can see, most of this was done with an Arduino Yun (I have no idea what the deal with that one is, it's just what I had lying around), but I had another PCB to connect the many buttons/outputs/etc to the Yun easily.

You can also see that I used nylon standoffs to firmly connect the Yun and PCB to the box. I like how solid it makes it. There are many ways to do it, but I went for the easy, solid, but ugly way: just have the standoff bolts stick out the bottom.

![img_20160901_181200749](/assets/images/img_20160901_181200749.jpg)

Here it is all wired up. There are lots of wires, but there's still a decent amount of space so it's not a challenge to close the box. You can also see the back of the LCD: it actually has this little extra chip on it that makes it very easy to interface with, needing only 4 pins, as opposed to lots more if you didn't have that chip, maybe.

And finally, I'll end with an example of the finished product:

![aao](/assets/images/aao.png)

*Oooooooooooooooooh.*
