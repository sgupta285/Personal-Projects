# Stakeholder Summary

## Executive summary

This measurement pack compares rule-based attribution, a model-based attribution view, and spend response curves for the same synthetic marketing system. The outputs are designed for budget planning, not for making causal claims stronger than the data supports.

## Headline numbers

- Journeys analyzed: **12,000**
- Touchpoints analyzed: **53,997**
- Conversion rate: **11.25%**
- Total conversions: **1,350**
- Revenue: **$344,418.98**
- Media spend: **$435,891.94**
- Blended ROAS: **0.79**

## Attribution readout

- Rule-based methods disagree most on direct, email, and paid social.
- The model-based view keeps search and email strong while reducing some of the last-touch inflation that shows up in direct traffic.
- The biggest difference between the baseline and model-based views is that upper- and mid-funnel channels recover more contribution once the full path is considered.

## Response curve readout

- Best current marginal return: **email**
- Lowest current marginal return: **paid_search**
- Estimated daily conversion lift from reallocation: **10.21**
- Estimated daily revenue lift from reallocation: **$1,755.37**

## Budget recommendation

Move budget toward:
| channel     |   spend_delta |
|:------------|--------------:|
| email       |           500 |
| paid_social |           250 |

Move budget away from:
| channel     |   spend_delta |
|:------------|--------------:|
| paid_search |          -500 |
| display     |          -500 |

## Measurement caveats

- Do not interpret this as causal incrementality proof.
- Keep holdout or geo experiments as the next validation layer for any major budget move.
- Direct and organic channels still need careful handling because they often absorb intent created elsewhere.

## Experiment hooks

Before scaling the reallocation plan, validate one or more of the following:

1. geo-based holdout for search or social
2. incrementality test for email cadence
3. regional affiliate on/off test
4. creative holdout inside paid social
