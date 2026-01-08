---
date: 2026-01-07 00:00:00-05:00
layout: post
permalink: something_fishy_pedal
thumbnail: /assets/thumbnails/something_fishy.jpg
image: /assets/thumbnails/something_fishy.jpg
title: "Something Fishy: BTDR Digital Reverb"
---

Here's a pedal I made a looooong time ago, but somehow it never escaped the drafts folder. No more!

It's a pretty simple reverb pedal, but it has a great sound. In contrast to most of the other pedal circuits I've put together, which were entirely analog, this one is based on a digital chip, the BTDR chip from Accutronics/Belton (I'm pretty sure it's the -2H version [here](https://stompboxparts.com/semiconductors/belton-btdr-2h-reverb-ic/)). Sometimes digital chips can have an actual noticeable bit of latency to them (I guess due to the signal processing time?), but somehow this chip didn't, possible because it's relatively simple.

I'm *pretty* sure [this](https://tagboardeffects.blogspot.com/2014/07/rub-dub-reverb-deluxe.html) was the circuit plan I was building, but I honestly don't remember. In fact, I don't remember a whole lot, so this post will be mostly the pics I had.

## The circuit

For previous pedals I had used [stripboard](https://en.wikipedia.org/wiki/Stripboard) to put together the circuits, which is pretty common for DIY pedals (in fact, you can see in the circuit link above that it's shown in stripboard!). It's cheap and real easy, but can become chaotic and looks a bit janky.

So I think I used... KiCad? or something, to make an actual circuit pattern, which I'd print out on a certain printer paper, which I'd then iron onto a copper plate, and then etch.

The design, working out the correct ironing settings:

![](/assets/images/img_20160915_222921580.jpg "IMG_20160915_222921580")

Design, ironed on:

![](/assets/images/img_20160915_232425103.jpg)

Such beauty:

![](/assets/images/img_20160918_195852820.jpg)

![](/assets/images/img_20160915_231359338.jpg)

Then, you do the etching (in Ferric Chloride), which etches everything that's not covered by the printer ink, and then you wash the ink away with a solvent, and only the copper traces remain:

![IMG_20160918_235013036.jpg](/assets/images/img_20160918_235013036.jpg)

Finally, I used a center punch (above) and teensy dremel bit to drill allllllllllllll those througholes.

Is this less work in the end than using stripboard? Absolutely not. Is it marginally cooler? I'll let you be the judge 😎

Here it is, installed in the enclosure:


<div style="
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  max-width: 600px;
  margin:0 auto;
">
  <img src="/assets/images/img_20170120_014149337.jpg" alt="Image 1" style="width:100%; display:block;">
  <img src="/assets/images/img_20170120_014159697.jpg" alt="Image 2" style="width:100%; display:block;">
</div>


You can see that for some reason I designed it so the pots were directly on the board, which is nice, but also made it pretty cramped. I did... not plan this one very carefully.


## Design

The most fun part of making a pedal is making the enclosure design. To me, this pedal has a real "watery" sound, so I used an MC Escher design and some free fonts to whip this up:

![](/assets/images/Pasted%20image%2020260108005117.png)


To get this design onto the metal enclosure, it's basically the same process as for the circuit board above, but with an extra step. I iron the pattern onto the metal with printer paper and the printer ink acts as a resist.

You then leave it in the same etching solution:

![IMG_20170113_244329425.jpg](/assets/images/img_20170113_244329425.jpg)

and it etches away the non-ink parts.

![IMG_20170113_010643774_HDR.jpg](/assets/images/img_20170113_010643774_hdr.jpg)

At this point you might think we're done, since it looks like the pattern we want is there, in black and metallic. However, there are two reasons it's not done. First, what do you do if you want a color besides black? 

Second, after etching, the etched parts are *sunken* and the inked part is only on the *raised* parts, so it's more exposed if anything, and on top of that, the ink isn't very durable. So what's more common is to wash away the ink, leaving this kind of ghostly looking pattern:


![IMG_20170112_240131724.jpg](/assets/images/img_20170112_240131724.jpg)

And *then* you paint the whole thing again (typically with spraypaint). Finally, you sand down the whole surface. Only the high parts (that were originally covered by the printer ink and *not* etched) will be sanded, leaving the paint in the recessed/etched areas.

Finally, you apply several coats of lacquer:

![IMG_20170119_095226634](/assets/images/img_20170119_095226634.jpg)

Pop some knobs on...

![IMG_20170120_113246419](/assets/images/img_20170120_113246419.jpg)

and tada!

![IMG_20170120_113258185](/assets/images/img_20170120_113258185.jpg)

It honestly amazes me how sharp you can get those images from etching. I mean on some level I'm not at all surprised, since I spent more hours than I'd care to admit in grad school doing nanolithography where you're essentially doing the same process but down to ~10's of nanometers of precision, but that was with an electron microscope, and this is with, you know, a clothes iron and consumer printer.

A funny thing I realized when I found this in my drafts is that when I made this ages ago, I just randomly grabbed a thematic Escher drawing for the design. But when I [went to the Netherlands about a month ago]({{site.baseurl}}/2025-11-16-netherlands) I visited the MC Escher museum (highly recommend!) and  saw an original print of this very one!

![](/assets/images/Pasted%20image%2020260108010645.png)

What's more, I didn't realize it at the time, but nearly all of Escher's works are various forms of woodcuts and lithography, which are (variants of) the same technique I used for these pedals. Time is a flat circle, etc etc.
