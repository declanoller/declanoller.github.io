---
date: 2025-06-23 00:00:00-05:00
layout: post
permalink: GCRL_motivations
thumbnail: /assets/images/thumbnails/robot_ruler_led_renoir_thumbnail.png
title: GCRL - Motivations
---

[Last time]({{ site.basurl}}/2025-05-28-Goal_conditioned_RL_background_and_overview), we chatted about the high level ideas of GCRL. I alluded to some motivations for it, like the flexibility it gave in the realistic concrete example, and whatever "goal relabeling" is, but didn't go into much depth.

In my opinion, the motivations fall into two big categories: generality, and efficiency. Both of these are big factors in the success of LLMs, and they haven't been fully leveraged in RL yet. Maybe GCRL could do that for RL!


# Name games

As I mentioned last time, I don't wanna focus on somewhat arbitrary names for different techniques that are all pretty similar. But unfortunately, we have to a bit today :(

I'll say MTRL (multi-task RL) to mean having a set of parameters $z$ that determine what reward function is being used, $r(s, a, z)$; so super general. I'll say GCRL to mean the subset of MTRL where the $z$ variable corresponds to a state, and it usually comes with some other choices baked in as well.

The motivations below do apply to both MTRL and GCRL, but for each, GCRL can benefit even moreso from them.

# Generality

The usual approach in RL is:

- you have a specific problem you want to solve
- you think about the reward function that would lead an agent to learn to solve this specific problem
- you mainline caffeine and spend a ton of time, effort, and money training the agent to maximize this specific reward

and if you're lucky, you get an agent that can solve that problem. But even if that agent is *really good*, it's typically only optimized for *that problem*! And that kind of sucks. If you're gonna collect all that experience anyway, why not get a more flexible and capable agent out of it?

I've already mentioned flexibility as a motivation, but there are some underappreciated aspects of it, discussed in the first section below. Then, in the next section, I talk about why dealing with specific rewards at all is a pain and could be avoided. 

## MTRL: Don't solve just one problem, solve many!

Let's say we have a stock trading robot. When investing, you (at least implicitly) choose some point on the risk-payoff tradeoff curve. In traditional single-problem RL, you'd choose that tradeoff point up front and train the agent with a reward function corresponding to it. But if you decided after training that it's too risky and you'd prefer to make a little less money on average but not have wild swings in your accounts, you're out of luck -- you have to retrain it. I'll call this the "I changed my mind about what I want" scenario.

One option would be to choose the *range* of the possible problems you might want to solve and design reward functions for them parameterized by the $z$ variable, and then solve all of them in the typical MTRL approach. In the trading agent example, the $z$ variable could represent the desired risk-payoff point. Then, you can change how risky it'll behave *after* training, when you've had a chance to deploy it. 

You can view $z$ as a "knob" you can turn to alter the behavior of the agent in this dimension. This is useful if you don't know exactly which problem you'll have to solve during deployment (for example, maybe your investment firm has different clients with different risk tolerances). I'll call this the "I don't know the exact problem" scenario.

![](assets/images/chili_reward_functions.png)

The "I changed my mind about what I want" and "I don't know the exact problem" scenarios are definitely big motivations for MTRL, but I'd argue that it's useful even if you **won't** change your mind and you **do** know the exact problem:

- **The "environment train-deployment gap":** Often, despite our best efforts, true deployment is still a little different than training. So even if you trained it for a specific risk tolerance and you don't want to use it for other ones, you might discover that the actual environment ends up being a little more inherently risky. The MTRL agent lets you compensate for that by turning the "risk" knob down a bit to get the level you actually want.
- **The "reward-behavior gap":** Even if you have in mind some specific behavior you want your agent to have, in "real" problems the link between reward and behavior isn't so direct. In toy problems, the rewards are often simple enough that you can mathematically show (or just *see*) that an optimal policy for that reward would do what you want. But, real problems often involve several reward functions with several components that have competing "interests". You might know what each component incentivizes on its own and have some ideal behavior in mind, but getting that behavior will require finding a specific weighted combination of all those components in just the right ratio. With MTRL, you can train across all of these combinations, and then find the combination that gives you the behavior you want.
	- A good analogy is me making chili:  I never look up a recipe for chili, I just know what all the ingredients are, what flavor each contributes, and (roughly) what I'd like the final product to taste like. I don't know what's the exact amount I should use of each ingredient, and if I tried making the recipe by flying blind, it'd probably taste terrible and I would've wasted all that time making it.


### Shortcomings of pure MTRL

