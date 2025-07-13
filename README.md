# mariachi-lang

---

mariachi-lang is a programming language with a Spanish-inspired syntax. A large part of the code is from the CodePulse youtube series, [Make Your Own Programming Language](https://www.youtube.com/playlist?list=PLZQftyCk7_SdoVexSmwy_tBgs7P0b97yD). If you are interested in implementing your own language, I highly recommend this series. I modified the code a bit to model Spanish as a fun DSL-like language for basic scripting.

The tutorial is quite Javaesque and follows similar patterns as Robert Nystrom's book [Crafting Interpreters](https://craftinginterpreters.com/), so if you like the youtube series, you'll love Robert's book and I recommend checking that out as well.

With that said, the OOP nature of the tutorial is a bit overcomplex for the what I have in mind for mariachi-lang. The current goal is to refactor the code in order to make it more Pythonic while relying on Python native types, this will hopefully make it more consitent, however it will lose some of the power gained through implementing custom language types.

If you are curious in playing around with the language you can go ahead and give it a try, I am open to suggestions through pull or issues requests.

Current Status- for and while loops are both broken.
If statements sorta work now

## Getting Started

1. Clone the repo
2. Install requirements: `pip install -r requirements.txt`
3. Run the REPL: `python -m mariachi`

## Running Tests

```bash
pytest
```

## Example

```mariachi
sea x = 3
define cuadrado(n) { n * n }
cuadrado(2)
```
