---
date: 2017-10-10 21:56:40-04:00
layout: post
permalink: 2017-10-10-a-spoooooooooky-project
thumbnail: /assets/images/thumbnails/bloodhead1.jpg
title: A spooOOOOoooky project!
---

This is a fun one.

It's also a testament to how nifty and easy it is to quickly whip up a project with Arduinos, provided you have enough of a "critical mass", as I've called it before, of other stuff that you might end up needing.

How was this one born? Well, there was a Halloween grad student party our school was throwing, on a Friday night. It's... honestly, really the type of thing I, or any grad student, should go to. We're mostly isolated from other grad students, and these parties have typically gotten pretty raucous when I've gone to them. However, that night, I really wasn't feelin it. I got home from work/the gym kind of late, hadn't eaten, and the party was downtown. I think it might've also been raining or something, adding to the "I don't want to go out" side of the scale.

So did I suck it up, shower, and eat something quick? Did I go party like a cool person?

YOU BETCHA

...if by "party" you mean, stay home and mess around with Arduinos, then YEAH I PARTIED.

At the time (well, about two months prior...) I had gone on an Aliexpress spree, ordering literally any object if it was like, two bucks or less. I had this constant influx of sketchy-ass looking packages from China coming in. It was like xmas every day; it was glorious. So one of the latest things I had got was a little water pump. [Here's the link for it](https://www.aliexpress.com/store/product/Anself-Ultra-quiet-Mini-Water-Pump-DC12V-4-2W-Brushless-Water-Oil-Pump-Waterproof-Submersible-Fountain/1466008_32691301212.html), though who knows how long it will work. Here are a couple pics:

![pump1](/assets/images/pump1.png)

[gallery ids="1613,1614" type="rectangular"]

12V, 4.2W, meaning about 300mA. Pretty hefty current draw, actually. I'll get back to that later.

Now, I wanted to use this new toy I had gotten... but I also wanted to make something halloween related. *And then it all came together.*

This probably wouldn't happen in most other houses, but in our house, we have stuff like a creepy foam head lying around. It was too perfect; I realized what I had to make.

Naturally, I had to make the head vomit blood.

In addition to the pump, I had also recently gotten a ton of sensors from Aliexpress. The goal: make a proximity sensor trigger the pump to squirt fake blood out of the head's mouth for a few seconds. I actually had... sheeeit, maybe 3 different motion sensors? I had two IR ones and one ultrasonic one. My roommate (also being super cool and staying home to Arduino rather than going out and having fun) took one of the IR ones and I took the ultrasonic one, and we basically raced to see who could get it working the quickest. It's not to say one or the other wasn't superior, but at that point we really just wanted to get it working.

We both set to googlin' for example code other people had written to copy and modify for our uses. It turned out mine was easier to get working, I guess. [Here's a link to it on Sparkfun](https://www.sparkfun.com/products/13959) (hint: it was about a quarter of the price, including shipping, on Aliexpress, for the same exact product), and here's what it looks like in case that link dies:

![hcsr04-stm32f4xx](/assets/images/hcsr04-stm32f4xx.jpg)

This is one of the great things about Arduinos. I wanted to get it working, I googled its name and Arduino, or something, found [this page](http://randomnerdtutorials.com/complete-guide-for-ultrasonic-sensor-hc-sr04/) with some example code, and had it working in like *two minutes.*

I mean, on some level it's not that crazy. It means stuff was working as it should have, and this stuff is fairly standard. But the great thing about it is just how much stuff is out there, that I could google it, knowing nothing about it, and have it functioning so quickly.

Anyway, so that's kind of half the problem solved. The other half involves getting the pump to work.

I was using an Arduino Micro (no reason why, just had it around). I wanted it to make the pump run, but the pump needed about 300mA, and you obviously can't source that from an Arduino output pin (or even the power pins, I think). So, I needed some sort of current activated switch. Now, ideally, I'd go for a relay. Relays have their downsides (obviously they're not gonna be switching too fast, they need a pretty decent amount of current to switch, etc), but they're also simple as hell, so that's what I'd like for a simple project like this, if I had the option.

Unfortunately, I only had 12V relays sitting around, and the Arduino pins can only do 5V. But, I *did* have some random transistors sitting around. Now, I don't know a ton about using transistors as switches, so I googled "2n7000 used as switch" and got exactly what I needed pretty quick.

I basically connected the pump in series with the power source, through the transistor, so when the Arduino set its output to high, it would let current flow through the pump, directly from the power source I was using, 12VDC I believe. Here's a derpy schematic I made, since I have no idea what I'm doing in Fritzing and don't really wanna spend the time to learn:

![bloodhead pump schematic.png](/assets/images/bloodhead-pump-schematic.png)

(And of course, you also need to power the HR S04, with 5V, I believe.)

Anyway, without further ado, lets see some pics!

![img_20161117_103844583](/assets/images/img_20161117_103844583.jpg)

This was actually taken long after it was built. You can see that the fake blood has crusted on top. It was actually pretty tasty, because it was water, corn starch, food coloring, and cocoa powder (pro tip: add a bit of green food coloring, it makes it a little browner!).

The head basically just sits in the blood reservoir, so when the blood comes out of the mouth, it returns to the pool.

![img_20161117_103852471](/assets/images/img_20161117_103852471.jpg)

This was pretty quickly made and obviously jury rigged. The foam head would float in the fake blood, and otherwise be unbalanced, so I had to strap it down by sticking that brass pipe through the neck and attaching that to the cookie pan through a drilled hole with wire. You can see the pump sitting there, with just the input pipe submerged.

![img_20161117_103901701](/assets/images/img_20161117_103901701.jpg)

Another shot. I rammed another brass pipe through the back so it could squirt blood out the mouth.

![img_20161117_103927151](/assets/images/img_20161117_103927151.jpg)

The brass pipe is actually a bit set back from the lips, and I used a knife to widen the mouth hole so it spread out more. Truly gruesome!

![img_20161117_103912143](/assets/images/img_20161117_103912143.jpg)

Here's a photo of the above circuit. The only difference is that I added an LED that also gets turned on when the pump gets turned on, so I could know that it should be getting triggered, if it for some reason wasn't. That's it! Pretty simple.

Now... let's talk about the bad news. I noticed that, if you triggered it a few times in a row continuously, the transistor would get *really damn hot*. As in, too hot to touch without burning yourself (the worst I've ever experienced was one when I plugged in a beefy 7805, the type that has be used with a heat sink, but it actually had a weird atypical pinout, so when I connected it the normal way, it went into thermal shutdown. It wasn't working so I squeezed it tightly between my thumb and forefinger to see if it was warm and I swear there was an audible *sizzle*. It blistered up; won't be making that mistake again).

Anyway, I guessed that the dinky little TO-92 package of this transistor (2N7000) probably couldn't handle the 300mA the pump was drawing (in fact, it might be more, since, as the saying goes, the blood was definitely thicker than water, causing the pump to strain more). Taking a look at the datasheet confirms this (I think), since the maximum continuous drain current is 200mA. I've since ordered some 5V relays that the Arduino can switch, so maybe next time I'll use them.

Here's a video of it working:

![](/assets/images/VID_20161029_173446472.gif)

Not that it'll probably ever help anyone, but here's the code I used:

> int trigPin = 11; //Trig - green Jumper
> int echoPin = 12; //Echo - yellow Jumper
> int ledPin = 6;
> long duration, cm, inches;
> void setup() {
> //Serial Port begin
> Serial.begin (9600);
> //Define inputs and outputs
> pinMode(trigPin, OUTPUT);
> pinMode(ledPin, OUTPUT);
> pinMode(echoPin, INPUT);
> }
> void loop()
> {
> // The sensor is triggered by a HIGH pulse of 10 or more microseconds.
> // Give a short LOW pulse beforehand to ensure a clean HIGH pulse:
> digitalWrite(trigPin, LOW);
> delayMicroseconds(5);
> digitalWrite(trigPin, HIGH);
> delayMicroseconds(10);
> digitalWrite(trigPin, LOW);
> // Read the signal from the sensor: a HIGH pulse whose
> // duration is the time (in microseconds) from the sending
> // of the ping to the reception of its echo off of an object.
> pinMode(echoPin, INPUT);
> duration = pulseIn(echoPin, HIGH);
> // convert the time into a distance
> cm = (duration/2) / 29.1;
> inches = (duration/2) / 74;
> if(inches<50){
> digitalWrite(ledPin, HIGH);
> delay(5000);
> }
> else{
> digitalWrite(ledPin, LOW);
> }
> Serial.print(inches);
> Serial.print("in, ");
> Serial.print(cm);
> Serial.print("cm");
> Serial.println();
> delay(50);
> }
