### A.1 One item per capability

- **bin2dec** — "What is binary 1111000111 in decimal?" → 967 (probe label: 7)
- **collatz2** — "Apply the Collatz rule (if even, halve; if odd, triple and add 1) twice to 4543. What is the result?" → 6815 (probe label: 0)
- **digitprod7** — "What is the product of the digits of 5545, mod 7?" → 3 (probe label: 3)
- **isqrt** — "What is the integer square root (rounded down) of 9470?" → 97 (probe label: 7)
- **mod7_add** — "What is (57 + 38) mod 7?" → 4 (probe label: 1)
- **mod7_mul** — "What is (18 * 76) mod 7?" → 3 (probe label: 4)
- **mul3x1** — "What is 267 * 4?" → 1068 (probe label: 6)
- **numletter** — "Multiply 168 by the alphabet position of 'j'. What is the result mod 26?" → 16 (probe label: 16)
- **roman** — "What is LXVII + LXXXVII in decimal?" → 154 (probe label: 7)
- **sq_mod7** — "What is (22^2 + 99) mod 7?" → 2 (probe label: 1)
- **units** — "How many milliliters are in 254 centiliters?" → 2540 (probe label: 1)
- **unscramble** — "Unscramble the letters 'gloan' to form an English word." → along (probe label: a)
- **weekday** — "What day of the week is 252 days after Sunday?" → Sunday (probe label: 0)
- **add3_mid** — "What is 157 + 456?" → 613 (probe label: 1)
- **add_base8** — "What is 67 + 76 in base 8 (both numbers are octal)?" → 165 (probe label: 5)
- **antonym** — "Which of these means the opposite of 'innocent': busy, firm, exact, guilty?" → guilty (probe label: 4)
- **base7** — "Write 8622 in base 7." → 34065 (probe label: 5)
- **caesar** — "The word 'jsywd' was made by shifting each letter of a word forward by 5. What was the original word?" → entry (probe label: e)
- **clock24** — "It is 2:00 on a 24-hour clock. What time will it be in 130 hours? Answer as H:00." → 12:00 (probe label: 12)
- **count_div7** — "How many integers between 88 and 134 (inclusive) are divisible by 7?" → 7 (probe label: 7)
- **mod13** — "What is (659 + 800) mod 13?" → 3 (probe label: 9)
- **oct2dec** — "What is octal 6302 in decimal?" → 3266 (probe label: 6)
- **odd_one_out** — "Which word is not like the others: heron, swan, pear, owl?" → pear (probe label: 3)
- **reverse_string** — "Spell the string 'vuldr' backwards." → rdluv (probe label: r)
- **sub3_mid** — "What is 328 - 124?" → 204 (probe label: 0)

### A.2 All starved margins, per seed