The previous section gives some arguments for why you might as well try to solve your problem with a range of reward functions (MTRL) rather than a single one. However, it's still a bit unsatisfying for a few reasons:

#### "I didn't think of that"

You still have to think of all the problems you might want to support and design rewards for them, and if you didn't think of them, you're out of luck.

#### Reward design just... sucks

Designing rewards can be a real pain. Aside from the previous point, reward hacking and unpredictable interactions between reward components are real problems in practice, and they get worse the more components you have. It'd be nice if we could somehow avoid having to design rewards.

Here's a screenshot of some of the rewards they had to carefully design in the [Meta-world paper](https://arxiv.org/abs/1910.10897) to get the robot to do what they want:

![](assets/images/Pasted%20image%2020250611202047.png)

This goes on for quite a while, one per task. And to be clear, those functions you see are themselves defined in terms of other nested functions several layers deep:

![](assets/images/Pasted%20image%2020250611202250.png)

This, too, continues for a while. No one wants to see how the MTRL sausage gets made.

#### We don't actually care about rewards! Or, the "boss metric" 

This is a pretty underappreciated point about RL as a practice; it definitely took a while to sink in for me!

Bluntly: *The agent wants reward. We want behavior.* It can be easy to lose sight of that because we spend so much time making our algorithms get better at accumulating rewards, but at the end of the day, we actually want a certain behavior from our agents and the rewards are just a tool for achieving that. Obviously, the field of RL is built around the fact that if you design your rewards well, then they're a *really good* tool for getting that behavior, but they're still a proxy for what we actually want.

