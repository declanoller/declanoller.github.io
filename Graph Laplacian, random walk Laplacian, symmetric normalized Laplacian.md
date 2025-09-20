


questions:

- [ ] how can I "construct" a transition matrix $P$ with eigenvalues and vectors with certain properties, so I can look at what $P$ would look like with those?
- [ ] 







---


---

# graph, transition matrix, and adjacency matrix basics

first some basics about the transition matrix $P$, adjacency matrix $A$, and graphs in general:

- an undirected graph means $A$ is symmetric; a directed graph means $A$ is asymmetric.
- if  is symmetric, it does NOT mean the transitions probs ($P$) are symmetric
	- e.g., $P(A \rightarrow B) \neq P(B \rightarrow A)$
	- but, it DOES imply that there's a stationary distribution $\pi$, and that detailed balance holds for it: $\pi_i P_{ij} = \pi_j P_{ji}$
	- What does it mean if detailed balance didn't hold?
		- there's still a stationary distribution, but it's not "time reversible", i.e., there's a cyclic flow
		- for example, if you had the MDP A -> B -> C -> A, the dist $\pi = (1/3, 1/3, 1/3)$ would be stationary, but you never have any flow from B to A
		- I think it could also mean you have a one-way transition, like to a sink or from a source state
		- 
	- so: "reversible" means detailed balance holds and vice versa
- this relationship is tight:
	- if $P$ is reversible, then the related $A$ is symmetric
	- if $P$ is NOT reversible, then the related $A$ is asymmetric
- $A$ determines $D$, so therefore also specifies $L$
	- but we also have $P = D^{-1} A$, so $A$ also uniquely specifies $P$ 
- BUT! $P$ does NOT *uniquely* determine $A$:
	- i.e., scaling $D \mapsto cD, A \mapsto cA$ leaves $P$ unchanged
	- basically, $P$ determines the ratio of edge weights (transition probabilities), but not their scale
- so in general, from a high level, we should have this in our head:
	- for a "well behaved", "typical" markov process that's time reversible, $P$ is NOT symmetric (it's fine to have the probability transitions between two states not be the same)
	- but provided it's well behaved like this, $A$ WILL be symmetric
- 



# different laplacian versions



Normal GL: $L = D - A$

random walk GL: 
$$
\begin{aligned}
L_\text{rw} &= I - D^{-1} A \\
&= D^{-1} L \\
& = I - P
\end{aligned}
$$
symmetric normalized GL:
$$
\begin{aligned}
L_\text{sym} &= I - D^{-1/2} A D^{-1/2} \\
&= D^{-1/2} L D^{-1/2} \\
\end{aligned}
$$
and (useful later):
$$
\begin{aligned}
L_\text{sym} &= D^{-1/2} L D^{-1/2} \\
&= D^{-1/2} (D L_\text{rw}) D^{-1/2} \\
&= D^{1/2} L_\text{rw} D^{-1/2} \\
\end{aligned}
$$



okay, this is useful:

