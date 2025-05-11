---
date: 2017-07-22 03:10:39-04:00
layout: post
thumbnail: /assets/images/thumbnails/orangeyaglad.jpg
title: 'Orange Ya Glad: first chassis design'
---

The first of many. So, so many.

So I've been making these guitar pedals. Ostensibly they're about cool musical effects, but, let's be honest: if you've seen any of them on the internet, it's at least half about how they look. People make *really damn cool* designs on their guitar pedals. One of my favorite guys who makes cool designs is [this guy Cody Deschenes](http://music.codydeschenes.com/), though he actually does a different design method than I've done here (which you'll see in a future post!).

I had assembled a couple pedals at this point but hadn't actually done any designs, so I was excited to. There are a handful of methods people use, but I decided to go for a fairly straightforward one. I followed [the method in this video](https://www.youtube.com/watch?v=xkvizYfDkxw), which is basically based on printing your pattern on a transparent sticker, sticking it to the pedal, and lacquering the hell out of it after. It doesn't give the most mindblowing results, but it's pretty decent for fairly minimal effort (compared to other methods).

It boils down to this:

1. Sand/clean/prepare chassis
2. Prime chassis (necessary? ehhh)
3. Spray paint several layers
4. Stick sticker on
5. Lacquer, like 5 coats (very important!)

Pretty simple. The sticker paper I used was the same as in the video, same with the paints, etc.

Actually, lemme briefly talk about the circuit itself for a minute. After the previous "worst fuzz pedal ever" I made, I kind of wanted one that didn't suck as much. I searched for a little bit and found that a pretty common one is the "Bazz fuss" (spoonerisms, wheee), and it's pretty damn simple. Here's a pic some guy drew of the basic schematic:

![small-fuss-layout](/assets/images/small-fuss-layout.jpg)

Reaaaaaaaal simple. Very vaguely, the transistor is acting as an amplifier, and the diode is probably creating distortion (because it lets nothing pass in one direction, and only stuff past its cutoff voltage, etc), and the pot is for attenuating the output signal/volume, etc.

Here's the thing. I looked at a bunch of different schematics for it, and they all seemed to have that R1 resistor set to either 10k or 100k, which is kind of a big difference. I honestly didn't know which to do, so I thought I'd split the difference and make it 47k.

Anyway, you can see that this circuit is crazy small. He drew it on a 5 x 10 stripboard, and it could probably be even smaller. I actually wanted to mount the pot directly on the board for this one, so I downloaded "DIY layout creator" (which is a kind of ghetto piece of software, but actually relatively easy to use) and made one of those nice looking stripboard layouts that suited my purpose:

![stripboard](/assets/images/stripboard.jpg)

The discerning reader will notice (just kidding, no one's paying that much attention) that the pot is actually not in the same place in the schematic that it is in the schematic above. The reason is that, I didn't particularly care about having a volume knob (I usually have like 3 different volume knobs available to me; why would I want another, rather than one that does something else?), so I replaced the original pot with 33k and 68k resistors, so it was kind of permanently set at 33% volume. However, I also read that adding a resistor between the transistor and ground (where it connects to ground) would affect the amount of fuzz. Therefore, I added a 5k potentiometer, and lo and behold, it does affect it.

Anyway, here are a few pics of that part.

Here's the teensy stripboard I was able to use. At the time of writing this, I actually tend to use the drill method for making stripboard breaks, but at the time I was still using a razor, and it's honestly pretty good as long as you make several deep cuts, scrape a little, and test the conductivity on either side of the cut well.

![IMG_20161216_013355154.jpg](/assets/images/img_20161216_013355154.jpg)

Here's the completed circuit. Insanely.* Teensy.*

![IMG_20161216_102651178.jpg](/assets/images/img_20161216_102651178.jpg?w=504)

Anyway, onto the chassis!

Drilled and cleaned:

![IMG_20161216_134303939.jpg](/assets/images/img_20161216_134303939.jpg)

Painting in my serial-killer-lair-looking basement:

![IMG_20161217_183424554.jpg](/assets/images/img_20161217_183424554.jpg)

Applying the sticker. I wanted to go for something silly and fun, and I'm partial to stupid puns, so... here we are. If you notice now, it doesn't look that great: the sticker parts looks a lot lighter:

![IMG_20161218_010653328.jpg](/assets/images/img_20161218_010653328.jpg)

I would be disappointed if it ended up like that, but...

![IMG_20161218_122100122.jpg](/assets/images/img_20161218_122100122.jpg)

...the lacquer really makes it pop!

A couple little details: I really like how the "faded" look came through in the font (that it's supposed to look like!). If you add a "border" like I did (credits to the above video), it's really hard to notice the boundary of the sticker. Lastly, they tell you to be really aggressive with smoothing out bubbles when you apply the sticker, but you're supposed to use a "rolling" motion and I guess I used too much of a "smearing" motion, because you can see that below the G in "glad", I smeared the ink a little. Oh well.

Electrical taping the inside, so we don't accidentally short something (the chassis is ground, as usual).

![IMG_20161218_123713572.jpg](/assets/images/img_20161218_123713572.jpg)

Adding the circuit: I actually could have probably spaced it out more. I really like this size chassis (1590A I think?), when you can use it. It's very compact and cute.

![IMG_20161218_124320827.jpg](/assets/images/img_20161218_124320827.jpg)

My great shame: At this point I wasn't using washers, because I'm stupid. When I went to tighten the nuts, my pliers I was using (also a bad idea...) gouged through the paint, down to the chassis metal... ugh. Learned a good lesson here.

![IMG_20161218_124329564.jpg](/assets/images/img_20161218_124329564.jpg)

The final product! It's a little hard to make out in this pic, but the knob is yellow, which I think goes with a general "citrus" theme.

![orangeyaglad](/assets/images/orangeyaglad.jpg)

![orangeyaglad2](/assets/images/orangeyaglad2.jpg)
