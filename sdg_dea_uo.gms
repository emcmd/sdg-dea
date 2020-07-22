* set definitions
sets
c(*)	countries
i(*)	inputs
o(*)	outputs
o_u(*)  undesired outputs
cs(c)	selected country;
alias(c,cc);

* load sets from inc file
$offlisting
$include gams_data_input/sets_sdg0.inc

* load parameter definitions and values from csv files
table input(c,i) 'inputs'
$ondelim
$offdigit
$include gams_data_input/inputs_sdg0.csv
$offdelim
;

table output(c,o) 'outputs'
$ondelim
$offdigit
$include gams_data_input/outputs_sdg0.csv
$offdelim
;

table output_u(c,o_u) 'undesired outputs'
$ondelim
$offdigit
$include gams_data_input/undes_outputs_sdg0.csv
$offdelim
;

* define remaining parameters, variables, and equations
parameters
eff_save(cc)
si_save(cc,i)
so_save(cc,o)
so_u_save(cc,o_u)
lambda_save(cc,c)
epsilon
io;

*small positive value to enforce positivity on inputs/outputs using method in Tone (2020)
epsilon = 1e-6;

* switch between input and output-oriented solve
io = 0;

variables
obj;

positive variables
slack_i(i)
slack_o(o)
slack_o_u(o_u)
lambda(c);

equations
of_sbm_uo_oo
of_sbm_uo_io
in_sbm_uo
out_sbm_uo
out_u_sbm_uo
vrs_sbm_uo;

* define output-oriented VRS SBM model with undesirable outputs (based on Tone (2001 & 2004))
of_sbm_uo_oo(cs)..          obj =e= 1 + 1/(card(o)+card(o_u)) * (sum(o, slack_o(o)/output(cs,o)) + sum(o_u, slack_o_u(o_u)/output_u(cs,o_u)));
in_sbm_uo(cs,i)..           input(cs,i) =e= sum(c, input(c,i)*lambda(c)) + slack_i(i);
out_sbm_uo(cs,o)..          output(cs,o) =e= sum(c, output(c,o)*lambda(c)) - slack_o(o);
out_u_sbm_uo(cs,o_u)..      output_u(cs,o_u) =e= sum(c, output_u(c,o_u)*lambda(c)) + slack_o_u(o_u);
vrs_sbm_uo..                sum(c,lambda(c)) =e= 1;

* define input-oriented VRS SBM model with undesirable outputs (based on Tone (2001 & 2004))
of_sbm_uo_io(cs)..          obj =e= 1-(1/card(i)) * sum(i, slack_i(i)/input(cs,i));


model sbm_uo_oo    /of_sbm_uo_oo, in_sbm_uo, out_sbm_uo, out_u_sbm_uo, vrs_sbm_uo/
model sbm_uo_io    /of_sbm_uo_io, in_sbm_uo, out_sbm_uo, out_u_sbm_uo, vrs_sbm_uo/

option optcr = 0, reslim = 10800;

* adjust base points where needed to handle negative parameter values, according to Tone (2020)
parameters
smin_i,smin_o,smin_o_u;
smin_i = smin((c,i),input(c,i));
smin_o = smin((c,o),output(c,o));
smin_o_u = smin((c,o_u),output_u(c,o_u));

if( (smin_i le 0),
    input(c,i) = input(c,i) - smin_i + epsilon;
);
if( (smin_o le 0),
    output(c,o) = output(c,o) - smin_o + epsilon;
);
if( (smin_o_u le 0),
    output_u(c,o_u) = output_u(c,o_u) - smin_o_u + epsilon;
);

* solve loop for each dmu
loop(cc,
    cs(cc) = yes;

    if((io=0),
        solve sbm_uo_oo using LP maximising obj;
        eff_save(cc) = 1/obj.l;
    elseif (io=1),
        solve sbm_uo_io using LP minimising obj;
        eff_save(cc) = obj.l;
    );

    si_save(cc,i) = slack_i.l(i);
    so_save(cc,o) = slack_o.l(o);
    so_u_save(cc,o_u) = slack_o_u.l(o_u);
    lambda_save(cc,c) = lambda.l(c);
    cs(cc) = no;
);

* output results
FILE sdg0_eff_res / gams_output_files\sdg0_eff_res.csv /
PUT sdg0_eff_res;

sdg0_eff_res.pc = 6;
sdg0_eff_res.pw = 32767;
sdg0_eff_res.nd = 10;

put '', 'eff',loop(i,put i.tl); loop(o, put o.tl); loop(o_u, put o_u.tl); loop(c, put c.tl);
loop(c,
    put /, c.tl, put eff_save(c), loop(i,put si_save(c,i)); loop(o,put so_save(c,o)); loop(o_u,put so_u_save(c,o_u)); loop(cc, put lambda_save(c,cc));
);