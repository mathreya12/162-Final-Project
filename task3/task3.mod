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
var T {VENUES, SPORTS} >= 0;

minimize NetCost: 
    sum {i in VENUES} cost[i] * y[i] - sum {i in VENUES, j in SPORTS} 10 * T[i, j];

subject to Req {j in SPORTS}:
    sum {i in VENUES} s[i, j] = sessions_req[j];

subject to VenueSlots {i in VENUES}:
    sum {j in SPORTS} s[i, j] <= max_sports[i] * y[i];

subject to Elig {i in VENUES, j in SPORTS}:
    s[i, j] <= eligibility[i, j] * y[i];

subject to TicketsCap {i in VENUES, j in SPORTS}:
    T[i, j] <= s[i, j] * capacity[i];

subject to TicketsDem {i in VENUES, j in SPORTS}:
    T[i, j] <= s[i, j] * demand[j];