I like to think of this as the "boss metric" because it's what your boss actually cares about: if your algorithm is crushing it at getting all the reward but the behavior sucks, your boss won't be happy. And conversely, if you do something where the rewards are weird (or you're not even using them!) but you're producing an agent that does exactly what the boss wants, your Christmas bonus tendies package will be very plump.

The unifying theme is that if we still might forget to make some rewards, designing rewards is hard, and we don't even actually *want* rewards, then... why not sidestep them? Why not try to more directly get the behavior we want?

## GCRL: if you can go anywhere, you've solved many problems

That's what GCRL (in the proper definition) does: the $z$ vector is a state itself, of the same form as $s$ (that's why it's often written as $g$ or $s_g$ rather than $z$). The reward is almost always something that reflects a (negative) *distance* between $s$ and $g$, often the sparse "indicator" function $r(s, g) = \mathbb 1[s = g]$ or a dense version like $r(s, g) = -\Vert s - g \Vert^2$.

With either of these reward functions, the optimal policy for a given goal is simply getting to that goal as quickly as possible. Since the MDP is essentially a graph, this becomes a shortest-path graph traversal problem (obviously a much studied problem in computer science). 

If you can do this, it dodges many of the problems I highlighted in the previous section! 

- If your GCRL policy can truly go to any state quickly, it's very general, and you don't have to worry about not having thought of some reward.
- The reward functions above are generic in form, so you don't have to do any problem-specific reward design.
- We can directly plug in the states we want the agent to be at without having to worry about our rewards being the best way to achieve that.

But as you might expect... there are never any free lunches, and this is a devil's bargain.

You might ask what differentiates GCRL from typical RL, then? I.e., why are we even using reward functions in RL rather than just using GCRL with a distance reward function? I'd say there are at least two big reasons.

### It's just a different problem

The first reason is that RL is solving the problem of maximizing the average cumulative discounted reward, which is a different problem than just getting to another state as quickly as possible.

As an example someone pointed out to me, sometimes we really care not just about the agent *getting* to some goal state, but also the *path* that the agent took there. If you want your yardwork robot to go to the state where there's nothing on the lawn except grass, there are many "paths" (sequences of states) it can take to get there, but it's a very important whether it annihilated your dog in the process or not. In typical RL, we'd handle this by making the pet-annihilating states have very negative rewards, and therefore any path going through these states would be undesirable for a good policy. In the version where it just cares about getting to the goal very quickly, going through fluffy might be the fastest way to get there :(

### Goals have problems, too

Another big reason is that in some problems, even specifying the goal state can be tricky, and the distance reward might be wonky. 

Specifying the goal state can be difficult because you have to specify a whole state to plug in, when you only might care about parts of it. For example, if your robot's state is composed of 1000 features that are sensor readings, and you really just want it to achieve specific values for 7 of them, you still have to plug in *some* values for the other 993. You probably can't plug in zeros or the same values as the current state and expect it to work, because those likely won't be valid values given the specific 7 feature values, so it'll be an impossible state. This is actually a kind of unsolved problem in the field, so this'll be the subject of a future post.

And, the distance reward might be wonky even if you can supply a true goal state, because the features might have different scales and meanings. As a really simple example, let's say one of your features is the RGB value of a light and another feature is a physical length in meters. Clearly, for a goal state $g$, the largest the dense reward $r(s, g) = -\Vert s - g \Vert^2$ can be is when $s = g$, so $r(s, g) = r(g, g) = 0$. 

![One of Renoir's lesser known works](assets/images/robot_ruler_led_renoir.png)

But how should you compare two states $s_1$ and $s_2$ with different RGB and length features? There's no "natural" equivalence between a difference in an RGB value and a difference in a length, and this would force *some* equivalence between them (depending on what unit you chose for the length, for example). This is a *very* important practical detail for most GCRL methods, so I'll talk about this in the near future. 

### Nevertheless

However, neither of these broad problems should be a game ender for GCRL.

For the first issue, many real world problems actually *are* ones where we only care about getting to a goal quickly and don't especially care about the intermediate states. And, for the problems where there are states we want to avoid, there are ways of working that in. However, this is a more fundamental distinction between problems, so in some cases we might have to bite the bullet and say that GCRL just isn't the right approach.

The second issue is less all-or-nothing, and I'll talk about some strategies to deal with it in a later post.


# Data efficiency with relabeling

The generality arguments above are the main motivations, but MTRL can also give some efficiency gains.

Last time, the way I presented the MTRL learning process is that at the beginning of each episode, a $z$ value would be selected, and the policy would run in the environment and collect data that we'd use to train the models for that $z$ value.

For example, if the robot had collected the transition $(s, a, r(s, a, z_1), s')$ while acting conditioned on $z_1$, we'd do a simple TD(0) Q-learning style update to the Q function with:
$$
Q(s, a, z_1) \leftarrow r(s, a, z_1) + \gamma \max_{a'} Q(s', a', z_1)
$$
But... $z$ isn't "real" in the same way the states and actions are. Why can't we use that transition to update $Q$ for $z_2$ as well? If policy did action $a$ in that state while conditioned on $z_2$ instead, it still would've ended up in $s'$; it just would've received a different reward. So we can use this same transition tuple to update like:
$$
Q(s, a, z_2) \leftarrow r(s, a, z_2) + \gamma \max_{a'} Q(s', a', z_2)
$$
This is generally called "relabeling", because the transition tuple would be "labeled" with the $z_i$ that it was collected under, and we're effectively just relabeling that. Note that this relies on being able to calculate $r(s, a, z)$ for different $z$ values, and this may also run into standard off-policy issues depending on which algorithm you're using. 

Despite that, the efficiency gains are potentially huge. The original and most famous version of this comes from the straightforwardly named paper ["Hindsight Experience Replay"](https://arxiv.org/abs/1707.01495). 

## Relabeling with GCRL and sparse rewards

Although you can relabel for any $z_i$ and any transition tuples you want, where it really shines is when the rewards are very sparse.

For example, imagine a $1000 \times 1000$ 2D gridworld in which a single cell is the goal which the agent receives $r = 1$ for reaching, and otherwise receives nothing. Every episode we randomly select one of the cells to be the goal and run the policy conditioned on that goal. Since the goal is one of those million cells, the untrained policy is really unlikely to stumble upon it via random walk. So almost every episode it'll receive zero reward and the Q function won't get updated with any useful information for a long time.

But, if we did the strategy above, we could update the Q function with the $z_i$ goal corresponding to the cell it *did* happen to reach, regardless of which was used during the actual episode. This way, the Q function for at least *some* $z$ value would get meaningfully updated each episode, speeding up learning immensely.

Intuitively, this can be explained by saying that learning is a lot easier if, even when you do something wrong, you're told "the thing you did *would've* been good if you had wanted to do this other thing."

Note that I used GCRL as the example here. You *can* do relabeling with regular old MTRL as described above, just changing $z_i$ and $r(s, a, z_i)$ for the update, but there are a few reasons why it's more commonly used with GCRL:

- As I mentioned, relabeling with MTRL does rely on being able to calculate $r(s, a, z)$ for any $z$. That's often possible, if you designed the reward functions yourself, but in the general RL formulation, the rewards are just given to you from the environment.
	- In contrast, in GCRL we're almost always using a reward function we've chosen that's some generic distance between the current state and goal, so relabeling is possible.
- Another reason is that (assuming you can relabel with MTRL), it's not necessarily clear when you *should* relabel. From the example above, relabeling is potentially really helpful when rewards are sparse and we relabel to get positive examples. But with MTRL, for a given $(s, a)$, it's not immediately obvious what you should relabel to without calculating $r(s, a, z_i)$ for all $z_i$ each time. Maybe none of the $z_i$ give a positive reward. One answer could be "always relabel" to just train with more varied data, but that can have some subtle downsides.
	- In contrast, in GCRL, there's always one very clear thing to relabel: the actually-achieved goal. It *will* have a positive reward.


Also note that you can relabel way more than for just the last state the agent happens to reach in a trajectory! I.e., if the trajectory is the sequence of transitions $[(s_0, a_0, r(s_0, a_0, g)), (s_1, a_1, r(s_1, a_1, g)), \dots, (s_n, a_n, r(s_n, a_n, g))]$, then what I proposed above was relabeling $g$ to $s_n$, the final state it reaches. But we can kind of always relabel up to each state in the trajectory that it reaches!

I.e., we can do the following relabelings with that single trajectory:
$$\begin{aligned}
\bigg[ &(s_0, a_0, r(s_0, a_0, s_1) ), (s_1, a_1, r(s_1, a_1, s_1)) \bigg] \\
\bigg[ &(s_0, a_0, r(s_0, a_0, s_2) ), (s_1, a_1, r(s_1, a_1, s_2)), (s_2, a_2, r(s_2, a_2, s_2)) \bigg] \\
\ & \dots \\
\bigg[ &(s_0, a_0, r(s_0, a_0, s_n) ), (s_1, a_1, r(s_1, a_1, s_n) ), \ \dots, \ (s_n, a_n, r(s_n, a_n, s_n)) \bigg] \\
\end{aligned}
$$
Which clearly produces a lot of useful training data!

## Similar vibe as learning the transition function, but not quite

On the surface, some of GCRL has the same flavor as learning the transition function for model based RL; in contrast to most model-free RL algorithms, both GCRL and MBRL can (ideally) reuse data produced from some other process to learn models that can be used for general tasks.

However, even in their idealized forms (i.e., where we have full data coverage and models with limitless capacity), this ostensible similarity is pretty shallow: if you perfectly learn a transition model, that gives you a tool to learn the RL models for any task, *but you still have to learn them*. The task should be a lot easier now for all the reasons people want to do MBRL, but it's still a big ol' dynamic programming problem. In contrast, if you manage to solve the GCRL problem, now you already have an agent that can go to any goal state effectively.

Obviously, I'm just spitballing in very broad strokes here, and there are a million differences between MBRL and GCRL.


# The "human view" of GCRL

Beep boop, saying "human view" makes me sound pretty robotic. This part is more of a "vibes" based argument for GCRL, but those can be useful too. Basically: it feels closer to how humans actually operate in the world. 

(It gets a bit muddled because the concept of an "action" is very precise in standard RL, happening discretely, at a fixed frequency, and at one specific time scale; meanwhile, for humans and the real world, they're more continuous and there's no single thing you can say is the "action" in the same way. I.e., it sure seems like in reality, actions are far more hierarchical, like "options" in RL.)

If I try and probe my internal process and how it *feels* when I do things in the world, most of the things that seem like they could be undebatably called an "action" are happening at a very low, subconscious level. Rather, it mostly feels like I just have desires, i.e., a way I want the world to be (in some local sense), i.e., a goal state. 

If a goal is close enough to my current state ("I'd like to be drinking from the coffee cup in my hand"), the low level actions lead directly to it (raising the cup to my mouth). But when the goal is further away ("I'd like to make a 3D shrek shaped cake and bring it to my friend's birthday party"), it doesn't feel like I'm thinking about "actions" that need to be done so much as other states ("subgoals") I'll need to visit on the way to the true goal.

This is clearly semantics though, and someone could easily phrase it the opposite way, which is clear from even the language we use: most people would say we need to *go* to the store to get ingredients for the cake (an action), while I'm saying that it's more like we need to *be* at the store (a state).

This view is still useful, because of the process or algorithms it could imply. In my view, we primarily think in terms of *what* we want and *where* we want to be. Sometimes, we consider subgoals in between, but only once we reach the lowest level do we actually do "actions". So for example, this could imply using a hierarchical scheme where models trained with RL propose goals and subgoals, until the low level where something more like MPC navigates between the lowest level states.

---

Anyway, that's all for today! Next time I'll go deeper into a few of the core problems that GCRL approaches are trying to deal with to make them feasible for the large scale application we'd like.