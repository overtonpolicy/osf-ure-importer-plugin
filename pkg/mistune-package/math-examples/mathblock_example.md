# MathTex Examples

## Math Block

```````````````````````````````` example
~~[hello](/)~~
.
<p><del><a href="/">hello</a></del></p>
````````````````````````````````


## Math Blocks

### Standard Math Block

$$\alpha\beta*2^{3i}$$ 

### Standard Math Block with spaces around the fence

$$ \alpha\beta*2^{3i} $$ 

### Multiline Math Block

Multiline Block:

$$\alpha
\beta
*2^{3i}$$

Padded Multiline Block:

$$ \alpha
\beta
*2^{3i} $$

### Multiline Math Block with a close heading

Multiline Block:
$$\alpha
\beta
*2^{3i}$$
Closing

Multiline Block:
$$\alpha
\beta
*2^{3i}$$

Padded Multiline Block:
$$ \alpha
\beta
*2^{3i} $$
Closing

Padded Multiline Block:
$$ \alpha
\beta
*2^{3i} $$


### Math Block that starts inline

This should be on a separate line : $$\alpha\beta*2^{3i}$$ This line should be standalone on a new line.

This should be on a separate line : $$ \alpha\beta*2^{3i} $$ This line should be standalone on a new line.

### Math Block that starts inline and is multiline

This should be on a separate line : $$\alpha
\beta
*2^{3i}$$ This line should be standalone on a new line.

This should be on a separate line : $$ \alpha
\beta
*2^{3i} $$ This line should be standalone on a new line.

### Edge Cases

Test the regexp for a single character $$k$$ math block.

Test the regexp for a single character padded $$ k $$ math block.


## Bad Syntax and False Clauses

### {Block Open} ... {Span Closed} 

The equation should not render. The block open should render as a span, leaving the {Span Close} to be rendered as a standalone dollar sign: $$\alpha\beta*2^{3i}$

The equation should not render. The block open should render as a span, leaving the {Span Close} to be rendered as a standalone dollar sign: $$ \alpha\beta*2^{3i} $

### {Span Open} ... {Block Closed} 

The equation should render as a math span with a dollar sign following it. The {Span Open} matches with the first character of {Block Closed}, leaving the second character on its own: $\alpha\beta*2^{3i}$$

The equation should render as a math span with a dollar sign following it. The {Span Open} matches with the first character of {Block Closed}, leaving the second character on its own: $ \alpha\beta*2^{3i} $$

### Multiple Legitimate dollar values.

If I have $3 dollars and I give you $2, then nothing should render.

If I have some $ and I give you a little $ then nothing should render.

What If I have some money: $$ ?

What If I have lots of money: $$$$ 



