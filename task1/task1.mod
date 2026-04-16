set VENUES;
set SPORTS;

param cost {VENUES};
param capacity {VENUES};
param max_sports {VENUES};
param demand {SPORTS};
param sessions_req {SPORTS};
param eligibility {VENUES, SPORTS};

var y {VENUES} binary;
var x {VENUES, SPORTS} binary;

minimize TotalCost: sum {i in VENUES} cost[i] * y[i];

subject to Demand {j in SPORTS}:
    sum {i in VENUES} x[i, j] = 1;

subject to Eligibility {i in VENUES, j in SPORTS}:
    x[i, j] <= eligibility[i, j];

subject to Activation {i in VENUES, j in SPORTS}:
    x[i, j] <= y[i];

subject to Capacity {i in VENUES}:
    sum {j in SPORTS} x[i, j] <= max_sports[i];