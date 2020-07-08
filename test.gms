sets
c(*)	countries
i(*)	inputs
o(*)	outputs
o_u(*)  undesired outputs;

$include data_input_to_gams/test.inc

table input(c,i) 'inputs'
$ondelim
$offdigit
$include data_input_to_gams/test_inputs.csv
$offdelim
;

table output(c,o) 'outputs'
$ondelim
$offdigit
$include data_input_to_gams/test_outputs.csv
$offdelim
;

table output_u(c,o_u) 'undesired outputs'
$ondelim
$offdigit
$include data_input_to_gams/test_undes_outputs.csv
$offdelim
;

display c, i, o, o_u, input, output, output_u;