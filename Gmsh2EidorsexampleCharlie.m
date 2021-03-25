% How to get our 3D models into EIDORS and run fwd

% MAKE SURE YOU RUN THE EIDORS STARTUP \EIDORS\eidors\startup.m
% run C:\Users\Charlie\Documents\eidors-v3.10\eidors-v3.10-ng\eidors\startup


% DONT USE CLEAR ALL

% We are using https://github.com/Jimbles/meshio2matlab to load the mesh -
% sorry for yet another download!

% run the MakeSensorMeshes.py to make the .vtu file

%% load the mesh into matlab

fname = 'pneunet_approximate_test'; %'finger_two_bend_hollow';

%if you have the meshiolibrary
if exist('meshio')
    
    M=meshio.read([fname '.vtu']); % THE MESH IS IN MM
    
    save(fname,'M');
    
    % we can plot everything in this file:
    meshio.plot(M)
    
else
    
    load(fname)
    
end


% gmsh saves the lines and triangles it creates when converting step to
% tetrahedra, but we dont want those! We can just take the tetrahedral
% elements in M.cells(4)

%note the warning about points not referenced by triangulation. this means
%we have points in M.vtx which are not used by the tetrahedral mesh - we
%remove these later


%% create eidors stucture

% eidors creates the structures with all the various parameters which we
% need to recreate here:

% this is largely based on mk_fmdl_from_nodes

% create blank fwd object
MDL=eidors_obj('fwd_model', 'FingerSegmentSensor');

% specify nodes and triangulation
MDL.nodes = M.vtx./1000; % the 3d coordinates of the nodes IN METERS
MDL.elems = M.cells(4).tri; % which nodes create a tetrahedron

% specify boundary elements - eidors needs this separately
[srf, idx] = find_boundary(M.cells(4).tri);
MDL.boundary = srf;

% find ground node - as we are calculating voltage fields, we need a
% reference point to make the ground. This has nothing to do with the
% ground in the hardware. In theory this could be anywhere, but its best
% stuck somewhere away from the electrodes

gnd_pos = mean(MDL.nodes); % somewhere in the middle is fine

% find the nearest node to this point
gnd_dist = sqrt(sum((MDL.nodes - gnd_pos).^2, 2));
[~, gnd_node] = min(gnd_dist);
MDL.gnd_node = gnd_node;

%% Plot mesh to check all is ok
figure
show_fem(MDL) % this is only the SURFACE triangles, as matlab cant really cope with plotting tetra
title('EIDORS is happy with the mesh IN METERS');

%% Define electrodes

% we are going to use "point" electrodes to start with, these are on a
% single node only. eidors requires a stucture with the surface nodes for
% each electrode, and the contact impedance

% as an example, lets define two rings of electrodes at middle plane as per
% Sainas example

% elecRingZ=[0];

% radius of the inner shell hole, it's square but still
% radius_centre=0.016;

% create a ring of points
% phi_offset=0; % first one created at phi=0 but can be offset
% nElecRing = 8; % number of electrodes in each ring
% for iElec=1:nElecRing
%     phi_e = 2*pi*(iElec-1)/nElecRing  + phi_offset;
%     elec_pos_ring(iElec,:) = radius_centre * [cos(phi_e) sin(phi_e)];
% end

% create points in 3D 
% elec_pos=[];
% nRing=length(elecRingZ);
% for iRing=1:nRing
%     elec_pos=[elec_pos; elec_pos_ring repmat(elecRingZ(iRing),[nElecRing,1]) ];
% end

% elec_pos = [ 0, -0.01, 0;
%              0, -0.01, 0.01; 
%              0, -0.01, 0.02; 
%              0, 0, 0.02;
%              0, 0.01, 0.02;
%              0, 0.01, 0.01;
%              0, 0.01, 0;
%              0, 0, 0];

% manually plot each electrode around square chamber perimeter
% elec_pos = [ -0.01, 0, 0;
%              -0.01, 0, 0.01; 
%              -0.01, 0, 0.02; 
%              0, 0, 0.02;
%              0.01, 0, 0.02;
%              0.01, 0, 0.01;
%              0.01, 0, 0;
%              0, 0, 0];


% No bend
% elec_pos = [-0.060, 0, 0;
%             -0.030, 0, 0; 
%              0,     0, 0;
%             -0.060, 0.02, 0;
%             -0.030, 0.02, 0; 
%              0,     0.02, 0];
         
% No bend, hollow
% elec_pos = [-0.060, 0+0.002, 0;
%             -0.030, 0+0.002, 0; 
%              0,     0+0.002, 0;
%             -0.060, 0.02-0.002, 0;
%             -0.030, 0.02-0.002, 0; 
%              0,     0.02-0.002, 0];


% One bend, hollow
% elec_pos = [-0.060, 0, -0.025;
%             -0.030, 0, -0.007; 
%              0,     0, 0;
%             -0.060, 0.02, -0.025;
%             -0.030, 0.02, -0.007; 
%              0,     0.02, 0];

