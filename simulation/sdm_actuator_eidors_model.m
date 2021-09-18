% EIDORS model of final EIT chamber (a simple rectangular prism with 6
% electrodes)

% MAKE SURE YOU RUN THE EIDORS STARTUP \EIDORS\eidors\startup.m
% run C:\Users\Charlie\Documents\eidors-v3.10\eidors-v3.10-ng\eidors\startup


% DONT USE CLEAR ALL

% We are using https://github.com/Jimbles/meshio2matlab to load the mesh -
% sorry for yet another download!

% run the MakeSensorMeshes.py to make the .vtu file

%% using built-in EIDORS functions
%  --> NOTE: this is a 2D simulation of the plane the electrodes are on,
%  there doesn't seem to be built-in functionality to use 3D rectangular
%  volumes

% electrodes = [];

% imdl = mk_common_model('a2sc', 8);
% 
% show_fem(imdl.fwd_model, [0,1]);

shape_str = ['solid top    = plane( 0, 0, 0; 0, 0, 1);\n' ...
             'solid bot    = plane( 0, 0,-1; 0, 0,-1);\n' ...
             'solid xmax   = plane( 4, 0, 0; 1, 0, 0);\n' ...
             'solid xmin   = plane(-4, 0, 0;-1, 0, 0);\n' ...
             'solid ymax   = plane( 0, 2, 0; 0, 2, 0);\n' ...
             'solid ymin   = plane( 0,-2, 0; 0,-2, 0);\n' ...
             'solid mainobj= top and bot and xmax and xmin and ymax and ymin;'];

elec_pos = [ -4, -2,  -0.5,   1,  1,  0;  %  e1
             -3, -2,  -0.5,   1,  1,  0;  %  e2
             -1, -2,  -0.5,   0,  1,  0;  %  e3
              1, -2,  -0.5,   0,  1,  0;  %  e4
              2, -2,  -0.5,   0,  1,  0;  %  e5
              3, -2,  -0.5,   0,  1,  0]; %  e6             

elec_shape = [0.2, 0, 0.1]; 
elec_obj   = {'xmin', 'xmin', 'ymin', 'ymin', 'ymin', 'ymin'};%'ymax', 'xmin', 'ymin'};
fmdl       = ng_mk_gen_models(shape_str, elec_pos, elec_shape, elec_obj);

show_fem(fmdl, [0,1]);

%% working version with help from James

shape_str = ['solid top     = plane(0,0,0;0,0,1);\n' ...
             'solid mainobj = top and orthobrick(-5,-0.5,-4;5,0.5,0) -maxh=0.5;\n']; %maxh is element size in brick
elec_pos = [ 4,  0,  0,   0,  0,  1;
             3,  0,  0,   0,  0,  1;
           0.5,  0,  0,   0,  0,  1;
          -0.5,  0,  0,   0,  0,  1;
            -3,  0,  0,   0,  0,  1
            -4,  0,  0,   0,  0,  1];

%  elec_pos = [ -4,  0,  0,   0,  0,  1;
%               -3,  0,  0,   0,  0,  1;
%             -0.5,  0,  0,   0,  0,  1;
%              0.5,  0,  0,   0,  0,  1;
%                3,  0,  0,   0,  0,  1   
%                4,  0,  0,   0,  0,  1]; 
           
elec_shape=[0.1,0,0.2]; %radius, 0, element size at elecs
elec_obj = 'top';
fmdl = ng_mk_gen_models(shape_str, elec_pos, elec_shape, elec_obj);
%  show_fem( fmdl );
 
%this is in meters so scale
fmdl.nodes = fmdl.nodes/1000;
show_fem(fmdl,[1 1.015])


%% Forward model settings

% set some default solver parameters we dont really ever need to change
% these for our purpose
fmdl.solve                  = @fwd_solve_1st_order;
fmdl.jacobian               = @jacobian_adjoint;
fmdl.system_mat             = @system_mat_1st_order;
fmdl.normalize_measurements = 0;

% Convert protocol file to EIDORS stim patterns

Amp = 0.005; % Current amplitude in Amps based on orangetest1

N_elec = size(elec_pos, 1);

% EIT measurements are defined in the following way:
% CS+ CS- V+ V-
% 1,2,1,6
% i.e. inject between 1 and 2, measure 1 referenced to 6 etc.

% create eidors stimulation structure for adjacent pairs as used in orange
% example, but this isnt optimal tbh
 options = {'meas_current', 'no_rotate_meas'};

 % HERE WE HAVE HARD CODED 6 ELECS BETTER TO SPECIFY THE MEASUREMENTS BY
 % PASSING ARRAY TO stim_meas_list 

