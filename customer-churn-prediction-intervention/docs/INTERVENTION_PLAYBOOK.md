# Intervention Playbook

## Risk tiers

- **Critical**: probability >= 0.80
- **High**: probability >= 0.65 and < 0.80
- **Medium**: probability >= 0.40 and < 0.65
- **Low**: probability < 0.40

## Routing logic

### Critical
- If MRR >= 1500 or the plan tier is enterprise: assign to customer success immediately
- Otherwise: send a targeted save offer and flag for a check-in

### High
- If payment failures exist: route through billing recovery plus product education
- If unresolved support or poor adoption is present: route to customer success plus onboarding refresh
- Otherwise: use lifecycle outreach with tailored value proof

### Medium
- Use product education, in-app guidance, and lifecycle reinforcement

### Low
- Monitor only

## Why this policy exists

High-touch human interventions are limited resources. The policy is designed to reserve expensive retention work for the accounts where the expected value is highest.
