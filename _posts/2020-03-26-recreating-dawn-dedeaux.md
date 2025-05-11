---
date: 2020-03-26 14:59:36-04:00
layout: post
permalink: /2020/03/26/recreating-dawn-dedeaux/
thumbnail: /assets/images/thumbnails/euler_smeared-4.jpg
title: Recreating Dawn DeDeaux
---

I've done [several]({{ site.baseurl }}/2019-09-13-making-sol-lewitts-colored-bands-interactive-with-d3-js/) little [projects]({{ site.baseurl }}/2019-06-21-programmatically-recreating-sol-lewitts-all-two-part-combinations-of-arcs-from-corners-and-sides-and-straight-not-straight-and-broken-lines-with-d3-js/) previously about recreating art I saw at MASS MoCA, but they were Sol LeWitt pieces. His definitely stood out to me the most, but some other ones really caught my eye too.

One of them was the artist Dawn DeDeaux's "The Vanquished Series: G-Force #1 and #2". Here are a few pics I took:

![](/assets/images/IMG_20190616_130329-768x1024.jpg)

![](/assets/images/IMG_20190616_130326-768x1024.jpg)

As I recall, she had some other work there, but there were only a pair of these. I like them a lot. At a glance, you can see that they're both figures, that have had some process done to them that gave them this recognizable yet pretty unearthly and alienating look. I knew I had to try making these! I'm curious how she did this. Is she also a python-er?

Let's look at a few close-ups I took:

![](/assets/images/IMG_20190616_130334-768x1024.jpg)

![](/assets/images/IMG_20190616_130356-768x1024.jpg)

So we can see the main idea pretty easily: they were pixelated into little equal sized squares, and then smeared/exploded, such that they left trails behind them. The trails are different colors, so I took a guess that the trail color of each square was probably the mean color (however you define that, since color spaces are weird).

Here's the progression of what I did! I just used [Pillow](https://pillow.readthedocs.io/en/stable/) (PIL) and numpy basically. The main idea is this: import the image with PIL, convert to a numpy array, calculate a bunch of <code>PixelBlock</code> namedtuples:

<code>PixelBlock = namedtuple('PixelBlock', ['pixels', 'avg_color', 'block_corner', 'x', 'y', 'w', 'h', 'block_center_rel'])</code>

Then, for each <code>PixelBlock</code>, plug its location (relative to the center of the image) into a vector field that will determine where it gets sent to. This gives the "final" location of that block. Then, chop that path up into many steps and overwrite the pixels of the image's numpy array with the constant mean color for that block. Finally, overwrite the pixels of the final location with the pixels of the original <code>PixelBlock</code>. There are a bunch of details, a few of which I'll mention but most of which I won't.

Note that with this method, since you're necessary overwriting pixels/have some on top of others, you have to do them in a certain order: outside in. To do this, I just sort them by the norm of each <code>PixelBlock</code>'s <code>block_center_rel</code> attribute (i.e., the coordinates of that <code>PixelBlock</code>'s center, relative to the center of the image).

I think we get pretty far with this off the bat! Here's an example of mangling dear Euler, along with its corresponding translation per <code>PixelBlock</code>:

- 
- 

And one with much finer blocks:

![](/assets/images/euler_smeared_pos_1pt0_fixed.jpg)

However, it's still missing a lot. One is that here I just used a translation vector field of the form $f(x, y) = x \hat{i} + y \hat{j}$, which is just sending "spreading" all the blocks out uniformly. Clearly, way more is going on in the originals. To fix this, I just added a "jitter" term to each, a <code>np.random.randn(2)</code>. That definitely improves it a bunch:

- 
- 

![](/assets/images/euler_smeared_200.jpg)

Definitely getting closer. Next, I took a closer look at one of my bigger block sized images and compared it to the close up of the original (check them out above). Notice anything different? Yep, the trails in her image actually aren't one color, they're two! The mean color seems like a decent guess for one of them, but the pair seems to always be one color plus a lighter version of it. Additionally, the lighter side is always in one direction, like below, on the top side:

![](/assets/images/closeup.jpg)

Also an easy change:

![](/assets/images/euler_smeared-1.jpg)

It has the effect of adding a sense of depth, because now it looks like something 3D that was lit directionally.

Anyway, it's pretty good at this point, but not quite there. One big reason is that if you go back to the originals, you can see that they're not just randomly jittered straight lines, they definitely have curvature, sometimes pretty strongly:

![](/assets/images/curve_closeup.jpg)

This meant changing the method slightly, since before I was just relying on the final destination of the block. Now I had to define a vector field, and step through the path of the block as it travels through it. At this point it becomes a little more... art than science, as they say. To get some quick easy curvature, I just apply a rotation matrix at each point:

![{\displaystyle R={\begin{bmatrix}\cos \theta &-\sin \theta \\\sin \theta &\cos \theta \\\end{bmatrix}}}](/assets/images/fe4ee3f1ce8e028da5bd4219c9dc7fc2216543e4)

but, make it so the angle of rotation $\theta$ itself, is a periodic function of the distance from the center of image: $\theta = \mathrm{cos}(2 \pi r/r_{max})$

Which gives a vector field of the form:

![](/assets/images/vec_field.png)

Applied to the image, we get:

![](/assets/images/euler_smeared-2.jpg)

![](/assets/images/euler_smeared-3.jpg)

Definitely getting that weird look!

There's one last major mod. If you check the original again, you can see parts with really high curvature. There are probably lots of ways to do this, but I decided to just add little "whorls" randomly. By a whorl, I basically mean the same type of rotation field as applied to the whole thing, but applied to a local region and made to drop with distance much faster.

Like I said, at this point, there's some art to choosing the parameters that determine the strength of the effect, how fast it falls off, etc. If you mess them up, you quickly get some Cronenberg-esque monstrosities:

![](/assets/images/euler_smeared_horror3.jpg)
*"My existence is torture!"*

This hellbeast is actually the result of using a whorl as described above. Because a rotation field just looks like spinning around the origin, it causes the "outgoing" original field from the center to "collide" with the whorl's field going in the opposite direction, giving rise to that diverging horror area near his...no, its mouth. To make this less awful, I made it so it rotates around the whorl in opposite directions, depending on which side the point is on the whorl, like a stream going around a rock.

Lastly, you might have noticed in the last one, the demon Euler, the blocks were someone grid-like away from the whorl. This is because while the simple original single vector method above can be jittered by just adding a small random vector to each block's path, now the path is formed of many vectors. Therefore, to get that same randomness, we multiply each block's path by a small rotation matrix *after* the path has been calculated.

Finally, all together, here are a few outputs:

![](/assets/images/euler_smeared-4.jpg)

![](/assets/images/saturn_smeared.jpg)
Bonus points if you can recognize this one!

![](/assets/images/hiero_smeared.jpg)

![](/assets/images/moondog_smeared.jpg)
I'm so sorry, [Moondog](https://en.wikipedia.org/wiki/Moondog).

There are actually still a few little details I have to get down, but I think I'll stop here. The code repo for this [is here](https://github.com/declanoller/dawn-dedeaux-smear-art). See ya next time!
