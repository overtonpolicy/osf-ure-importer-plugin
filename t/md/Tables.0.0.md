Tables
home_wiki
# Tables

This is to test table markdown rendering.

## Table 1, with bolded headings:

| **Col 1** | **Col 2** | **Col 3** | **Col 4** |
|-----------|-----------|-----------|-----------|
| A1        | B1        | C1        | D1        |
| A2        | B2        | C2        | D2        |
| A3        | B3        | C3        | D3        |

Text immediately after the table

## Table 2, with different alignments

Here, column A is left aligned, Column B is center aligned, and column C is right aligned. However, while alignment is supported in pipe\_tables, it does not appear to be rendered correctly in the pandoc AST, and so it is not currently possible to easily translate it to OSF.

| Col A | Col B | Col C |
|-------|-------|-------|
| A1    | B1    | C1    |
| A2    | B2    | C2    |

## Future: multiline table cells

Multiline tables are rendered by pandoc using grid tables, and OSF only supports pipe tables. Thus, multiline cells are not supported.