% TODO
stim_list = [1, 6, 2, 5; 
             1, 3, 4, 2]; %% complete this! look at model and fix it
         
         
[stim, meas_select] = mk_stim_patterns(6, 1,'{op}', '{op}', options, 0.005);
                                    %  electrodes, 1 ring, ad==adjacent so
                                    % injecting between adjacent
                                    % electrodes; this is the worst method
                                    % to pick for us, so we need to fix
                                    % this (be clever with this!)

% **                                    
                                    
fmdl.stimulation = stim;
fmdl.meas_select = meas_select;

% get a easier to read protocol out
[prt]= stim_meas_list(stim);

%% Check FWD is ok

%some nodes are not used which is bad so take them out. Because there were
%nodes added by gmsh in the middle, the gnd is actually assigned to a
%floated node that is removed by this line, hence the warning from this
%line. the replacement it finds it ok though
fmdl = remove_unused_nodes(fmdl); % DO THIS EARLIER, BEFORE DEFINING GROUND NODE; might crash though

fprintf('Validating FWD...')
valid_fwd_model(fmdl);
fprintf('OK! :)\n');
%% Conductivity values

% conductivity - each element in mesh needs to be assigned a conductivity
% value in S/m

S = 0.4; % conductivity in S/m this is based on 0.2% saline but we need to check what could be used in reality

% in this case we are going to define a region in the mesh that has changed
% conductivity - this is just to make sure the mesh is working ok
S_pert = S * 1.05;

%% EIT Forward model

% Forward model simulates the electric fields in the chosen mesh for chosen
% electrode and stimulation pattern. This gives you all the voltages
% measurements you would get in an ideal experiment

% create img object and get "baseline" data. Setting each element to the
% conductivity S
img = mk_image(fmdl, S); %assigning every element in mesh the conductivity S
    % could also define S as a vector, and try making one corner have a
    % different conductivity, and reconstruct an image of THAT change, and
    % see the difference between uniform conductivity vs inhomogeneous
        % good sanity check!

% we want all the outputs because we want to see the current flow
img.fwd_solve.get_all_meas = 1;
% solve the fwd model for this img to get baseline voltages
v_baseline = fwd_solve(img);

%% Visualise the current injection

% we have 6 current injections, we can chose which one to view
Inj_number = 2; % between 

% convert voltage field into current field and take magnitude
curvolt     = v_baseline.volt(:, Inj_number);
elemcur     = calc_elem_current(img, curvolt);
elemcur_mag = vecnorm(elemcur, 2, 2);
current_img = mk_image(fmdl, elemcur_mag);

figure;
hold on
show_fem(current_img, [1, 1]) % magnitude current
show_current(img, v_baseline.volt(:, Inj_number)); % current vectors
daspect([1, 1, 1])
hold off
title(sprintf('Current field for stim %d', Inj_number));
% we can see that the current is localised close to the electrodes

% This is not easy to see! instead lets look at it in paraview instead

meshio.write(['final_eit_chamber_single_currentmag.vtu'], fmdl.nodes, fmdl.elems, {elemcur_mag}, {'currentmagnitude'}, {curvolt}, {'voltagefield'});

%% visualise sensitivity

% % each row in the jacobian shows the sensitivity of the measurement to changes in
% % conductivity in each element. i.e. how much does the voltage obtained change
% % if the conductivity in a particular element changes
% % These are all then combined to create a total sensitivity map.

% get the jacobian for this model
J = calc_jacobian(img);

% scale for element size
J = J./(get_elem_volume(img.fwd_model)');

% Take sensitivity of all lines  
Sens = (sum(J(:, :).^2, 1).^0.5); % change to J(n,:) to see just single measurement sensitivity

% sometimes its necessary to take dB to make it easier to visualise, the range of values are huge!
% Sens=log10(abs(Sens)); % its better if you let paraview handle it as you get better axis labels

meshio.write(['final_eit_chamber_moremesh_J.vtu'], fmdl.nodes, fmdl.elems, {Sens}, {'J'});


%% Plot the voltages for this image


figure; 
plot(v_baseline.meas);
hold on;
title('Voltages of final EIT chamber design')
set(findall(gcf, '-property', 'FontSize'), 'FontSize', 15);
set(findall(gcf, '-property', 'MarkerSize'), 'MarkerSize', 15);

%% plot the voltages together
% load('all_meas.mat')
% 
% figure; 
% plot(all_meas(1, :), 'r', 'LineWidth', 2.0); 
% hold on; 
% plot(all_meas(2, :), 'g--', 'LineWidth', 2.0); 
% plot(all_meas(3, :), 'b--', 'LineWidth', 2.0);
% legend('Straight', '1 bend', '2 bend');
% title('Voltages overlaid of first bend pneunet finger', 'FontSize', 20);