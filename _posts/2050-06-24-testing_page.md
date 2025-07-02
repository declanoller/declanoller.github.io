---
date: 2050-06-24 00:00:00-05:00
layout: post
permalink: testing_page
thumbnail: /assets/images/thumbnails/THUMBNAIL_NAME_HERE
title: testing_page
---


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

Here it is with the direct post location (i.e., `_posts/2021-01-01-making-diy-lenses.md`), doesn't work:

[lenses post, direct](_posts/2021-01-01-making-diy-lenses.md)

Here's a link using the curly braces method and the heading with a `#` (works):

[DIY lenses post, permalink, the light ray box heading]({{ site.baseurl }}/2021-01-01-making-diy-lenses#the-light-ray-box)

Here's an obsidian-style markdown link (doesn't work):

[2021-01-01-making-diy-lenses](_posts/2021-01-01-making-diy-lenses.md)

# Embedded code on page


Here's a little javascript sim using "raw" and "endraw" jekyll tags (works):


{% raw %}
<div style="margin:0; overflow:hidden;">
  <canvas id="canvas"></canvas>
  <script>
    const canvas = document.getElementById("canvas");
    const ctx = canvas.getContext("2d");
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    const balls = Array.from({ length: 30 }, () => ({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      vx: (Math.random() - 0.5) * 6,
      vy: (Math.random() - 0.5) * 6,
      r: 10 + Math.random() * 10,
      color: `hsl(${Math.random() * 360}, 100%, 60%)`
    }));

    function draw() {
      ctx.fillStyle = "rgba(0, 0, 0, 0.2)";
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      for (let b of balls) {
        b.vx += (Math.random() - 0.5) * 0.5;
        b.vy += (Math.random() - 0.5) * 0.5;
        b.x += b.vx;
        b.y += b.vy;

        if (b.x < b.r || b.x > canvas.width - b.r) b.vx *= -1;
        if (b.y < b.r || b.y > canvas.height - b.r) b.vy *= -1;

        ctx.beginPath();
        ctx.arc(b.x, b.y, b.r, 0, Math.PI * 2);
        ctx.fillStyle = b.color;
        ctx.fill();
      }

      requestAnimationFrame(draw);
    }

    draw();
  </script>
</div>
{% endraw %}











