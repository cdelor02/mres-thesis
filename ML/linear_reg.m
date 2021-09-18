%% MATLAB multivariate linear regression


%%

filename = '../data/actuator_experiments_fixed_a0-2021-09-10/actuator_10_iterations_experiments_6_data_for_matlab_2.csv';

data = table2array(readtable(filename));


%%

s = size(data);
data = data(:, 2:end); % remove linecount which was included from the DataFrame

X = [ones(s(1), 1), data(:, 1:3)];

Y = data(:, 4:6);

%%

[beta, Sigma, E, CovB, logL] = mvregress(X, Y);


%% Plot the fitted model

B = beta;
xx = 0:1:length(data)-1;%linspace(0, length(data))';
fits = [ones(size(xx)), xx] .* B;

figure
h = plot(x,Y,'x', xx,fits,'-');
for i = 1:d
    set(h(d+i),'color',get(h(i),'color'))
end

% regions = flu.Properties.VarNames(2:end-1);
% legend(regions,'Location','NorthWest')




%%

load('flu');
Y = double(flu(:,2:end-1));
[n,d] = size(Y);
x = flu.WtdILI;
X = [ones(size(x)),x];
[beta,Sigma,E,CovB,logL] = mvregress(X,Y);

%%
B = beta;
xx = linspace(.5,3.5)';
fits = [ones(size(xx)),xx]*B;

figure
h = plot(x,Y,'x', xx,fits,'-');
for i = 1:d
    set(h(d+i),'color',get(h(i),'color'))
end

regions = flu.Properties.VarNames(2:end-1);
legend(regions,'Location','NorthWest')
