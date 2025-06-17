

# Equations

Here's an inline equation with dollar signs (works):

The score function $\nabla_\theta \log p_\theta(x)$ is pretty cool!

Here's a block equation with dollar signs (works):

$$
\begin{bmatrix}
a & b \\
c & d \\
\end{bmatrix}
$$

Here's an inline equation with mathjax:

The score function \\(\nabla_\theta \log p_\theta(x)\\) is pretty cool!

Here's a block equation with mathjax (kind of messed up?):
\\[
\begin{bmatrix}
a & b \\
c & d \\
\end{bmatrix}
\\]

# Image alt text and captions


Here's an image that might have a caption (doesn't work):

![The horror!](/assets/images/euler_smeared_horror3.jpg)

Here's an image that might have alt text (works):

![](/assets/images/euler_smeared_horror3.jpg "Help meeee")


# Inline images location


This image has a `/` in front of the `assets/...` location (works):

![bote0003](/assets/images/bote0003.jpeg)

This image does NOT have the leading slash (doesn't work):

![bote0003](assets/images/bote0003.jpeg)




# Do obsidian-style callouts work?

Here's a callout (doesn't work):


> [!NOTE] Please work?
> Hopefully a note is here!


# Links to pages and headings


Here's a link using `{{site(dot)baseurl}}` (with spaces around it, dot replaced with period) and the permalink (works):

[lenses post, permalink]({{ site.baseurl }}/2021-01-01-making-diy-lenses)

Here it is with the direct post location (i.e., `_posts/_posts/2021-01-01-making-diy-lenses.md`):

[lenses post, direct](_posts/2021-01-01-making-diy-lenses.md)

Here's a link using the curly braces method and the heading with a `#`:

[DIY lenses post, permalink, the light ray box heading]({{ site.baseurl }}/2021-01-01-making-diy-lenses#the-light-ray-box)


Here's an obsidian-style markdown link (doesn't work):

[2021-01-01-making-diy-lenses](_posts/2021-01-01-making-diy-lenses.md)

# Embedded code on page


Here's a little javascript sim hopefully:













