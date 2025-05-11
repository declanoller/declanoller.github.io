---
date: 2018-08-20 14:10:13-04:00
layout: post
permalink: /2018/08/20/neato-sequence-art/
thumbnail: /assets/images/thumbnails/ex_color_recaman_100terms_x00_2018-07-27_14-59-10.png
title: Neato sequence art
---

A while ago I watched [this video by Numberphile](https://www.youtube.com/watch?v=FGC5TdIiT9U) (a very cool channel!). In terms of the actual math, it's pretty light, but what I love about it is the idea of creating very cool images via very simple rules.

The idea of it is this. In the video, the guy shows a way of drawing a sequence of numbers (more on that in a minute). You draw a number line, and then you draw a semicircle *above* the line from the first number of the sequence to the second, with a diameter equal to the distance between the points. Then, you draw a semicircle from the second to third numbers of the sequence in the same way, except this time, the semicircle goes *under* the number line. You continue this way as long as you want, alternating above/below for the semicircles.

So here's what the design for the first few Fibonacci terms looks like:

![](/assets/images/fib1.png)

This is neat, but to be honest it's not super interesting if it's just a monotonically increasing function; the bigger range you show, the more detail you're going to lose for the smaller numbers/differences. So what really makes it is when you have a cool sequence that has more interesting behavior for a given range.

In the video, he uses [the Recaman sequence](http://mathworld.wolfram.com/RecamansSequence.html) as his sequence. The Recaman sequence is interesting. It goes as follows: starting at 1 (though you could definitely start elsewhere), each turn, you have a number you're either going to subtract from, or add to, the current number of the sequence, to get the next number of the sequence. You subtract if the number that would result hasn't been seen yet in the sequence (and is greater than 0), but if it has, instead you add that number to get the next in the sequence. The number you're either adding or subtracting each iteration starts at 2 and increases by 1 each iteration. This is often stated as "subtract if you can, add if you can't".

For example, starting at 1: you have to subtract or add 2. You can't subtract (<0), so you add and get 3. Now, you have to subtract or add 3 to 3. Again you can't subtract, so you add and get 6. Now you have to subtract or add 4, and you can subtract, so now you're at 2. Next, add 5 to 2 to get 7, and so on...

Let's just skip to the pretty pictures. Here it is for the first 20 terms:

![](/assets/images/recaman_ex1-1024x768.png)

Very neat! You can get an idea of the behavior: if you get a term that's kind of far out enough that it has space for it and nearby terms to subtract for their next term, but close enough to 0 that its subtracted terms *aren't* big enough to subtract (so, they have to add), you get these sections of multiple adjacent terms (like the bunch towards the left in the above pic), which looks awesome in my opinion.

What's also very cool to me is that it has this awesome, strange behavior where it definitely tends to increase as the sequence goes on, but it leaves little gaps so the sequence eventually goes waaaaay back from a higher number. In contrast to what I was mentioning above about how something like the Fibonacci sequence isn't that interesting because you only really get to "see" one scale, for the Recaman you really get to!

Here are a few more, showing more and more terms.

N = 40:

![](/assets/images/rec40-1024x768.png)

N = 100:

![](/assets/images/rec100-1024x768.png)

N = 480:

![](/assets/images/rec480-1024x768.png)

One thing that's interesting to me about the Recaman Sequence is that I've never seen this mechanism for generating a sequence before. Probably the simplest sort of sequence is more like a function, where you can just say a<sub>i</sub> = f(i). That is, you can calculate what the i-th term is by itself. For example, maybe just a geometric sequence like 1, 2, 4, 8, ... where it's just a<sub>i</sub> = 2<sup>i</sup> . The next simplest type is probably recursive, where you define each term in terms of one or more preceding terms, like a<sub>i</sub> = f(a<sub>i-1</sub>) or something. So, the Fibonacci or Collatz sequences are good examples of this. The important part is that for a recursive sequence, you usually can't just calculate the ith term by itself, you need all the preceding terms to get there (unless the recursive relation is so simple that it has an obvious mapping to the first type of sequence I mentioned; i.e., that one could also be defined as a<sub>i</sub> = 2a<sub>i-1</sub>).

So the Recaman is recursive for sure, because it's either subtracting from/adding to the current term to get the next. But the part that makes it unlike any other I've seen is its method for "forking" (choosing to subtract or add, basically an if/then statement): while some (see the Collatz, Tent, below) also fork at each term, they fork based on some objective, stable property of the term (i.e., is it even or odd). However, the Recaman is essentially keeping a *register* of visited values, which is something I've never really seen before in sequences. One thing I briefly experimented with was making a "double Recaman" sequence, where the "register" allows you to go to the same point twice, but no more. So it definitely looks a little different, and you can see it forking from the same point, where it went one way after its first visit to the point, and another way its second.

Double Recaman, first 30 terms:

![](/assets/images/doubleRec_30terms_x01_2018-08-20_09-33-01-1024x768.png)

So that's the Recaman.

But what else can we do?

Let's try a few other sequences!

We can't go without [the famous Collatz sequence](https://en.wikipedia.org/wiki/Collatz_conjecture). The rule is just "divide by 2 if it's even, do 3*x+1 if it's odd". You can start wherever, and the length of the sequence produced ("ending" when it gets to 1) is *very* erratic with where you begin. For example, x0 = 26 has 11 steps, while x0 = 27 has 111.

x0 = 19:

![](/assets/images/collatz19-1024x768.png)

x0 = 27:

![](/assets/images/collatz27-1024x768.png)

The Collatz is cool because it has the backtracking effect the Recaman has, but tends to get monotonically larger, looking kinda like a seashell.

How about [the Tent map](https://en.wikipedia.org/wiki/Tent_map)? It's pretty simple, but very cool. For x between 0 and 1, if x is less than 1/2, it returns 2*x. If it's greater than or equal to 1/2, it returns 2*(1-x). It bounces around like crazy, but is unfortunately pretty confined to the 0,1 range.

Tent, x0 = 0.47, 80 terms:

![](/assets/images/ex_tent_80terms_x00.47000000000000003_2018-07-27_14-28-36-1024x768.png)

Tent, x0 = 0.26, 80 terms:

![](/assets/images/tent_80terms_x00.26_2018-07-27_14-28-36-1024x768.png)

There are a few others, but to be honest I couldn't find too many others that look distinguishable from one of these.

Okay, patterns are cool, but how can we make them cooler?

One thing I tried was making a triangle whose height is dependent on the difference, instead of a semicircle:

Collatz, x0 = 263, 30 terms:

![](/assets/images/tri_ex_collatz_tri_30terms_x0263_2018-07-27_16-11-13-1024x768.png)

Recaman, 50 terms:

![](/assets/images/ex_recaman_tri_50terms_x01_2018-08-19_21-21-33-1024x768.png)

I really like these, actually. The more random ones like Collatz look kind of like a mountain range to me.

I wanted to spice it up a bit more though! One thing I tried was making the color of the circle dependent on the radius of the semicircle. Here's how it came out:

Tent, x0 = 0.26, 80 terms:

![](/assets/images/ex_color_tent_80terms_x00.26_2018-07-27_15-01-49-1024x768.png)

Collatz, x0 = 43, 200 terms:

![](/assets/images/ex_color_collatz_200terms_x043_2018-07-27_15-00-19-1024x768.png)

I think it looks slightly better in black:

Tent, x0 = 0.42, 80 terms:

![](/assets/images/ex_color_black_tent_80terms_x00.42_2018-07-27_15-02-56.png)

One thing I didn't love about this is that when two semicircles of very different sizes meet, the color changes abruptly, which I don't think looks great. However, because of the way Recaman tends to have large sections of similar sized semicircles, it actually comes out looking pretty neat!

Recaman, 100 terms:

![](/assets/images/ex_color_recaman_100terms_x00_2018-07-27_14-59-10.png)

However, I still wanted a way to make colored ones without that abrupt color change. To do this, I used the triangle one (which would have the same problem as the above if I just naively colored it by the size of triangle), but with a slight change. It still has a color based on the triangle size, but the color of each fades to black as it approaches the number line. This makes all colors blend together nicely!

I also messed with the line widths here a little, because some looked better than others.

Recaman, 50 terms:

![](/assets/images/ex_color_fade1_recaman_tri_50terms_x01_2018-08-19_19-59-08.png)

Collatz, 30 terms, x0 = 263:

![](/assets/images/ex_color_fade2_collatz_tri_30terms_x0263_2018-07-27_16-22-33.png)

Recaman, 100 terms:

![](/assets/images/ex_color_fade3_recaman_tri_100terms_x00_2018-07-27_16-19-09.png)

Tent, x0 = 0.47, 80 terms:

![](/assets/images/ex_color_fade4_tent_tri_80terms_x00.47_2018-08-19_22-15-35.png)

At this point I tried to do a few original things, rather than just riffing on what they came up with. I thought, dang, this simple idea was really cool, maybe it's easy to come up with other cool sequence art!

It turns out it is not. Here's what I tried. Similar to the stuff above, I'm connecting sequence terms to the ones following them. However, this time, it's like there are two number lines, perpendicular to each other, with their 0 points overlapping. The line each sequence term is drawn from/to alternates. I also do the line color/line length thing as above, and also the thing with the fade (where it fades towards either edge).

Here's an example:

Recaman, 50 terms:

![](/assets/images/recaman_BOX_50terms_x01_2018-08-19_22-38-55.png)

Then, to add a bit more interest, I rotate it 4 ways:

Collatz, x0 = 27, 115 terms:

![](/assets/images/collatz_BOX_115terms_x027_2018-08-19_22-40-29.png)

Tent, x0 = 0.47, 80 terms:

![](/assets/images/tent_BOX_80terms_x00.47_2018-08-19_22-50-51.png)

Unfortunately, it doesn't look thaaaat cool in my opinion, and there just don't seem to be much variation once I make 5 or 10 of them.

Recaman, 1000 terms:

![](/assets/images/recaman_BOX_1000terms_x01_2018-08-19_22-55-39.png)

One thing I think is kind of cool is that, I do the 4-fold symmetry thing in each step (as opposed to drawing the whole sequence and then rotating it 4 times). This creates some cool "weaving" effects, like in the last one (look at the dark red and green in the corners).

Welp, that's all for now. It's definitely inspired me to make more math/programming generated art though, so look for that in the future!
