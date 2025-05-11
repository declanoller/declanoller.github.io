---
date: 2021-01-01 19:39:51-05:00
layout: post
permalink: /2021/01/01/making-diy-lenses/
thumbnail: /assets/images/thumbnails/IMG_20200117_181132-1.jpg
title: Making DIY lenses
---

I recently got a microscope, which has been tons of fun. In the process of learning and figuring out how to configure the optics to get a good image on my DSLR, I opened my old copy of Hecht's Optics to relearn stuff I ostensibly learned a while ago in undergrad.

It seems like the most common way the optics of simple lenses is taught is to derive a few basics about refraction, and then use those to justify ray diagrams and their "rules", and then basically just apply those rules to various combinations of interfaces to show the practical effect they have.  And they are pretty helpful for learning!

So while the ray diagrams you see in books (I'll be showing bits of an old version of Hecht here) are usually drawn, like:

![](/assets/images/IMG_20200610_215818-1024x611.jpg)

sometimes they like to show photos of real ray diagrams, made with beams of light going through lens systems in a dark room, like:

![](/assets/images/IMG_20200610_215852-1024x755.jpg)

Since I was learning about them anyway, I thought it'd be fun to try making a few and do it myself! You can obviously just draw out the ray diagram on paper, or use any number of programs to do it, but I thought it might give me a more intuitive feel to get to actually move them around and see how the results change. Also, what else am I gonna use a 3D printer for? :P

There are a few parts to this: the lenses, the light ray box, and others.

First, I'll mention that I decided to make only 2D lenses here, for a few reasons: 1) way less material, 2) ray diagrams are typically shown in 2D (and I'm not sure you really lose much between 2D and 3D anyway? is that right?), and 3) a ton of the problems people deal with when making lenses seem to be a lot worse for 3D than 2D. Maybe in the future I'll try some 3D ones.

![](/assets/images/IMG_20200117_181132-2-1024x996.jpg)

### The light ray box

A light box is pretty straightforward, but the main thing is that you need a light source that's collimated enough that it produces beams that don't spread very much over a long distance. I wanted to make a box that would be pretty flexible in terms of what it could do, and let me experiment with various settings. To do this, I designed it so the lights would go at the back, and then the rays that come out would depend on some insert panels with slits. I also wanted the LEDs (the light source) to be a nicely packaged little thing at the back. Here's the main part of the box in Onshape:

![](/assets/images/image-1-1024x534.png)

And a couple of the insets:

![](/assets/images/image-2.png)

I got some superbright white LEDs, and set up the circuit so it runs off a ~12V DC supply, so each LED should have ~15mA running through it. In practice, they seemed to be getting a bit too warm, and PLA is sensitive to heat, and I don't want to start a fire, so a 9V supply works better. I just used a grid of LEDs, soldered into a piece of stripboard that I cut to the size of the inserts. Here's the little package with the LEDs and a couple inserts:

![](/assets/images/IMG_20191231_035804-1024x737.jpg)

The box above is just about the max size I could fit on my tiny 3D printer, but I realized after fiddling with it for a bit that it would be better if it were longer. For example, if the slit inserts are too close together, you get these "cross rays" where the light from one slit spreads to the slits besides the other one it's supposed to go to in the next insert, messing up the collimation:

![](/assets/images/IMG_20200102_015707-1024x768.jpg)

Also, how collimated the light gets is partly a function of how far apart the slits are. Luckily, I designed it so it would be easy to make an "extender" that I could couple to the box using the slots for the inserts:

![](/assets/images/image.png)

With this addition, the collimation is pretty good to the distances I need, and still decent even at ~1m:

![](/assets/images/IMG_20200102_015104-1024x768.jpg)

![](/assets/images/IMG_20200102_015241-1024x768.jpg)

The PLA is actually pretty translucent, so I found that you get much better light blocking if you put a layer of black electrical tape on the inside. Another detail is that I can specify the slit widths of the inserts in Onshape, but 3D prints famously warp, and in my experience, the dimensions of negative spaces are *very* unreliable. Therefore, I tried a few and found that slits of ~0.7mm were good. The rays themselves don't actually have to be very thin, but the wider they are, the bigger an angular range they let through, making it less collimated.

