sets
c(*)	countries
i(*)	inputs
o(*)	outputs
o_u(*)  undesired outputs;

$offlisting
$include data_input_to_gams/sets_sdg1.inc

table input(c,i) 'inputs'
$ondelim
$offdigit
$include data_input_to_gams/inputs_sdg1.csv
$offdelim
;

table output(c,o) 'outputs'
$ondelim
$offdigit
$include data_input_to_gams/outputs_sdg1.csv
$offdelim
;

table output_u(c,o_u) 'undesired outputs'
$ondelim
$offdigit
$include data_input_to_gams/undes_outputs_sdg1.csv
$offdelim
;


display c, i, o, o_u, input, output, output_u;