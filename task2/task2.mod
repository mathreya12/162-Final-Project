set VENUES;
set SPORTS;

param cost {VENUES};
param capacity {VENUES};
param max_sports {VENUES};
param demand {SPORTS};
param sessions_req {SPORTS};
param eligibility {VENUES, SPORTS};

var y {VENUES} binary;
var s {VENUES, SPORTS} binary;

minimize TotalCost: sum {i in VENUES} cost[i] * y[i];

subject to Req {j in SPORTS}:
    sum {i in VENUES} s[i, j] = sessions_req[j];

subject to VenueSlots {i in VENUES}:
    sum {j in SPORTS} s[i, j] <= max_sports[i] * y[i];

subject to Elig {i in VENUES, j in SPORTS}:
    s[i, j] <= eligibility[i, j] * y[i];
    

