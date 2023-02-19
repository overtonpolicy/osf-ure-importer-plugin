
# Mathspan Example

## Math Block

To declare a variable:

$$var math = \frac{1}{\sqrt{x^2 + 1}}$$


# A new heading
$$\alpha\beta*2^{3i}$$

Some more things:
$$\begin{array}{cc} a & b \\ c & d \end{array}$$
Next paragraph.

# Another heading

$$\alpha = 16663;
\beta = 46*2^{3i}$$

# Heading
$$\alpha
\beta
*2^{3i}$$
Next paragraph

This should be on a separate line : $$\\alpha\\beta*2^{3i}$$ This line should be standalone on a new line.

This should be on a separate line : $$ \\alpha
      \\beta
    *2^{3i} $$ This line should be standalone on a new line.
.

Test single character:$$ k $$-Math block.



This is something inline: $\sum_{i=0}^n i^2 = \frac{(n^2+n)(2n+1)}{6}$

$$\sum_{i=0}^n i^2 = \frac{(n^2+n)(2n+1)}{6}$$

$$
    \begin{matrix}
    1 & x & x^2 \\
    1 & y & y^2 \\
    1 & z & z^2 \\
    \end{matrix}
$$

This block does start inline, but it's a block: $$ \begin{matrix}
    1 & x & x^2 \\
    1 & y & y^2 \\
    1 & z & z^2 \\
    \end{matrix} $$

This is also a block: $$ \left[
\begin{array}{cc|c}
  1&2&3\\
  4&5&6
\end{array}
\right] $$ this runs on afterward

What are we looking for in an inline block? $\bigl( \begin{smallmatrix} a & b \\ c & d \end{smallmatrix} \bigr)$ and then additional text

$$ \begin{align}
\sqrt{37} & = \sqrt{\frac{73^2-1}{12^2}} \\
 & = \sqrt{\frac{73^2}{12^2}\cdot\frac{73^2-1}{73^2}} \\ 
 & = \sqrt{\frac{73^2}{12^2}}\sqrt{\frac{73^2-1}{73^2}} \\
 & = \frac{73}{12}\sqrt{1 - \frac{1}{73^2}} \\ 
 & \approx \frac{73}{12}\left(1 - \frac{1}{2\cdot73^2}\right)
\end{align} $$

$$ \begin{array}{c|lcr}
n & \text{Left} & \text{Center} & \text{Right} \\
\hline
1 & 0.24 & 1 & 125 \\
2 & -1 & 189 & -8 \\
3 & -20 & 2000 & 1+10i
\end{array} $$

# Double Dollar Sign on a separate line. Is this supported?

$$
\left\{ 
\begin{array}{c}
a_1x+b_1y+c_1z=d_1 \\ 
a_2x+b_2y+c_2z=d_2 \\ 
a_3x+b_3y+c_3z=d_3
\end{array}
\right. 
$$

This is the end of the html.