- the graph is uniquely specified by $A$, or by $P$ (up to a constant)
- and you can see from the laplacian definitions that they're all just different combos of $D, A$. So you can view them as different "views" of the graph, or different operators on the same graph
- some symmetry relations:
	- $L_\text{sym}$ is symmetric IFF $A$ is symmetric 
		- (you can write out the def in terms of $A$ and $D$, and then calculate $L_\text{sym}$ and show that they're the same)
	- $L$ is symmetric IFF $A$ is 
		- ($D - A$, they're both symmetric, so $L$ is)
	- $L_\text{rw}$ is NOT necessarily symmetric, even if $A$ is symmetric
		- recall, it's $= I - P$, and $P$ is not necessarily symmetric even if $A$ is
- for reversible $P$:
	- $L_\text{rw}$ has the same e.vecs $v_k$ as $P$, but the e.vals are shifted, $\lambda_k \mapsto 1 - \lambda_k$
	- note that the stationary dist $\pi$ obv has $\lambda_1 = 1$ for $P \pi = \lambda_1 \pi = \pi$
		- therefore, $\pi$ as an e.vec of $L_\text{rw}$ has e.val $1 - 1 = 0$.
- I think this stuff is answering questions I had a long time ago when I was looking a the eigenvectors of $P$ for some toy problems!
- For reversible $P$:
	- all e.vals are real and in $[-1, 1]$
	- the stationary dist has $\lambda = 1$, because $P \pi = \pi$
	- if reversible, then no other eigenvector has an eigenvalue of magnitude $1$
	- what do they represent? "modes of relaxation" -- for any dist, it's composed of the stationary dist plus deviations from it (composed of those other eigenvectors). As the dist transitions, it approaches the stationary dist. So, the deviations "relax" and go to zero, hence, they have e.vals with magnitude $< 1$.
- A non-reversible $P$ (for ex, periodic), it can have e.vals that are complex with magnitude $1$ (rotations, basically)
- 



![Drawing 2025-09-17 18.47.24.excalidraw](assets/Excalidraw/Drawing%202025-09-17%2018.47.24.excalidraw.png)




## relationship between eigenvectors and values of each

There's a kind of subtle point here. I wanted there to be a really clean distinction between the e.vecs and e.vals of the three versions of the Laplacian, where one could be translated into the other easily, but it's a bit more complicated.

Basically, the answer is that everything gets a lot neater if instead of looking at the ordinary EP, $L v = \lambda v$, we look at the *generalized* EP (GEP):

$$
L v = \lambda D v
$$

now, if we assume that $v_\text{sym} = D^{1/2} v$ and plug it into the EP for the symmetric one:

$$
\begin{aligned}
L_\text{sym} v_\text{sym} &= D^{-1/2} L D^{-1/2} v_\text{sym} \\

&= D^{-1/2} L D^{-1/2} D^{1/2} v \\
&= D^{-1/2} L v \\
&= D^{-1/2} \lambda D v \\
&= \lambda D^{1/2}  v \\
&= \lambda v_\text{sym}
\end{aligned}
$$

So that tells us that they have the *same eigenvalue*, provided the eigenvector for the symmetric one is related to the generalized eigenvector of the ordinary Laplacian.

How about for the RW? Assume that for this one: $v_\text{rw} = v$

$$
\begin{aligned}
L_\text{rw} v_\text{rw} &= D^{-1} L  v_\text{rw}\\
&= D^{-1} L v\\
&= D^{-1} \lambda D v\\
&= \lambda v\\
&= \lambda v_\text{rw}\\

\end{aligned}
$$

So here, the RW Laplacian actually has the same eigenvalue AND its eigenvector is equal to the generalized eigenvector of the ordinary Laplacian.








# Some misc resources


Significance of the random walk normalized graph Laplacian - Mathematics Stack Exchange
https://math.stackexchange.com/questions/4174140/significance-of-the-random-walk-normalized-graph-laplacian

good intuition: $P$ and $L_\text{rw}$ have the same e.vals (one minus etc) and e.vecs, so you really can just study $L_\text{rw}$ instead of $P$. Why would you?

- because the e.vals of $P$ are at most 1, the e.vals of $L$ are $> 0$, so it's PSD (kind of, it's not symmetric)
- while the stationary dist has $x P = x$, it has $L x = 0$, which is a nicer form

---

this guy again:

The graph Laplacian - Matthew N. Bernstein
https://mbernste.github.io/posts/laplacian_matrix/

much simpler than what I'm going for tho

---

convolutional neural network - Difference between Symmetrically normalized Laplacian matrix versus graph laplacian matrix - Cross Validated
https://stats.stackexchange.com/questions/581898/difference-between-symmetrically-normalized-laplacian-matrix-versus-graph-laplac

Useful: you can see for yourself that the symmetric normalized GL is symmetric by just showing that $L = L^\intercal$

Also, you can see from the form of its definition, $L_\text{sym} = D^{-1/2} L D^{-1/2}$, that it's basically normalizing the columns and rows of $L$ by $D$, so no large degree nodes dominate.


---

The Unreasonable Effectiveness of Spectral Graph Theory: A Confluence of Algorithms, Geometry & ... - YouTube
https://www.youtube.com/watch?v=8XJes6XFjxM

this looks really good.

---

expanders-2016.pdf
https://lucatrevisan.github.io/books/expanders-2016.pdf


---

Geometric intuition of graph Laplacian matrices - Mathematics Stack Exchange
https://math.stackexchange.com/questions/1717471/geometric-intuition-of-graph-laplacian-matrices

very long, I think he's mostly looking at simple graphs? but maybe useful at some point


---

[1211.0053] The Emerging Field of Signal Processing on Graphs: Extending High-Dimensional Data Analysis to Networks and Other Irregular Domains
https://arxiv.org/abs/1211.0053

linked from another, actually looks like a lot of what I've done

---






