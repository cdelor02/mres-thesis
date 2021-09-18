% LSTM

%https://uk.mathworks.com/help/deeplearning/ug/time-series-forecasting-using-deep-learning.html

%% Import data

filename = '../data/actuator_experiments_fixed_a0-2021-09-10/actuator_10_iterations_experiments_6_data_for_matlab_2.csv';

data = readtable(filename);
dataarray = table2array(data);


%% Standardise data

numTimeStepsTrain = floor(0.9 * height(dataarray));

dataTrain = dataarray(1:numTimeStepsTrain+1, 2:4);
dataTest  = dataarray(numTimeStepsTrain+1:end, 2:4);

%% Create inputs and outputs

% for i = 1:3
%     mu(i)  = mean(dataTrain(:,i));    
%     sig(i) = std(dataTrain(:,i));
%     datatrainStandardised(:,i) = (dataTrain(:,i) - mu(i)) / sig(i);
% end

mu(1) = mean(dataTrain(:, 1));
mu(2) = mean(dataTrain(:, 2));
mu(3) = mean(dataTrain(:, 3));

sig(1) = std(dataTrain(:, 1));%.a0);
sig(2) = std(dataTrain(:, 2));
sig(3) = std(dataTrain(:, 3));

dataTrainStandardised(:, 1) = (dataTrain(:, 1) - mu(1)) / sig(1);
dataTrainStandardised(:, 2) = (dataTrain(:, 2) - mu(2)) / sig(2);
dataTrainStandardised(:, 3) = (dataTrain(:, 3) - mu(3)) / sig(3);


%% Prepare X and y

XTrain(:, 1) = dataTrainStandardised(1:end-1, 1);%1:end-1, 1);
XTrain(:, 2) = dataTrainStandardised(1:end-1, 2);%1:end-1, 2);
XTrain(:, 3) = dataTrainStandardised(1:end-1, 3);%1:end-1, 3);

YTrain(:, 1) = dataTrainStandardised(2:end, 1);
YTrain(:, 2) = dataTrainStandardised(2:end, 2);
YTrain(:, 3) = dataTrainStandardised(2:end, 3);


%% Define LSTM architecture

numFeatures    = 3;
numResponses   = 3;
numHiddenUnits = 200;

layers = [ ...
    sequenceInputLayer(numFeatures)
    lstmLayer(numHiddenUnits)
    fullyConnectedLayer(numResponses)
    regressionLayer];

options = trainingOptions('adam', ...
    'MaxEpochs', 250, ...
    'GradientThreshold', 1, ...
    'InitialLearnRate', 0.005, ...
    'LearnRateSchedule','piecewise', ...
    'LearnRateDropPeriod', 125, ...
    'LearnRateDropFactor', 0.2, ...
    'Verbose', 0, ...
    'Plots', 'training-progress');

%% Train network

net = trainNetwork(XTrain.', YTrain.', layers, options);


%% Predict future voltages
% dataTest = table2array(dataTest);

dataTestStandardised = (dataTest - mu) / sig;
XTest = dataTestStandardised(1:end-1);

net = predictAndUpdateState(net, XTrain.');

[net, YPred(:,:)] = predictAndUpdateState(net, YTrain(end, :).');

numTimeStepsTest = numel(XTest);
for i = 2:numTimeStepsTest
    [net, YPred(:, i)] = predictAndUpdateState(net, YPred(:, i-1), 'ExecutionEnvironment', 'cpu');
end

YPred = sig * YPred + mu(1);

YTest = dataTest(2:end, 1);
rmse  = sqrt(mean((YPred - YTest).^2));

%% 
figure
plot(dataTrain(1:end-1, 1))
hold on
idx = numTimeStepsTrain:(numTimeStepsTrain+numTimeStepsTest);
plot(idx,[dataarray(numTimeStepsTrain, 5) YPred],'.-')
hold off
set(gca,'XTickLabel',linspace(0, length(dataTrain)/40, length(dataTrain)))
xlabel("Time (samples)")
ylabel("Voltage (V)")
title("EIT data predicted values")
legend(["Observed" "Predicted"])


%% Compare 

% YTestarray = YTest);

figure
subplot(2,1,1)
plot(YTest)
hold on
plot(YPred,'.-')
hold off
legend(["Test data" "Predicted data"])
ylabel("Voltage (V)")
title("Predicted")

subplot(2,1,2)
stem(YPred(1,1) - YTest(1,1))
xlabel("Month")
ylabel("Error")
title("RMSE = " + rmse(1,1))


