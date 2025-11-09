




- example
- main thing: does that sound right?
- the idea:
	- scope the biggest and smallest possible (1 to city size, for example)
	- this is actually only $\log_{10} N$ options --> 100 million --> $10^8$ --> 8 options
	- cross out the ones that don't sound plausible
	- use a tiny bit of reasoning, then take the midpoint
- we kind of already do this when we estimate the factors
- kind of a random walk idea?
	- let's say for each factor going into things, you look at the deviation (in OoM) from the true value, so 10x bigger than true is +1, 10x smaller is -1
	- to simplify let's assume you're never more than $\pm 1$ off
	- if there are $M$ factors, then you could be $\pm M$ off, where 0 means correct answer
	- variance grows with $M$, right?










