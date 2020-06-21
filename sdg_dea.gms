sets
c(*)	countries
i(*)	inputs
o(*)	outputs
cs(c)	selected country;
alias(c,cc);

parameters
input(c,i)
output(c,o);

$onecho > taskin.txt
set=c rng=sdg0!a2:a185 Rdim=1
set=i rng=sdg0!b1:ez1 Cdim=1
set=o rng=sdg0!b187:ez187 Cdim=1

par=input rng=sdg0!a1:ez185 Rdim=1 Cdim=1
par=output rng=sdg0!a187:ez371 Rdim=1 Cdim=1
$offecho

$call gdxxrw.exe sdg_gms_input.xlsx @taskin.txt
$gdxin sdg_gms_input.gdx
$load c i o input output
$gdxin

parameters
eff_save(cc)
eff_out(c)
epsilon;
epsilon = 1e-6;

variables
eff_primal
u_sel
u(o)
v(i)
t

obj_dual
eff_dual;

positive variables
slack_i(i)
slack_o(o)
lambda(c);

equations
of_primal
sumone_primal
const_primal
of_primal_oo
sumone_primal_oo
const_primal_oo
of_dual
const_in_dual
const_out_dual
sumone_dual
of_dual_oo
const_in_dual_oo
const_out_dual_oo
sumone_dual_oo
of_sbm
inputs_sbm
outputs_sbm
vrs_sbm

of_sbm_no
lin_sbm_no
inputs_sbm_no
outputs_sbm_no
vrs_sbm_no
;

* primal model (io)
of_primal(cs).. 	        eff_primal =e= sum(o,u(o)*output(cs,o)) + u_sel;
sumone_primal(cs)..	        sum(i, v(i)*input(cs,i)) =e= 1;
const_primal(c)..	        sum(o, u(o)*output(c,o)) + u_sel - sum(i, v(i)*input(c,i)) =l= 0;

* primal model (oo)
of_primal_oo(cs).. 	        eff_primal =e= sum(i,v(i)*input(cs,i)) - u_sel;
sumone_primal_oo(cs)..	    sum(o, u(o)*output(cs,o)) =e= 1;
const_primal_oo(c)..	    -sum(o, u(o)*output(c,o)) - u_sel + sum(i, v(i)*input(c,i)) =g= 0;

*dual model
of_dual(cs).. 		        obj_dual =e= eff_dual - epsilon*(sum(i,slack_i(i)) + sum(o,slack_o(o)));
sumone_dual..		        sum(c, lambda(c)) =e= 1;
const_in_dual(cs,i)..	    sum(c, lambda(c)*input(c,i)) + slack_i(i) =e= eff_dual*input(cs,i);
const_out_dual(cs,o)..	    sum(c, lambda(c)*output(c,o)) - slack_o(o) =e= output(cs,o);

*dual model (oo)
of_dual_oo(cs).. 		    obj_dual =e= eff_dual + epsilon*(sum(i,slack_i(i)) + sum(o,slack_o(o)));
sumone_dual_oo..		    sum(c, lambda(c)) =e= 1;
const_out_dual_oo(cs,o)..	sum(c, lambda(c)*output(c,o)) - slack_o(o) =e= eff_dual*output(cs,o);
const_in_dual_oo(cs,i)..	sum(c, lambda(c)*input(c,i)) + slack_i(i) =e= input(cs,i);

*sbm model (io)
of_sbm(cs)..                eff_primal =e= 1-(1/card(i))*sum(i, slack_i(i)/input(cs,i));
inputs_sbm(cs,i)..          input(cs,i) =e= sum(c, input(c,i)*lambda(c)) + slack_i(i); 
outputs_sbm(cs,o)..         output(cs,o) =e= sum(c, output(c,o)*lambda(c)) - slack_o(o);
vrs_sbm..                   sum(c,lambda(c)) =e= 1;

*sbm model (no)
of_sbm_no(cs)..             eff_primal =e= t-(1/card(i))*sum(i, slack_i(i)/input(cs,i));
lin_sbm_no(cs)..            1 =e= t+(1/card(o))*sum(o, slack_o(o)/output(cs,o));
inputs_sbm_no(cs,i)..       t*input(cs,i) =e= sum(c, input(c,i)*lambda(c)) + slack_i(i);
outputs_sbm_no(cs,o)..      t*output(cs,o) =e= sum(c, output(c,o)*lambda(c)) - slack_o(o);
vrs_sbm_no..                sum(c,lambda(c)) =e= t;

model primal    /of_primal, sumone_primal, const_primal/
model primal_oo /of_primal_oo, sumone_primal_oo, const_primal_oo/
model dual      /of_dual, sumone_dual, const_in_dual, const_out_dual/
model dual_oo   /of_dual_oo, sumone_dual_oo, const_out_dual_oo, const_in_dual_oo/
model sbm 	/of_sbm, inputs_sbm, outputs_sbm, vrs_sbm/
model sbm_no 	/of_sbm_no, lin_sbm_no, inputs_sbm_no, outputs_sbm_no, vrs_sbm_no/

option optcr = 0, reslim = 10800;

u.lo(o) = epsilon;
v.lo(i) = epsilon;
t.lo = epsilon;

* adjust base point where needed according to Tone (2020)
parameters
smin_i,smin_o;
smin_i = smin((c,i),input(c,i));
smin_o = smin((c,o),output(c,o));

if( (smin_i le 0),
    input(c,i) = input(c,i) - smin_i + epsilon;
);
if( (smin_o le 0),
    output(c,o) = output(c,o) - smin_o + epsilon;
);


* solve loop for each dmu
loop(cc,
    cs(cc) = yes;
    solve sbm_no using LP minimising eff_primal;
    eff_save(cc) = eff_primal.l;
    cs(cc) = no;
);

* output results
FILE sdg0_eff_res / output_files\sdg0_eff_res.csv /

PUT sdg0_eff_res;

sdg0_eff_res.pc = 6;
sdg0_eff_res.pw = 1000;
sdg0_eff_res.nd = 10;

put '', 'sdg0';
loop(c,
    put /, c.tl, put eff_save(c);
);