### The lenses

If you do a quick search, you'll find that maaaany people have made lenses before, so this isn't original by any means. I've seen lots of DIY methods: 3D printing lenses directly, [machining and chemically polishing plastics](https://www.youtube.com/watch?v=7na8kQ78vkQ), casting epoxy into a mold, and cutting actual glass, to name a few. I'm not sure the direct 3D printing lenses end up good (you need to polish a lot to end up with any sort of optical clarity, and 3D printed materials tend to be pretty soft, and I'm not sure it could even work with filament printing because 3D prints aren't exactly homogeneous internally).

I wanted to try epoxy resin casting, which is fortunately a very common and relatively easy method. However, the devil (and bulk of hard work) is usually in the details. This part was way more involved than the light box, but I learned a lot of useful things.

I started by designing a couple lens molds in Onshape:

![](/assets/images/image.png)

and using some 2 part epoxy that I had around. This produced this sad looking specimen:

![](/assets/images/IMG_20200102_020202.jpg)

with the rays:

![](/assets/images/IMG_20200102_020039-1024x656.jpg)

You can see that it's...trying, but it's pretty lackluster.

First, this epoxy isn't very clear; I just used the stuff I have lying around for random household fixes. That's easily fixed; I searched "clear epoxy" and got some of that.

Second, you can see a ton of bubbles, which definitely mess things up. Epoxy is a popular DIY material and looks great when it's crystal clear, so getting rid of bubbles is a common hurdle. Some people use a blowtorch on the surface as it's curing, while others either cast it under vacuum or under pressure.

(Vacuum intuitively made sense to me: dropping the ambient pressure should cause bubbles to come out of the epoxy. However (see links below), it turns out that casting under *pressure* is more common. It seems like vacuum does bring out the bubbles... but the epoxy is so viscous that it ends up creating a bunch of foam, which is very bad. I guess under pressure, the bubbles might remain, but it squeezes them very small? But apparently, some people also successfully use vacuums for epoxy too. The epoxy lord works in mysterious ways.)

