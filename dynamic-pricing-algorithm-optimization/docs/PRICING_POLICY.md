# Pricing Policy and Guardrails

## Objective

The current pricing engine optimizes for **expected gross profit**.

## Guardrails

1. **Cost floor**
   - recommended price must stay at least 8% above unit cost

2. **Base-price band**
   - recommended price is bounded within 85% to 125% of base price

3. **Competitor fairness cap**
   - recommended price cannot exceed 115% of competitor price in the same context

4. **Daily move constraint**
   - recommended price stays within 80% to 120% of the current price

5. **Inventory-aware pricing**
   - when inventory pressure is high, the optimizer avoids unnecessary price cuts

## Why these constraints exist

Pricing projects look unrealistic when they optimize only for a model objective and ignore policy. These guardrails keep the system reviewable by a merchandising or pricing operations team and make the recommendations more credible.
