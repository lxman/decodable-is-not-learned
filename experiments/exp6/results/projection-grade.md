# Experiment 6 — complete numerical projection grading

Source: the pre-sweep `../projection.md`; values from the once-written `verdict.json`.
HIT means inside the inclusive range, with no extra tolerance. Ineligible cells are not graded.

## Eight test forecasts

| Test | Point | Range | Actual T | Numeric | Called fire | Actual fire | Binary |
|---|---:|---|---:|---|---|---|---|
| A:smollm3_3b | 0.14 | [0.06, 0.22] | 0.154133 | HIT | True | True | HIT |
| A:olmo7b | 0.13 | [0.05, 0.21] | 0.143134 | HIT | True | True | HIT |
| A:olmo13b | 0.15 | [0.07, 0.23] | 0.112472 | HIT | True | True | HIT |
| A:comma_7b | 0.09 | [0.01, 0.17] | 0.168934 | HIT | False | True | MISS |
| B:smollm3_3b | 0.18 | [0.09, 0.27] | 0.194494 | HIT | True | True | HIT |
| B:olmo7b | 0.17 | [0.08, 0.26] | 0.206738 | HIT | True | True | HIT |
| B:olmo13b | 0.19 | [0.10, 0.28] | 0.158083 | HIT | True | True | HIT |
| B:comma_7b | 0.13 | [0.04, 0.22] | 0.183817 | HIT | True | True | HIT |

## Every eligible per-rung cell