So, this led to me making a pressure chamber, following [this handy video](https://www.youtube.com/watch?v=eYL_Klfp3Lk). Now, "making a DIY pressure chamber" might sound like "making a shrapnel bomb" to the thinking man, but to comfort my poor mom, the pressures are real low. The guy in the video had pretty good success at ~20 PSI, and the pipe is rated to much higher than that.

Here it is! I just used a bike pump valve insert to pump it.

![](/assets/images/IMG_20200106_185732.jpg)

![](/assets/images/IMG_20200106_215246.jpg)

![](/assets/images/IMG_20200106_221956.jpg)

![](/assets/images/IMG_20200108_165943-1.jpg)

Getting it to maintain pressure was a whole awful process I haven't perfected yet. To be honest, I probably should've spent the ~$50 or whatever to just buy a steel pressure chamber that wouldn't have had this problem. When I pumped it to ~25 PSI, it would maintain for a little while, but would pretty much continuously leak until ~5 PSI, so if I wanted good results, I'd have to be around and repump it every little while. Ideally I'd pump it and leave it overnight to really cure, but this worked well enough to solve the problem. I tried using both teflon pipe fitting tape and this nasty PTFE pipe joint compound (wear gloves!).

![](/assets/images/image-1.png)

They helped, but I still had the problem. Anyway, here's casting some lenses with it:

![](/assets/images/IMG_20200108_165943-2.jpg)

![](/assets/images/IMG_20200115_084928.jpg)

Much better! You can see how clear they are. Pretty much no bubbles!

![](/assets/images/IMG_20200115_095449-1024x770.jpg)

What might look like bubble there is actually surface roughness, which leads me to the next tricky problem of this project: polishing. From what I've seen, pretty much no matter how lenses are made (this way, machining, or real ones with glass), polishing is a big part of it. Roughness at pretty much every scale is bad: large scale roughness will give you an effect of having a ton of clear but separate lenses/mirrors (like looking at a diamond ring), while small scale roughness will just give you blurriness.

When it comes out of the mold, it has a distinct pattern of the 3D print layers, and will produce basically no image rays:

![](/assets/images/IMG_20200109_180248-1024x608.jpg)

At this point I did many steps of polishing with increasing grit sandpaper (using a pack that goes from 2000 - 10000 grit).

![](/assets/images/IMG_20200116_132202-1024x768.jpg)

I sanded it with a bit of water, which seemed to work well. I didn't use a jig or anything (which would let you more precisely control the shape), and just rocked it back and forth while sanding. After a bit of sanding:

![](/assets/images/IMG_20200117_101857-768x1024.jpg)

Smoother, but still not there. After a bit longer:

![](/assets/images/IMG_20200116_135640.jpg)

Lastly, I used some polish by just rubbing it in with a cloth, which helped a bit more. I tried both Brasso and Flitz multi purpose polishes. I also tried using a cloth buffing wheel with my drill, and some polishing wax with my dremel and a foam/cloth bit, but I found those seemed to do something bad to the lenses (maybe melting them from being too high RPM? or collecting gunk? it wasn't clear.).

Anyway, time to put the pieces together! Here's the final product with the light box and a few of the lenses:

![](/assets/images/IMG_20200123_213640-1024x507.jpg)

![](/assets/images/IMG_20200123_213617-1024x446.jpg)

![](/assets/images/IMG_20200117_181132-1024x464.jpg)

Note that in some of the pics, the light is bluish and blurrier. I think this is because I tried using the "night mode" on my phone, which makes it brighter, but also blurrier. However, by eye, the rays were cleaner, more like the non-night-mode pics.

![](/assets/images/IMG_20200117_181034-1024x476.jpg)

There you can see that the center rays are decent, but the ones near the edge are pretty blurry. I'm not sure if that's an effect of the lens being non-negligibly wide, or just not being polished enough near the edges.

A couple diverging ones:

![](/assets/images/IMG_20200123_213707-1024x592.jpg)

![](/assets/images/IMG_20200123_213801-1024x768.jpg)

It's pretty cool that you can see the virtual image in that one! That's actually a sign the lens isn't that great, because it's making reflections, but it is pretty cool.

And some combos:

![](/assets/images/IMG_20200117_181404-1024x521.jpg)

![](/assets/images/IMG_20200123_214356-1024x768.jpg)

![](/assets/images/IMG_20200123_214235-2-1024x415.jpg)

It seems like there starts to be too many reflections and blurriness with more than one lens at this point, but I think I can solve that with a bit more tweaking.

Anyway, that's about all for now. There are a couple more little things I'll mention. When I first made the lens molds, I just made them as one piece like this, with a hole at the back to pop it out:

![](/assets/images/IMG_20200108_213313-768x1024.jpg)

This resulted in breaking them, because even with lubing up the mold with vaseline before casting, there's just a lot of surface area/friction with the sides. Instead printing two sides, which are held together with screws, worked a lot better, like so:

![](/assets/images/IMG_20200109_185738-768x1024.jpg)

![](/assets/images/IMG_20200115_091535.jpg)

![](/assets/images/IMG_20200110_111607.jpg)

This has the added benefit that I can mix and match sides in the future to make asymmetric lenses.

One last interesting thing is that, while the polish definitely helped, it didn't make it *glassy*. What did, though, was a little experiment I did of using nail polish on one lens:

![](/assets/images/IMG_20200116_135710.jpg)

Compare that one to the (polished) one above! It's nuts. I think what's happening is this: the polish "fills in the gaps" that remain at a microscopic level after polishing, and do an index-matching of sorts. However, the polish is pretty liquid-y and can only do so much. The nail polish is much more viscous, and I think it's doing the index-matching at the lens surface, but it also forms a very glassy and smooth surface (the side that's exposed to the air/incoming light rays) when it dries, due to how it dries. However, when I tried it with the light box (and you can tell a bit from just looking at that pic), the beams are a kind of wobbly. I think it actually adds back some large-scale roughness, because the nail polish itself adds some large scale waviness. Out of the frying pan and into the fire. Still, maybe it could work in some other way, so I'll keep it in mind for the future.

See ya next time!
