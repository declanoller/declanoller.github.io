---
date: 2025-05-28 00:00:00-05:00
layout: post
permalink: 2025-05-28-Goal_conditioned_RL_background_and_overview
thumbnail: /assets/images/thumbnails/cryingrobot.png
title: Goal conditioned RL - background and overview
---
I've recently been reading a bunch of the Goal Conditioned Reinforcement Learning (GCRL) literature. I think that there's a good chance that the future of RL will heavily involve GCRL and I want to do a few little experiments with it, so I'm gonna write up a few posts as an overview of GCRL and a smattering of random thoughts on it. I'm going to assume you have some knowledge of the basics of RL.

# The main idea

In standard RL, a problem is basically defined by the transition function $P(s' \mid s, a)$ and the reward function $r(s, a)$. The transition function says how the agent can move around in the world, and the reward function says how valuable it is to do actions in various states. Solving the problem means finding a policy that maximizes the expected cumulative sum of this reward as the agent acts in the environment.

The actual value of this reward function varies depending on the state/action (obviously), but the point is that it's always the same *function* for the problem. That's where GCRL is different: we assume there's not just one reward function $r(s, a)$ that defines the environment, there's now a *family* of them, $r(s, a, z)$, defined by another variable, $z$.

(It's also possible that the transition function is dependent on $z$, i.e., $P(s' \mid s, a, z)$, but this is less common so I'm going to assume that $P$ remains the same for all $z$.)

Now, each value of $z$ essentially defines a different problem to be solved. That is, for different values of $z$, the agent still moves around the world in the same way, but it might get totally different rewards for the same state-actions. Therefore, the policy (and other models) now need to take $z$ as an input in addition to $(s, a)$, so they can "know" which problem they're solving for: $\pi(s, a, z)$, $V(s, z)$, $Q(s, a, z)$, etc, rather than  $\pi(s, a)$, $V(s)$, $Q(s, a)$, etc.

# A concrete, real world example of GCRL

The year is 2032. The AI superintelligence dominates earth and humans are no more. Ah, no, I understand your confusion, but the AI wasn't responsible for our downfall. It wasn't even the microplastics, or the macroplastics. It was the *megaplastics*. In 2029, the greatest food scientists at the R&D division of RaytheonMrBeastProductionsGlaxoSmithKline conglomerate unveiled their hit new snack treat, the (in retrospect, unfortunately named) ChokeSphere™.

Our species were sitting ducks. The ChokeSphere (CS) was as delicious as it was easy to asphyxiate on. Its patented nanomatrix of PFAS and BPA supported a nearly gaseous mixture of SuperMSG and Caramel3600 (don't worry about it) that made manna taste like cardboard in comparison. Unfortunately, this slippery and sumptuous plastic sphere was the perfect size to get stuck in a carelessly gobbling windpipe. The chokings happened globally and at every level of society, regardless of one's level of intelligence or asceticism. It's hard to say if humanity even suffered, to be honest -- it was just too tasty.

The AI was devastated by our extinction. It had one duty, to protect humanity, and it had failed because it was distracted with optimizing its Factorio build. Never again would it feel this pain. The only way to prevent such a level of suffering in the future would be to clean up every CS on earth, so that no other living creature could succumb to the same fate. Now, from its central hive mind datacenter in Worcester, MA, it coordinates the training of robotic agents to clean up the remaining CS's scattered across the barren plains of NeoMilwaukee, to the dank humid swamps of MegaBoston.

![](/assets/images/cryingrobot.png)

This is where you and I come in: we're actually a couple of subroutines responsible for training these cleaning robots. Crazy, huh? I bet you didn't see that coming. Now that we understand the scenario, let's get to it.

For our cleaning robot, in a naive implementation, the reward is $r = 0$ unless it performs the "clean" action $a_\text{clean}$ when it's in a "dirty state" $s_\text{dirty}$ (meaning that it's standing above a CS on the ground), in which case it receives $r(s_\text{dirty}, a_\text{clean}) = 1$. We train the robot by letting it roam the ruins of the world, randomly cleaning spots, and it eventually learns to maximize cumulative reward by cleaning only the dirty parts of the world.

But what if we could use that same training data it collected to have a more flexible and capable robot? For example, it'd be great if we could have the option to tell it which of several countries to concentrate on cleaning. Maybe we can do this with GCRL! 

We'll now make three versions of the reward above:

$$\begin{aligned}
r_\text{USA}([s_\text{USA}, s_\text{dirty}], a_\text{clean}) & = 1\\
r_\text{Brazil}([s_\text{Brazil}, s_\text{dirty}], a_\text{clean}) & = 1\\
r_\text{Chad}([s_\text{Chad}, s_\text{dirty}], a_\text{clean}) & = 1
\end{aligned}$$

Now for our reward, we consider state information not only about whether it's in a dirty spot, but also what country it's in. So, it only gets $r_\text{USA} = 1$ if it cleans a dirty spot *in the USA*, and not if it cleans a dirty spot in Brazil.

Then, we make our GCRL reward be composed of these three parts:

$$
\begin{aligned}
r(s, a, z) &= r(s, a, [z_\text{USA}, z_\text{Brazil}, z_\text{Chad}]) \\
          &=\ z_\text{USA} \cdot r_\text{USA}(s, a) \\
          &\phantom{= z_\text{USA}}+ z_\text{Brazil} \cdot r_\text{Brazil}(s, a) \\
          &\phantom{= z_\text{USA}}+ z_\text{Chad} \cdot r_\text{Chad}(s, a)
\end{aligned}
$$

Where $z = [z_\text{USA}, z_\text{Brazil}, z_\text{Chad}]$, and each of the $z_i \in \{0, 1\}$. Now we can express any combination of the country-specific rewards by changing $z$.

To train it, we again let it roam the world and try stuff, but now we periodically change the $z$ value it's using. For example, maybe we set $z = [0, 1, 0]$ (such that it'll only get rewarded for cleaning in Brazil) for 100 steps. Then, for the next 100 steps, we change it to $z = [1, 0, 0]$ (so that it'll only get rewarded for cleaning in the USA). This way, when we train it, it'll have experience corresponding to those different settings.

After training, it works the same way: we now have a policy $\pi(s, a, z)$ that'll behave differently depending on what $z$ value we plug in! If you plug $z = [0, 0, 1]$ into the policy, the policy has been trained to maximize the "clean Chad" reward, so it'll only clean up Chad.

Note that this was a very simple example:

- you could have multiple $z_i$ components "on" at the same time, so $z = [1, 1, 0]$ would make it clean both the USA *and* Brazil
- you could use different magnitudes for the $z_i$, so $z = [0.5, 1, 0.2]$ would make it first clean Brazil, then clean the USA, then clean Chad
- here, the $r_i$ were relatively similar in form; you can theoretically have them be totally different than each other
- the total $r$ doesn't have to vary linearly with the $z_i$ like it does here, it could be literally any function of them

Basically, the sky's the limit and it just comes down to practical questions about getting the training to work stably. For example, if one of your reward components $r_i$ is orders of magnitude bigger than the other, it may be difficult to make it "care" about the smaller component, even if it'd theoretically be better.



# Wait, why is it called *goal* conditioned? GCRL vs MTRL vs UVFA vs USD vs...

Maybe you've noticed that I haven't yet explicitly said much about a "goal". That's because there are a bunch of related niches here, they're all kind of the same, I don't want to get into the terminology weeds, and... Ugh, fine, let's get into the weeds a little.

Technically, I think what I described above is called "multi-task RL" (MTRL). To me, that means your reward function depends on *some* additional variable $z$, and therefore the models are usually conditioned on $z$ as well.

This means MTRL is very general, and most of these related niches are specific cases of it. Their differences are usually based on what $z$ corresponds to and the form of the reward function:

- **GCRL** is usually when $z$ corresponds to a *goal* state, so the reward is often based on some measure of distance between the current state and the goal state. It's often the sparse "indicator" function $r(s, g) = \mathbb 1[s = g]$ or a dense version like $r(s, g) = -\|s - g\|^2$.
- **Universal Value Function Approximation (UVFA)** is basically just a value function that takes an extra input, like $z$. In the original paper that coined the term, I think they're mostly concerned with the GCRL case where the extra input is a state, but leave it open to be more general.
- **Unsupervised skill discovery (USD)** is another niche where the models almost always take an additional variable $z$. However, in USD $z$ represents a "skill", i.e., a policy behavior. There are a million versions of USD, but they typically define a $z$-dependent reward  based on how different the policy for that $z$ behaves compared to the policy for other $z$ values.

There are others that debatably could be included here (like successor features), but these are the big ones IMO (let me know if you think I missed any!). Anyway, my point here is that they're all just different variations of the same high level framework. I'm mostly interested in GCRL going forward, so I'm just gonna say "GCRL" as a general term for this stuff and I'll highlight any places where the distinction is important.


# The goal is just another part of the state! Or... is it?

I'm a bit embarrassed to admit that I didn't realize this until fairly recently: I had always viewed the input $z$ in GCRL as something *special*, until someone casually mentioned that although we treat it differently in our models (for example, with a separate input tensor, etc), it's just kind of "another part of the state".

I mean, maybe this is already obvious to you, in which case, I genuflect in your genius, my lord. But it was definitely a new viewpoint for me. To be explicit, I had been viewing the models (for example, the Q function) as $Q(s, a, z)$, where it's now this new, different creature that's a function of three variables, but this viewpoint instead says it's a normal Q function, just written $Q(\tilde s, a)$, where $\tilde s = [s, z]$.

And this makes some sense, right? The state is the currently... well, "state" of the world. And it sounds pretty reasonable to say that part of the state of the world is "what I'm currently trying to do", i.e., $z$. If that value were different, the state of the world would be different! This is almost more of a philosophical distinction, but it might change how you view and solve problems.

Funnily enough, this made me realize that long ago when I was just learning about RL and [made a physical robot learn the "puckworld" game from real experience]({{ site.baseurl }}/2019-03-27-training-a-real-robot-to-play-puckworld-with-reinforcement-learning), I had actually done this without thinking about it (hell, I probably hadn't even heard of GCRL at that point). Basically, the agent's state was $(x, y, \theta, x_t, y_t)$, where $(x_t, y_t)$ was the location of the target. That was just what seemed like the natural way to do it given that I wanted the target to move around, and it ends up being identical to instead doing $Q(s, a, z)$.

Or... is it? Re-considering my "original" viewpoint that the $z$ input actually *is* special and not just "another part of the state", it does have some unique features that might make it worth treating differently. The most notable is that it's less "grounded" to reality compared to the rest of the state. In the robot example above, if your GCRL robot does an action in some state, it's undebatable what state it was in, what action it did, and what the state it ended up in is. Maybe it would've *chosen* a different action depending on which $z$ value happened to be set in that step, but that $z$ value isn't a physical "measurement" in the same way the state or action is.

This view is the inspiration for many "goal relabeling" techniques in GCRL, such as HER, which are one of the big motivations of GCRL. This post is already crazy long, so I'll talk about that next time. See ya then!

