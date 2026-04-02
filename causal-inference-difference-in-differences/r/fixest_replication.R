library(data.table)
library(fixest)

args <- commandArgs(trailingOnly = TRUE)
path <- ifelse(length(args) > 0, args[[1]], "data/sample/panel.csv")
dt <- fread(path)

dt[, did_term := ever_treated * post]
base_fit <- feols(outcome ~ did_term + covariate | unit_id + time_id, cluster = ~unit_id, data = dt)
print(summary(base_fit))

event_fit <- feols(outcome ~ sunab(treatment_cohort, time_id) + covariate | unit_id + time_id, cluster = ~unit_id, data = dt[ever_treated == 1 | ever_treated == 0])
print(summary(event_fit))
