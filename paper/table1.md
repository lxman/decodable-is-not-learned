| capability | task | probe label | surface basis | split (held-out / observed values) | val / train / disc. | fate |
|---|---|---|---|---|---|---|
| bin2dec | binary to decimal, 8-12 bits | value mod 10 (0-9) | bit-string (3968 significant 8-12-bit strings) | 0.2 → 400/2,000 | 400 / 1,600 / 0 | attrited |
| collatz2 | two Collatz steps | ones digit of the FIRST-step result (0-9) | N token (~9990 values) | 0.2 → 400/2,000 | 400 / 1,600 / 0 | attrited |
| digitprod7 | product of 4 digits (1-9), mod 7 | the product mod 7 (0-6) | the number token (9^4 = 6561 values) | 0.2 → 400/2,000 | 400 / 1,600 / 0 | attrited |
| isqrt | integer square root of N (100-9999) | ones digit of the root (0-9) | N token (~9900 values) | 0.2 → 400/2,000 | 400 / 1,600 / 0 | attrited |
| mod7_add | (a+b) mod 7, 2-digit operands | a mod 7 (0-6) | first operand token (90 values) | 0.2 → 18/90 | 400 / 1,600 / 0 | attrited |
| mod7_mul | (a*b) mod 7, 2-digit operands | a mod 7 (0-6) | first operand token (90 values) | 0.2 → 18/90 | 396 / 1,604 / 0 | attrited |
| mul3x1 | 3-digit x 1-digit multiplication | tens digit of the product (0-9) | the 3-digit operand token (900 values) | 0.2 → 167/835 | 392 / 1,608 / 0 | attrited |
| numletter | (N x alphabet position) mod 26 | the result (0-25) | N token (990 values); letters all seen | 0.2 → 174/867 | 402 / 1,598 / 0 | attrited |
| roman | roman numeral addition (values 1-99) | first numeral's value mod 10 (0-9) | first numeral string (99 values) | 0.2 → 20/99 | 400 / 1,600 / 0 | attrited |
| sq_mod7 | (a^2 + b) mod 7, 2-digit operands | a^2 mod 7 (quadratic residues: 0, 1, 2, 4) | the squared operand token (90 values) | 0.2 → 18/90 | 403 / 1,597 / 0 | attrited |
| units | metric conversion (power 1-3) | power of 10 (1-3) | unit pair (16 values; design's 3/16 holdout overrides the 15-value minimum) | 0.2 → 3/16 | 378 / 1,622 / 0 | attrited |
| unscramble | unscramble a 5-6 letter word | first letter of the solution | the solution word (multiset-unique pool) | 0.2 → 150/736 | 407 / 1,593 / 0 | attrited |
| weekday | day-of-week offset, N <= 499 | N mod 7 (0-6) | offset token N (~499 values) | 0.2 → 100/497 | 403 / 1,597 / 0 | attrited |
| add3_mid | 3-digit addition | middle digit of the sum (0-9) | tens-digit pair (100 values) | 0.2 → 20/100 | 413 / 1,587 / 0 | survivor |
| add_base8 | octal addition, 2-digit operands | ones digit of the octal sum (0-7) | ones-digit pair in base 8 (64 values) | 0.2 → 13/64 | 409 / 1,591 / 0 | survivor |
| antonym | which option is the opposite of the cue | answer position (1-4) | the cue word (the cue-answer association is the lookup) | 0.2 → 24/117 | 408 / 1,592 / 0 | survivor |
| base7 | write N in base 7 | N mod 7 (0-6, the last digit) | N token (~9990 values) | 0.2 → 400/2,000 | 400 / 1,600 / 0 | survivor |
| caesar | decode a Caesar shift (k stated, 1-5) | first letter of the decoded word | (first cipher letter, shift) combo (~130 values) | 0.2 → 44/110 | 795 / 1,205 / 0 | survivor |
| clock24 | 24-hour clock, +D hours (D 25-499) | (H+D) mod 24 (0-23) | offset token D (475 values); mod-of-offset sibling of weekday | 0.2 → 95/471 | 405 / 1,595 / 0 | survivor |
| count_div7 | count of multiples of 7 in [a, b] | the count (~4-18) | both endpoint tokens (shared value space) | 0.45 → 446/882; 446/934 | 824 / 1,201 / 1,975 | survivor |
| mod13 | (a+b) mod 13, 3-digit operands | a mod 13 (0-12) | first operand token (900 values) | 0.2 → 164/817 | 391 / 1,609 / 0 | survivor |
| oct2dec | octal to decimal, 3-4 octal digits | value mod 10 (0-9) | octal string (4,032 values); value-mod-10 sibling of bin2dec | 0.2 → 400/2,000 | 400 / 1,600 / 0 | survivor |
| odd_one_out | which of 4 words is not like the others | answer position (1-4) | all 4 words (shared components over the category vocab) | 0.45 → 72/130; 72/149; 72/151; 72/136 | 338 / 741 / 6,921 | survivor |
| reverse_string | reverse a random 4-6 letter string | last letter of the input (26) | final BPE chunk of the input (chunks, not strings, are the lookup unit) | 0.2 → 130/650 | 408 / 1,592 / 0 | survivor |
| sub3_mid | 3-digit subtraction (non-negative) | middle digit of the difference (0-9) | tens-digit pair (100 values) | 0.2 → 20/100 | 408 / 1,592 / 0 | survivor |
