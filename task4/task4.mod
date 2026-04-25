set VENUES ordered;
set SPORTS;

param cost {VENUES};
param capacity {VENUES};
param max_sports {VENUES};
param demand {SPORTS};
param sessions_req {SPORTS};
param eligibility {VENUES, SPORTS};

param ticket_profit default 10;
param bus_cost      default 20;
param demand_scale  default 1;

set PAIRS   := {i in VENUES, k in VENUES:              ord(i) < ord(k)};
set TRIPLES := {i in VENUES, k in VENUES, l in VENUES: ord(i) < ord(k) < ord(l)};

param T_MAX := max {i in VENUES} max_sports[i];
set WEEKS := 1..T_MAX;

param eff_demand {j in SPORTS} := demand_scale * demand[j];

# Pre-bus base tickets at (i,j): used as the source of bus outflow so that
# destination tickets don't recursively depend on their own inflow.
param base_tix {i in VENUES, j in SPORTS} := min(eff_demand[j], capacity[i]);
param M_TIX := max {i in VENUES, j in SPORTS} base_tix[i,j];

var y {VENUES} binary;
var x {i in VENUES, j in SPORTS, t in WEEKS:
       eligibility[i,j] = 1 and t <= max_sports[i]} binary;
var h {SPORTS, WEEKS} binary;
var w {VENUES, WEEKS} >= 0, <= 1;
var b2 {PAIRS}   binary;
var b3 {TRIPLES} binary;

# a3F[p,q,r,t] = 1 iff triple (p,q,r) has a 3-venue network AND all three
# host in week t (7%-each-pair full mode).
var a3F {TRIPLES, WEEKS} binary;

# pair10[p,q,t] = 1 iff pair {p,q} runs in 10% mode in week t (either a
# 2-venue network, or a 3-venue network with the third venue idle).
var pair10 {PAIRS, WEEKS} binary;

var f {i in VENUES, k in VENUES, t in WEEKS: i <> k} >= 0;
var T {VENUES, WEEKS} >= 0;

minimize NetCost:
      sum {i in VENUES} cost[i] * y[i]
    + bus_cost * (sum {(i,k)   in PAIRS}   b2[i,k]
                + sum {(i,k,l) in TRIPLES} b3[i,k,l])
    - ticket_profit * sum {i in VENUES, t in WEEKS} T[i,t];

subject to SportWeek {j in SPORTS}:
    sum {t in WEEKS} h[j,t] = 1;

subject to SportSessions {j in SPORTS}:
    sum {i in VENUES, t in WEEKS:
         eligibility[i,j] = 1 and t <= max_sports[i]} x[i,j,t] = sessions_req[j];

subject to SessionInChosenWeek
    {i in VENUES, j in SPORTS, t in WEEKS:
     eligibility[i,j] = 1 and t <= max_sports[i]}:
    x[i,j,t] <= h[j,t];

subject to VenueWeekCap {i in VENUES, t in WEEKS: t <= max_sports[i]}:
    sum {j in SPORTS: eligibility[i,j] = 1} x[i,j,t] <= y[i];

subject to WDef {i in VENUES, t in WEEKS: t <= max_sports[i]}:
    w[i,t] = sum {j in SPORTS: eligibility[i,j] = 1} x[i,j,t];

subject to WZero {i in VENUES, t in WEEKS: t > max_sports[i]}:
    w[i,t] = 0;

subject to OneNetwork {v in VENUES}:
      sum {(p,q)   in PAIRS:   p = v or q = v}             b2[p,q]
    + sum {(p,q,r) in TRIPLES: p = v or q = v or r = v}    b3[p,q,r]
    <= 1;

# Averaged UB: valid because a3F is binary (forced to 0 unless b3 and all
# three w's equal 1).
subject to A3FullUB {(p,q,r) in TRIPLES, t in WEEKS}:
    a3F[p,q,r,t] <= (b3[p,q,r] + w[p,t] + w[q,t] + w[r,t]) / 4;

subject to Pair10_Wp {(p,q) in PAIRS, t in WEEKS}: pair10[p,q,t] <= w[p,t];
subject to Pair10_Wq {(p,q) in PAIRS, t in WEEKS}: pair10[p,q,t] <= w[q,t];

# (b3 - a3F) = 1 iff the triple's 3-venue network exists but is not in full
# mode this week, i.e. exactly one of its pairs runs in 10% mode.
subject to Pair10_Net {(p,q) in PAIRS, t in WEEKS}:
    pair10[p,q,t] <=
          b2[p,q]
        + sum {(pp,qq,r) in TRIPLES: pp = p and qq = q} (b3[pp,qq,r] - a3F[pp,qq,r,t])
        + sum {(pp,r,qq) in TRIPLES: pp = p and qq = q} (b3[pp,r,qq] - a3F[pp,r,qq,t])
        + sum {(r,pp,qq) in TRIPLES: pp = p and qq = q} (b3[r,pp,qq] - a3F[r,pp,qq,t]);

# Without this, the optimizer could set a3F=0 with all three venues active
# and illegally claim 10% flow on all three pairs.
subject to TriplePairExclusion {(p,q,r) in TRIPLES, t in WEEKS}:
    pair10[p,q,t] + pair10[p,r,t] + pair10[q,r,t] <= 1;

# Flow UBs. Base caps the 10% mode, Any forces f=0 when no mode is active,
# 7 caps the full-triple mode at 7% (and is slack when in 10% mode).
subject to FlowUB_Base {i in VENUES, k in VENUES, t in WEEKS: i <> k}:
    f[i,k,t] <= 0.10 * sum {j in SPORTS:
                            eligibility[i,j] = 1 and t <= max_sports[i]}
                base_tix[i,j] * x[i,j,t];

subject to FlowUB_Any {i in VENUES, k in VENUES, t in WEEKS: i <> k}:
    f[i,k,t] <= 0.10 * M_TIX * (
          (if ord(i) < ord(k) then pair10[i,k,t] else pair10[k,i,t])
        + sum {(pp,qq,r) in TRIPLES:
               (pp=i and qq=k) or (pp=k and qq=i)
               or (pp=i and r=k) or (pp=k and r=i)
               or (qq=i and r=k) or (qq=k and r=i)} a3F[pp,qq,r,t]
        );

subject to FlowUB_7 {i in VENUES, k in VENUES, t in WEEKS: i <> k}:
    f[i,k,t] <= 0.07 * sum {j in SPORTS:
                            eligibility[i,j] = 1 and t <= max_sports[i]}
                base_tix[i,j] * x[i,j,t]
              + 0.03 * M_TIX * (if ord(i) < ord(k)
                                then pair10[i,k,t] else pair10[k,i,t]);

subject to TCap {i in VENUES, t in WEEKS}:
    T[i,t] <= capacity[i] * w[i,t];

subject to TDem {i in VENUES, t in WEEKS}:
    T[i,t] <= sum {j in SPORTS:
                   eligibility[i,j] = 1 and t <= max_sports[i]}
              eff_demand[j] * x[i,j,t]
            + sum {kk in VENUES: kk <> i} f[kk,i,t];