% Two bend, hollow
% elec_pos = [-0.055, 0, -0.030;
%             -0.030, 0, -0.007; 
%              0,     0, 0;
%             -0.055, 0, -0.030;
%             -0.030, 0.02, -0.007; 
%              0,     0.02, 0];
     
% Two bend, hollow, INTERIOR of finger shell
elec_pos = [-0.055, 0, -0.030;
            -0.030, 0, -0.007; 
             0,     0, 0;
            -0.055, 0.02, -0.030;
            -0.030, 0.02, -0.007; 
             0,     0.02, 0];         
       
% Pneunet test         
elec_pos = [0, 0, 0.0475;
            0, 0.02, -0.0475; 
             0,     0, 0; % save
            0, 0, -0.0475;
            0, 0.02, -0.0475; 
             0,     0.02, 0];   % save      
% uncomment this line to plot the points on top of the mesh surface before
% checking in eidors later
figure; show_fem(MDL); hold on; plot3(elec_pos(:, 1), elec_pos(:, 2), elec_pos(:, 3), '.', 'Markersize', 50); hold off

%% create electrodes structure

z_contact = 1e-3; % ohms per meter (this isnt that important in our application as the contact should be good)

% unique surface node references
srf_tri = unique(srf(:));
srf_nodes = MDL.nodes(srf_tri,:);

% loop through each electrode
for iElec = 1:size(elec_pos,1)
    
    %assign conductivity to structure
    electrodes(iElec).z_contact = z_contact;
    
    % find surface nodes within electrode radius
    edist = sqrt(sum((srf_nodes - elec_pos(iElec,:)).^2,2));
    [~,enode] = min(edist);
    
    electrodes(iElec).nodes = srf_tri(enode);
end

% add electrode structure to model struct
MDL.electrode = electrodes;

figure
show_fem(MDL)
title('Mesh with electrode locations');

%% Forward model settings

% set some default solver parameters we dont really ever need to change
% these for our purpose
MDL.solve                  = @fwd_solve_1st_order;
MDL.jacobian               = @jacobian_adjoint;
MDL.system_mat             = @system_mat_1st_order;
MDL.normalize_measurements = 0;

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
             1, 3, 2, 4]; %% complete this! look at model and fix it
         
         
[stim, meas_select] = mk_stim_patterns(6, 1,'{op}', '{op}', options, 0.005);
                                    %  electrodes, 1 ring, ad==adjacent so
                                    % injecting between adjacent
                                    % electrodes; this is the worst method
                                    % to pick for us, so we need to fix
                                    % this (be clever with this!)

% **                                    
                                    
MDL.stimulation     = stim;
MDL.meas_select     = meas_select;

% get a easier to read protocol out
[prt]= stim_meas_list(stim);

%% Check FWD is ok

%some nodes are not used which is bad so take them out. Because there were
%nodes added by gmsh in the middle, the gnd is actually assigned to a
%floated node that is removed by this line, hence the warning from this
%line. the replacement it finds it ok though
MDL = remove_unused_nodes(MDL); % DO THIS EARLIER, BEFORE DEFINING GROUND NODE; might crash though

fprintf('Validating FWD...')
valid_fwd_model(MDL);
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
img = mk_image(MDL, S); %assigning every element in mesh the conductivity S
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
Inj_number = 1;

% convert voltage field into current field and take magnitude
curvolt     = v_baseline.volt(:, Inj_number);
elemcur     = calc_elem_current(img, curvolt);
elemcur_mag = vecnorm(elemcur, 2, 2);
current_img = mk_image(MDL, elemcur_mag);

figure;
hold on
show_fem(current_img, [1, 1]) % magnitude current
show_current(img, v_baseline.volt(:, Inj_number)); % current vectors
daspect([1, 1, 1])
hold off
title(sprintf('Current field for stim %d', Inj_number));
% we can see that the current is localised close to the electrodes

% This is not easy to see! instead lets look at it in paraview instead

meshio.write([fname 'single_currentmag.vtu'], MDL.nodes, MDL.elems, {elemcur_mag}, {'currentmagnitude'}, {curvolt}, {'voltagefield'});

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

meshio.write([fname '_moremesh_J.vtu'], MDL.nodes, MDL.elems, {Sens}, {'J'});


%% Plot the voltages for this image


figure; 
plot(v_baseline.meas);
hold on;
title('Voltages of two bend finger')
set(findall(gcf, '-property', 'FontSize'), 'FontSize', 15);
set(findall(gcf, '-property', 'MarkerSize'), 'MarkerSize', 15);

%% plot the voltages together
load('all_meas.mat')

figure; 
plot(all_meas(1, :), 'r', 'LineWidth', 2.0); 
hold on; 
plot(all_meas(2, :), 'g--', 'LineWidth', 2.0); 
plot(all_meas(3, :), 'b--', 'LineWidth', 2.0);
legend('Straight', '1 bend', '2 bend');
title('Voltages overlaid', 'FontSize', 20);

