# mariachi-lang

---

mariachi-lang is a programming language with a Spanish-inspired syntax. A large part of the code is from the CodePulse youtube series, [Make Your Own Programming Language](https://www.youtube.com/playlist?list=PLZQftyCk7_SdoVexSmwy_tBgs7P0b97yD). If you are interested in implementing your own language, I highly recommend this series. I modified the code a bit to model Spanish as a fun DSL-like language for basic scripting.

The tutorial is quite Javaesque and follows similar patterns as Robert Nystrom's book [Crafting Interpreters](https://craftinginterpreters.com/), so if you like the youtube series, you'll love Robert's book and I recommend checking that out as well.

With that said, the OOP nature of the tutorial is a bit overcomplex for what I have in mind for mariachi-lang. The current goal is to refactor the code in order to make it more Pythonic while relying on Python native types, this will hopefully make it more consistent, however it will lose some of the power gained through implementing custom language types.

If you are curious in playing around with the language you can go ahead and give it a try, I am open to suggestions through pull or issues requests.

Current Status- everything should work, some strange behavior to note is all functions, statements, and loops return 0

## Getting Started

1. Clone the repo
2. Install requirements: `pip install pytest typer`
3. Run the REPL: `python -m mariachi.repl repl`

Yep, the repl entry is in a file called repl, a bit redundant, I will fix that later.

## Running Tests

```bash
pytest
```

## Example

```mariachi
sea x = 3
define cuadrado(n) { n * n }
cuadrado(2)

mientras i < 5 {
    canta(i)
    i = i + 1
}

si x > 10 {
    canta("Grande")
} quizas x > 5 {
    canta("Mediano")
} sino {
    canta("Pequeño")
}
```
