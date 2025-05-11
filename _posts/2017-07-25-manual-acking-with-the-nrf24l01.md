---
date: 2017-07-25 16:54:28-04:00
layout: post
thumbnail: /assets/images/thumbnails/img_20161127_175851992.jpg
title: Manual ACKing with the nRF24L01
---

This one will be very basic to most people who have done this, but it would have been helpful to me when I started with this stuff, so I’m putting it here.

First, a little background:

In the past couple months I’ve been messing around with the nRF24L01 (just gonna call them nRF’s from now on) radio frequency (RF) modules. Arduino hobbyists love them because they’re cheap (it seems like their competitor in this arena were Zigbee chips, which people seem to say are good but very expensive) and relatively versatile and powerful. They operate in the 2.4GHz frequency range and can actually get a pretty hefty amount of range! My roommate and I did a “range test” where I took one nRF that was just spraying out a constant stream of data, and he took another nRF with an LCD attached that displayed the received data. We went to a nearby park, and literally couldn’t get far enough away from each other to make the data stop being collected, which was about 1000′ according to Google Maps. They’re a lot of fun and really open up some project possibilities, which I’ll put here as I do them.

There are several libraries volunteers have written for them, most notably the RF24 library, which has a handful of good examples when you install it with the Arduino IDE. Now, I really do appreciate that, I know that absolutely no one has to write them, so I’m just lucky that they exist. I really do appreciate that. But, let me kvetch for a minute. I’m basically used to a standard with Arduinos where any relatively easily bought module/etc is documented *out the ass* on the internet in the form of tutorials, guides, example programs, forum posts, etc. This has been one of the least documented modules I’ve seen (just to be clear, not literally the class/library documentation, because there is that for this library. I just mean general online resources). There’s the class documentation online ([here](https://tmrh20.github.io/RF24/classRF24.html)) and some examples that come with the library. Those examples have probably been the most helpful, just because they allow me to butcher working code and figure out the ins and outs. However, tutorials (not related to the library dev/maintainer) are sparse, and most of the ones I’ve seen are pretty handwavy. I’m not sure if it’s because the people writing those don’t actually know much about it themselves (I suspect for some that’s the case), or they just don’t want to go into unnecessary detail. But, either way, it has not been easy.

ANYWAAAAAY

So, here’s what this post is about. Let’s say you have two RF modules, A and B, in different locations, and you want to send some data from A to B. However, they’re pretty far apart, so the signal is weak and it may not always reliably get there. Now, you could just do it naively by sending out all the data from A, to B, and hope it gets there. Depending on your application, this might be fine (obviously, when you listen to music on the radio, they just send it out and you hear what gets to you. A little different cause that’s analog and this is digital, but the concept works).

But let’s say you really care about making sure the data gets there. How could you do that? Well, if it were two *people* (A and B) yelling to each other across a distance on a windy day, it might make sense for them to come up with a system beforehand, where B could verify when he got what A was saying. So maybe A yells *GURK* and B hears it, so B yells back *SMYIRT*, and A knows that means that his buddy got the message, so he can go on to the next one. Alternatively, maybe B doesn’t hear anything, or it’s unintelligible, so he waits like they planned. A doesn’t get a SMYIRT back for a while, so he tries yelling GURK again. Maybe it works this time, but maybe it doesn’t, and then after trying for a few more minutes they decide it’s not gonna happen, and give up.

This is pretty much what you do with RF communications if you care about data fidelity. The data B sends back in response is called the “ACK” for “acknowledge”. Often, A will be sending real data of substance, while the ACK B sends will be just a tiny data packet to let A know.

Now, the RF24 library actually has a lot of ACK functionality, and several of the example sketches cover it. I was able to get a couple of the examples working with my setups easily. However, I still chose to manually implement my own example ACK system, for two reasons.

The first is that, honestly, I spent some hours trying to figure out how to ACKtually (HAHAHAHAHAHAAHHAHA AHAHAHAHAHH AHAHAHHAH) use the library’s tools for handling ACK, and I really came up blank. Like I said before, the online documentation for this is sparse. The library documentation itself tells you what the functions *do*, but anyone who’s used any non-trivial function for anything knows that there’s more than just the inputs and outputs. The example sketches have decent comments in them, but it’s still unclear why most of the stuff is happening.

The other reason is that I wanted to kind of understand it a little more internally, which I do now. I understand the basic concept, but there are usually subtleties to this stuff.

So, on to the juicy stuff. Some actual substance.

Below is my setup. I have two identical nRF/Arduino pairs:

![full.jpg](/assets/images/full.jpg?w=462&h=491)

As you may or may not be able to see, I’m using Arduino Pro Minis (PM). I’m actually doing this in anticipation of the next part of my project (super low power operation). I should say that they are the 3.3V/8MHz ones, which is nice because it means I can power them off the same rails as the nRF. I should also say that, though it seems like it can sometimes work, you really don’t want to power the nRF from any Arduino pins. Arduino pins are often very current limited, and from what I’ve read, power issues are a big source of trouble with the nRF.

![IMG_20161127_175851992.jpg](/assets/images/img_20161127_175851992.jpg?w=516&h=398)

The nRF runs at 3.3V. You *must* supply that to its power pins, but the data pins can work with 5V. One other thing you may notice is the capacitor on the left side. Some people seem to say that you want a capacitor across the power rails as close to the nRF’s rails as possible (some people solder it directly onto the nRF). From what I’ve tested, it seems to not matter (maybe because I’m already using a somewhat regulated power supply).

So, I have both PM’s connected to my PC the whole time, so that I can read stuff on their serial ports. Because they’re plugged into different USB jacks, I can open another instance of the Arduino IDE and have a serial monitor for each one. Right now I’ve made the one of the left the transmitter, the one on the right the receiver.

Here was my goal. I wanted the transmitter to send a message (an integer) to the receiver, the receiver to increment that integer, and send it back as an ACK, and the transmitter to increment the ACK and repeat if it got it. If it didn’t, keep sending the same one. There are lots of ways of doing this, but my main goal at this stage was a “robustness” such that no packets were missed and everything was happening in a very steady, understood way. Thus, the way I’ve done it is certainly inefficient and slow, but whatever, it accomplishes its goal.

So, here’s the code:

```python
#include
#include “nRF24L01.h”
#include “RF24.h”

const uint64_t pipes[2] = { 0xABCDABCD71LL, 0x544d52687CLL }; // Radio pipe addresses for the 2 nodes to communicate.
RF24 radio(7,8);

//State stuff
bool sender = 1;
bool receiver = 0;

bool ROLE = receiver; //CHANGE THIS LINE TO CHANGE ITS ROLE

bool prim_send = 1, prim_rec = 0, prim_role;
bool temp_send = 1, temp_rec = 0, temp_role;
bool msg_recvd = 0;

//msg stuff
unsigned long msg = 1;
unsigned long ACKmsg = msg;
unsigned long dumpbuffer = 1;

//Timing stuff
int send_period = 1000;
unsigned long Tinit = 0;
unsigned long ser_update_per = 100;
unsigned long last_ser_update = 0;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);

  radio.begin();

  // Set the PA Level low to prevent power supply related issues since this is a
  // getting_started sketch, and the likelihood of close proximity of the devices. RF24_PA_MAX is default.
  radio.setPALevel(RF24_PA_MAX);
  radio.setDataRate(RF24_250KBPS);
  // Open a writing and reading pipe on each radio, with opposite addresses
  if(ROLE == receiver ){
    Serial.println(“*** SETTING TO PRIMARY RECEIVE ROLE”);
    prim_role = 0;
    temp_role = 0;
    radio.openWritingPipe(pipes[0]);
    radio.openReadingPipe(1,pipes[1]);
    radio.startListening();
  }
  else if(ROLE == sender ){
    Serial.println(“*** SETTING TO PRIMARY TRANSMIT ROLE”);
    prim_role = 1;
    temp_role = 1;
    radio.openWritingPipe(pipes[1]);
    radio.openReadingPipe(1,pipes[0]);
    radio.stopListening();
  }

  Tinit = millis();
  last_ser_update = millis();
  Serial.println(“Finished with setup”);
}

void switchTempRole(){

  if (temp_role == temp_rec ){
    Serial.println(“*** CHANGING TO TRANSMIT ROLE”);
    radio.openWritingPipe(pipes[1]);
    radio.openReadingPipe(1,pipes[0]);
    radio.stopListening();
    radio.flush_tx();
    temp_role = temp_send; // Become the primary transmitter (ping out)
  }
  else if (temp_role == temp_send ){
    radio.openWritingPipe(pipes[0]);
    radio.openReadingPipe(1,pipes[1]);
    flushReadBuffer();
    radio.startListening();
    Serial.println(“*** CHANGING TO RECEIVE ROLE”);
    temp_role = temp_rec; // Become the primary receiver (pong back)
    msg_recvd = 0; //Say we haven’t receieved anything yet in this cycle.
  }
}

void checkForTempRoleSwitch(){
  if((millis()-Tinit)>send_period){
    switchTempRole();
    Tinit = millis();
  }
}

bool checkSerialUpdate(){
  if((millis()-last_ser_update)>send_period){
    last_ser_update = millis();
    return(1);
  }
  return(0);
}

void flushReadBuffer(){
  while(radio.available()){
    Serial.println(“Data flushed from read buffer.”);
    radio.read(&dumpbuffer, sizeof(unsigned long));
  }
}

void loop() {
// put your main code here, to run repeatedly:

  if(prim_role==prim_rec){//If this is the primary receiving radio.

    if(temp_role == temp_rec){
      if(radio.available()&&!msg_recvd){//If we get a message when we haven’t before
        radio.read(&msg, sizeof(unsigned long));
        msg_recvd = 1;
        Serial.print(“Received “);
        Serial.println(msg);
        ACKmsg = msg + 1;
      }
    }

    if(temp_role == temp_send){
      if(msg_recvd){
        radio.write(&ACKmsg, sizeof(unsigned long) );
        if(checkSerialUpdate()){
          Serial.print(“Sent ACK: “);
          Serial.println(ACKmsg);
        }
      }
      else{
        if(checkSerialUpdate()){
          Serial.println(“No msg received; no ack sent.”);
        }
      }
    }

    checkForTempRoleSwitch();
  }

  if(prim_role==prim_send){//If this is the primary “sending” radio.

    if(temp_role == temp_send){//If the transmitter is currently sending stuff out.
      radio.write(&msg, sizeof(unsigned long) );
      if(checkSerialUpdate()){
        Serial.print(“Sent “);
        Serial.println(msg);
      }
    }

    if(temp_role == temp_rec){//If it’s waiting for the ack.
      if(radio.available() && !msg_recvd){
      radio.read(&msg, sizeof(unsigned long));
      msg_recvd = 1;
      Serial.print(“Received ACK: “);
      Serial.println(msg);
      msg++;
    }

  }

  checkForTempRoleSwitch();

  }

}
```

I’ll just go over a couple of what I consider key parts here.

There are two “permanent roles” in this sketch. I.e., the Arduino can be set to be a sender or receiver by setting the line bool ROLE = receiver;. This doesn’t change during execution. However, there are also two “temporary roles” that *do* change depending on whether the Arduino is sending or reading data. The switch from one to the other is smoothly handled by the switchTempRole() function, which changes the pipes appropriately.

Anyway, the main execution is pretty straightforward. Each Arduino (regardless of its permanent role) alternates between temporarily sending (Tx) and receiving (Rx), at a fixed rate. Now, the periods of Tx and Rx for the two Arduinos are almost certainly *not *synchronized, but that actually doesn’t matter. The picture below should explain it.

![TxRx_timing1.png](/assets/images/txrx_timing1.png?w=1200)

Where the progression of time is down the page, and Tx means the relevant Arduino is transmitting, and likewise for Rx. You’ll notice that the receiver’s timings are staggered with respect to the transmitter’s, which is almost always what happens. However, as long as it is listening for *some* time while the transmitter is sending (which is always the case), it turns out fine.

Now, when I first did this (i.e., a version of the code previous to the one I posted), it was *mostly* working but something was off. Everything was getting received, the numbers in both serial monitors were increasing, but there were fairly often doubles. What I mean by this is some progression, something like (in the serial monitor for the receiver, for example):

> *** CHANGING TO RECEIVE ROLE
> Received 231
> *** CHANGING TO TRANSMIT ROLE
> Sent ACK: 232
> *** CHANGING TO RECEIVE ROLE
> Received 231
> *** CHANGING TO TRANSMIT ROLE
> Sent ACK: 232
> *** CHANGING TO RECEIVE ROLE
> Received 233
> *** CHANGING TO TRANSMIT ROLE
> Sent ACK: 234

So you can see from this that it’s definitely receiving stuff, sending stuff, and incrementing… but something is weird because it received 231 twice before getting 233.

The answer to this is that the chip itself has a “read buffer” where incoming data is stored before you read it. So, what was happening is, in this sketch, the sender repeatedly sends its message *repeatedly* during its Tx phase. So in this case, the transmitter was sending 231 again and again, which filled up the read buffer of the receiver. When the receiver first read the data during its Rx phase, it stored that value and then stopped reading. However, the other 231’s were still in its read buffer, so when the next cycle rolled around (where the transmitter was now sending 233), there were still several 231’s left in the receiver’s read buffer.

The fix was simple, adding the flushReadBuffer() function as in the code above. Interestingly, I put a little serial message, “Data flushed from read buffer.”, in the while loop of that function (where it does it for each <span class="skimlinks-unlinked">radio.read</span>() used to empty the buffer). Now if you look at the serial output:

> *** CHANGING TO RECEIVE ROLE
> Received 231
> *** CHANGING TO TRANSMIT ROLE
> Sent ACK: 232
> Data flushed from read buffer.
> Data flushed from read buffer.
> Data flushed from read buffer.

Note that there are *three* of that message, and there are for all the following communications too. I believe this is because the chip can only store three 32-byte data packets.

Now, there’s one last thing I want to look at. Because of the crude (but simple!) timing I used here, I’d wager that it can quickly get really crappy. If you noticed, the period I was using for the Tx/Rx phases were 1 second each, which is plenty of time to get data, even if they’re pretty staggered between the two Arduinos. But, I’m guessing if I do something a lot lower, just due to all the stuff I’m making the sketch do, it will quickly start missing data and not ACKing back as often.

Here, I’ve set send_period = 10 (10 ms!), and here is the serial output:

Transmitter:

> *** CHANGING TO TRANSMIT ROLE
> Sent 5635
> Sent 5635
> *** CHANGING TO RECEIVE ROLE
> *** CHANGING TO TRANSMIT ROLE
> Sent 5635
> Sent 5635
> *** CHANGING TO RECEIVE ROLE
> *** CHANGING TO TRANSMIT ROLE
> Sent 5635
> Sent 5635
> *** CHANGING TO RECEIVE ROLE
> Received ACK: 5636
> *** CHANGING TO TRANSMIT ROLE
> Sent 5637
> Sent 5637
> *** CHANGING TO RECEIVE ROLE
> Received ACK: 5638
> *** CHANGING TO TRANSMIT ROLE
> Sent 5639

Receiver:

> *** CHANGING TO RECEIVE ROLE
> Received 5637
> *** CHANGING TO TRANSMIT ROLE
> Sent ACK: 5638
> Data flushed from read buffer.
> Data flushed from read buffer.
> Data flushed from read buffer.
> *** CHANGING TO RECEIVE ROLE
> Received 5637
> *** CHANGING TO TRANSMIT ROLE
> Sent ACK: 5638
> Data flushed from read buffer.
> Data flushed from read buffer.
> Data flushed from read buffer.
> *** CHANGING TO RECEIVE ROLE
> Received 5637
> *** CHANGING TO TRANSMIT ROLE
> Sent ACK: 5638
> Data flushed from read buffer.
> Data flushed from read buffer.
> Data flushed from read buffer.
> *** CHANGING TO RECEIVE ROLE
> Received 5637
> *** CHANGING TO TRANSMIT ROLE
> Sent ACK: 5638
> Data flushed from read buffer.
> Data flushed from read buffer.
> Data flushed from read buffer.

You can see that stuff is clearly getting missed, understandably.