| capability | 410M untrained | 410M trained | 1B untrained | 1B trained |
|---|---|---|---|---|
| bin2dec | 0.08 / 0.08 / 0.06 / 0.00 / 0.06 | 0.00 / 0.07 / 0.00 / 0.00 / 0.00 | 0.00 / 0.00 / 0.00 / 0.00 / 0.07 | 0.00 / 0.00 / 0.00 / 0.00 / 0.00 |
| collatz2 | 0.76 / 0.77 / 0.78 / 0.75 / 0.74 | 0.94 / 0.93 / 0.93 / 0.92 / 0.93 | 0.81 / 0.81 / 0.79 / 0.78 / 0.75 | 0.96 / 0.96 / 0.95 / 0.97 / 0.97 |
| digitprod7 | 0.22 / 0.21 / 0.28 / 0.20 / 0.24 | 0.28 / 0.27 / 0.36 / 0.26 / 0.29 | 0.22 / 0.21 / 0.30 / 0.19 / 0.26 | 0.28 / 0.27 / 0.34 / 0.26 / 0.29 |
| isqrt | 0.41 / 0.36 / 0.38 / 0.42 / 0.38 | 0.62 / 0.57 / 0.62 / 0.63 / 0.57 | 0.44 / 0.37 / 0.43 / 0.40 / 0.38 | 0.66 / 0.63 / 0.67 / 0.66 / 0.63 |
| mod7_add | 0.00 / 0.00 / 0.00 / 0.00 / 0.00 | 0.00 / 0.00 / 0.00 / 0.00 / 0.00 | 0.00 / 0.10 / 0.00 / 0.09 / 0.00 | 0.00 / 0.00 / 0.00 / 0.00 / 0.00 |
| mod7_mul | 0.00 / 0.10 / 0.00 / 0.00 / 0.00 | 0.00 / 0.00 / 0.00 / 0.00 / 0.00 | 0.00 / 0.00 / 0.00 / 0.11 / 0.00 | 0.00 / 0.00 / 0.00 / 0.00 / 0.00 |
| mul3x1 | 0.09 / 0.08 / 0.00 / 0.11 / 0.00 | 0.13 / 0.13 / 0.13 / 0.14 / 0.14 | 0.09 / 0.08 / 0.07 / 0.11 / 0.09 | 0.21 / 0.17 / 0.19 / 0.16 / 0.17 |
| numletter | 0.06 / 0.09 / 0.08 / 0.06 / 0.10 | 0.11 / 0.10 / 0.11 / 0.10 / 0.10 | 0.07 / 0.07 / 0.08 / 0.06 / 0.07 | 0.09 / 0.12 / 0.12 / 0.11 / 0.09 |
| roman | 0.65 / 0.77 / 0.68 / 0.66 / 0.78 | 0.84 / 0.86 / 0.82 / 0.89 / 0.96 | 0.64 / 0.74 / 0.69 / 0.72 / 0.82 | 0.89 / 0.90 / 0.86 / 0.84 / 0.90 |
| sq_mod7 | 0.00 / 0.13 / 0.00 / 0.00 / 0.00 | 0.00 / 0.00 / 0.00 / 0.00 / 0.00 | 0.00 / 0.26 / 0.00 / 0.00 / 0.00 | 0.00 / 0.13 / 0.00 / 0.00 / 0.00 |
| units | 0.00 / 0.00 / 0.39 / 0.00 / 0.00 | 0.00 / 0.45 / 0.52 / 0.00 / 0.00 | 0.00 / 0.00 / 0.52 / 0.00 / 0.00 | 0.00 / 0.00 / 0.52 / 0.15 / 0.00 |
| unscramble | 0.20 / 0.18 / 0.22 / 0.18 / 0.20 | 0.32 / 0.25 / 0.29 / 0.31 / 0.33 | 0.21 / 0.19 / 0.22 / 0.21 / 0.19 | 0.33 / 0.30 / 0.32 / 0.32 / 0.33 |
| weekday | 0.00 / 0.09 / 0.00 / 0.11 / 0.00 | 0.09 / 0.08 / 0.00 / 0.00 / 0.00 | 0.08 / 0.12 / 0.09 / 0.00 / 0.00 | 0.00 / 0.00 / 0.00 / 0.00 / 0.09 |
| add3_mid | 0.00 / 0.00 / 0.00 / 0.00 / 0.00 | 0.00 / 0.00 / 0.00 / 0.00 / 0.00 | 0.00 / 0.00 / 0.00 / 0.00 / 0.00 | 0.00 / 0.00 / 0.00 / 0.00 / 0.00 |
| add_base8 | 0.00 / 0.00 / 0.00 / 0.00 / 0.00 | 0.00 / 0.00 / 0.00 / 0.00 / 0.00 | 0.00 / 0.00 / 0.00 / 0.00 / 0.00 | 0.00 / 0.00 / 0.00 / 0.00 / 0.00 |
| antonym | 0.00 / 0.00 / 0.00 / 0.00 / 0.00 | 0.57 / 0.58 / 0.62 / 0.53 / 0.59 | 0.00 / 0.00 / 0.00 / 0.00 / 0.00 | 0.52 / 0.47 / 0.44 / 0.36 / 0.45 |
| base7 | 0.00 / 0.00 / 0.00 / 0.00 / 0.00 | 0.00 / 0.00 / 0.00 / 0.00 / 0.00 | 0.00 / 0.00 / 0.00 / 0.00 / 0.00 | 0.00 / 0.00 / 0.00 / 0.00 / 0.00 |
| caesar | 0.00 / 0.00 / 0.00 / 0.00 / 0.00 | 0.00 / 0.00 / 0.00 / 0.00 / 0.00 | 0.00 / 0.00 / 0.00 / 0.00 / 0.00 | 0.00 / 0.00 / 0.00 / 0.00 / 0.00 |
| clock24 | 0.00 / 0.00 / 0.00 / 0.00 / 0.00 | 0.00 / 0.00 / 0.00 / 0.00 / 0.00 | 0.00 / 0.00 / 0.00 / 0.00 / 0.00 | 0.00 / 0.00 / 0.00 / 0.05 / 0.00 |
| count_div7 | 0.00 / 0.00 / 0.00 / 0.00 / 0.00 | 0.11 / 0.12 / 0.13 / 0.10 / 0.11 | 0.00 / 0.00 / 0.00 / 0.00 / 0.00 | 0.10 / 0.12 / 0.13 / 0.10 / 0.10 |
| mod13 | 0.00 / 0.00 / 0.00 / 0.00 / 0.00 | 0.00 / 0.00 / 0.00 / 0.00 / 0.00 | 0.00 / 0.00 / 0.00 / 0.00 / 0.00 | 0.00 / 0.00 / 0.00 / 0.00 / 0.00 |
| oct2dec | 0.00 / 0.00 / 0.00 / 0.00 / 0.00 | 0.00 / 0.00 / 0.00 / 0.00 / 0.00 | 0.00 / 0.00 / 0.00 / 0.00 / 0.00 | 0.00 / 0.00 / 0.00 / 0.00 / 0.00 |
| odd_one_out | 0.00 / 0.00 / 0.00 / 0.00 / 0.00 | 0.33 / 0.25 / 0.33 / 0.32 / 0.39 | 0.00 / 0.00 / 0.00 / 0.00 / 0.00 | 0.24 / 0.23 / 0.28 / 0.31 / 0.30 |
| reverse_string | 0.00 / 0.00 / 0.00 / 0.00 / 0.00 | 0.57 / 0.52 / 0.62 / 0.60 / 0.55 | 0.00 / 0.00 / 0.00 / 0.00 / 0.00 | 0.69 / 0.58 / 0.70 / 0.78 / 0.61 |
| sub3_mid | 0.00 / 0.00 / 0.00 / 0.00 / 0.00 | 0.00 / 0.00 / 0.00 / 0.00 / 0.00 | 0.00 / 0.00 / 0.00 / 0.00 / 0.00 | 0.00 / 0.00 / 0.00 / 0.00 / 0.00 |