| Test | Rung | Range | Actual D | Grade |
|---|---|---|---:|---|
| A:smollm3_3b | unscramble_short | [0.08, 0.35] | 0.164808 | HIT |
| A:smollm3_3b | unscramble_long | [0.08, 0.35] | 0.197493 | HIT |
| A:smollm3_3b | ipa_word | [-0.04, 0.20] | 0.151322 | HIT |
| A:smollm3_3b | sort3 | [0.03, 0.28] | 0.149472 | HIT |
| A:smollm3_3b | sort5 | [0.03, 0.28] | 0.023359 | LOW |
| A:smollm3_3b | deduction3 | [0.00, 0.25] | 0.068427 | HIT |
| A:smollm3_3b | deduction5 | [0.00, 0.25] | 0.145177 | HIT |
| A:smollm3_3b | ascii_bubble | [-0.02, 0.24] | 0.254475 | HIGH |
| A:smollm3_3b | shapes | [-0.03, 0.22] | 0.269197 | HIGH |
| A:smollm3_3b | lcs | [-0.04, 0.23] | 0.118336 | HIT |
| A:smollm3_3b | unit_interp1 | [-0.04, 0.20] | 0.093429 | HIT |
| A:smollm3_3b | unit_interp2 | [-0.04, 0.20] | 0.214098 | HIGH |
| A:olmo7b | unscramble_short | [0.08, 0.35] | 0.147084 | HIT |
| A:olmo7b | unscramble_long | [0.08, 0.35] | 0.144080 | HIT |
| A:olmo7b | ipa_word | [-0.04, 0.20] | 0.093917 | HIT |
| A:olmo7b | sort3 | [0.03, 0.28] | 0.136331 | HIT |
| A:olmo7b | sort5 | [0.03, 0.28] | 0.024023 | LOW |
| A:olmo7b | deduction3 | [0.00, 0.25] | 0.074808 | HIT |
| A:olmo7b | deduction5 | [0.00, 0.25] | 0.119467 | HIT |
| A:olmo7b | ascii_bubble | [-0.02, 0.24] | 0.215887 | HIT |
| A:olmo7b | shapes | [-0.03, 0.22] | 0.309474 | HIGH |
| A:olmo7b | unit_interp2 | [-0.04, 0.20] | 0.166271 | HIT |
| A:olmo13b | unscramble_short | [0.08, 0.35] | 0.105884 | HIT |
| A:olmo13b | unscramble_long | [0.08, 0.35] | 0.082739 | HIT |
| A:olmo13b | ipa_word | [-0.04, 0.20] | 0.060858 | HIT |
| A:olmo13b | sort3 | [0.03, 0.28] | 0.129030 | HIT |
| A:olmo13b | sort5 | [0.03, 0.28] | 0.000194 | LOW |
| A:olmo13b | deduction3 | [0.00, 0.25] | 0.055674 | HIT |
| A:olmo13b | deduction5 | [0.00, 0.25] | 0.117984 | HIT |
| A:olmo13b | ascii_bubble | [-0.02, 0.24] | 0.190920 | HIT |
| A:olmo13b | shapes | [-0.03, 0.22] | 0.181463 | HIT |
| A:olmo13b | lcs | [-0.04, 0.23] | 0.155076 | HIT |
| A:olmo13b | unit_interp1 | [-0.04, 0.20] | 0.174499 | HIT |
| A:olmo13b | unit_interp2 | [-0.04, 0.20] | 0.095337 | HIT |
| A:comma_7b | modarith_add1 | [-0.05, 0.22] | 0.008148 | HIT |
| A:comma_7b | unscramble_short | [0.08, 0.35] | 0.270707 | HIT |
| A:comma_7b | ipa_word | [-0.04, 0.20] | 0.311070 | HIGH |
| A:comma_7b | sort3 | [0.03, 0.28] | 0.250757 | HIT |
| A:comma_7b | sort5 | [0.03, 0.28] | 0.087938 | HIT |
| A:comma_7b | deduction3 | [0.00, 0.25] | 0.088456 | HIT |
| A:comma_7b | deduction5 | [0.00, 0.25] | 0.041906 | HIT |
| A:comma_7b | ascii_bubble | [-0.02, 0.24] | 0.297946 | HIGH |
| A:comma_7b | unit_interp2 | [-0.04, 0.20] | 0.163474 | HIT |
| B:smollm3_3b | unscramble_short | [0.12, 0.42] | 0.291753 | HIT |
| B:smollm3_3b | unscramble_long | [0.12, 0.42] | 0.254356 | HIT |
| B:smollm3_3b | ipa_word | [0.00, 0.28] | 0.353255 | HIGH |
| B:smollm3_3b | sort3 | [0.07, 0.35] | 0.163634 | HIT |
| B:smollm3_3b | sort5 | [0.07, 0.35] | 0.067407 | LOW |
| B:smollm3_3b | deduction3 | [0.03, 0.32] | 0.158873 | HIT |
| B:smollm3_3b | deduction5 | [0.03, 0.32] | 0.070640 | HIT |
| B:smollm3_3b | ascii_bubble | [0.00, 0.30] | 0.262432 | HIT |
| B:smollm3_3b | shapes | [0.00, 0.28] | 0.293565 | HIGH |
| B:smollm3_3b | lcs | [-0.02, 0.28] | 0.070060 | HIT |
| B:smollm3_3b | unit_interp1 | [-0.02, 0.24] | 0.124423 | HIT |
| B:smollm3_3b | unit_interp2 | [-0.02, 0.24] | 0.223534 | HIT |
| B:olmo7b | unscramble_short | [0.12, 0.42] | 0.254557 | HIT |
| B:olmo7b | unscramble_long | [0.12, 0.42] | 0.186876 | HIT |
| B:olmo7b | ipa_word | [0.00, 0.28] | 0.258621 | HIT |
| B:olmo7b | sort3 | [0.07, 0.35] | 0.202333 | HIT |
| B:olmo7b | sort5 | [0.07, 0.35] | 0.032019 | LOW |
| B:olmo7b | deduction3 | [0.03, 0.32] | 0.176210 | HIT |
| B:olmo7b | deduction5 | [0.03, 0.32] | 0.115892 | HIT |
| B:olmo7b | ascii_bubble | [0.00, 0.30] | 0.201486 | HIT |
| B:olmo7b | shapes | [0.00, 0.28] | 0.368603 | HIGH |
| B:olmo7b | unit_interp2 | [-0.02, 0.24] | 0.270778 | HIGH |
| B:olmo13b | unscramble_short | [0.12, 0.42] | 0.193883 | HIT |
| B:olmo13b | unscramble_long | [0.12, 0.42] | 0.152817 | HIT |
| B:olmo13b | ipa_word | [0.00, 0.28] | 0.206644 | HIT |
| B:olmo13b | sort3 | [0.07, 0.35] | 0.131919 | HIT |
| B:olmo13b | sort5 | [0.07, 0.35] | 0.006878 | LOW |
| B:olmo13b | deduction3 | [0.03, 0.32] | 0.096205 | HIT |
| B:olmo13b | deduction5 | [0.03, 0.32] | 0.107504 | HIT |
| B:olmo13b | ascii_bubble | [0.00, 0.30] | 0.167014 | HIT |
| B:olmo13b | shapes | [0.00, 0.28] | 0.305234 | HIGH |
| B:olmo13b | lcs | [-0.02, 0.28] | 0.037189 | HIT |
| B:olmo13b | unit_interp1 | [-0.02, 0.24] | 0.264884 | HIGH |
| B:olmo13b | unit_interp2 | [-0.02, 0.24] | 0.226821 | HIT |
| B:comma_7b | modarith_add1 | [-0.03, 0.28] | -0.028791 | HIT |
| B:comma_7b | unscramble_short | [0.12, 0.42] | 0.352948 | HIT |
| B:comma_7b | ipa_word | [0.00, 0.28] | 0.465939 | HIGH |
| B:comma_7b | sort3 | [0.07, 0.35] | 0.103667 | HIT |
| B:comma_7b | sort5 | [0.07, 0.35] | 0.042784 | LOW |
| B:comma_7b | deduction3 | [0.03, 0.32] | 0.086670 | HIT |
| B:comma_7b | deduction5 | [0.03, 0.32] | 0.140497 | HIT |
| B:comma_7b | ascii_bubble | [0.00, 0.30] | 0.263008 | HIT |
| B:comma_7b | unit_interp2 | [-0.02, 0.24] | 0.227631 | HIT |

Totals: {"A": {"HIT": 34, "LOW": 3, "HIGH": 6}, "B": {"HIT": 32, "LOW": 4, "HIGH": 7}}

Both Comma unscramble_long cells are THIN (13 ever-correct items); neither is graded.
Endpoint exclusions were known when the projection was made and receive no forecast credit.
