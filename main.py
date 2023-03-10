from matplotlib import test
import warnings
from collections import OrderedDict
from pylab import rcParams
import torch
import torch.nn as nn
import torchvision.transforms
import matplotlib.pyplot as plt 
import numpy as np 
import mne
from mne import io
from mne.datasets import sample
from sklearn.preprocessing import RobustScaler
warnings.filterwarnings('ignore')

torch.manual_seed(100)

# Intialize the parameters
eeg_sample_count = 240 # How many samples are we training
learning_rate = 1e-3 # How hard the network will correct its mistakes while (in other words, it's how fast the ntetwork tends to change its weights)
eeg_sample_length = 226 # Number of eeg data points per sample 
number_of_classes = 1 # We want to answer the "is this a P300?" question which in other words is the number of output classes
hidden1 = 500 # Number of neurons in our first hidden layer 
hidden2 = 1000 # Number of neurons in our second hidden layer
hidden3 = 100 # Number of neurons in our third hidden layer 
output = 10 # Number of neurons in our output layer

## Define the network 
tutorial_model = nn.Sequential()

# Input Layer (Size 226 -> 500)
tutorial_model.add_module('Input Linear', nn.Linear(eeg_sample_length, hidden1))
tutorial_model.add_module('Input Activation', nn.CELU())

# Hidden Layer (Size 500 -> 1000)
tutorial_model.add_module('Hidden Linear', nn.Linear(hidden1, hidden2))
tutorial_model.add_module('Hidden Activation', nn.ReLU())

# Hidden Layer (Size 1000 -> 100)
tutorial_model.add_module('Hidden Linear2', nn.Linear(hidden2, hidden3))
tutorial_model.add_module('Hidden Activation2', nn.ReLU())

# Hidden Layer (Size 100 -> 10)
tutorial_model.add_module('Hidden Linear3', nn.Linear(hidden3, output))
tutorial_model.add_module('Hidden Activation3', nn.ReLU())

# Output Layer (Size 10 -> 1)
tutorial_model.add_module('Output Linear', nn.Linear(output, number_of_classes))
tutorial_model.add_module('Output Activation', nn.Sigmoid())

# Define a loss function 
loss_function = torch.nn.MSELoss()

# Define a training procedure 
def train_network(train_data, actual_class, iterations):

  # Keep track of loss at every training iteration
  loss_data = []

  # Begin training ofr a certain amount of iterations 
  for i in range(iterations):

    # Begin with classification
    classifcation = tutorial_model(train_data)

    # Find out how wrong our network was
    loss = loss_function(classifcation, actual_class)
    loss_data.append(loss)

    # Zero out the optimizer gradients every iteration
    optimizer.zero_grad()

    # Teach the network how to do better next time
    loss.backward()
    optimizer.step()

# Save the network's default state so we can retrain from the default weights
torch.save(tutorial_model, "null")

## Create sample data using the parameters
sample_positives = [None, None] # Element [0] is the sample, Element [1] is the class
sample_positives[0] = torch.rand(int(eeg_sample_count / 2), eeg_sample_length) * 0.50 + 0.25
sample_positives[1] = torch.ones([int(eeg_sample_count / 2), 1], dtype=torch.float32)

sample_negatives = [None, None] # Element [0] is the sample, Element [1] is the class
sample_negatives_low = torch.rand(int(eeg_sample_count / 4), eeg_sample_length) * 0.25
sample_negatives_high = torch.rand(int(eeg_sample_count / 4), eeg_sample_length) * 0.25
sample_negatives[0] = torch.cat([sample_negatives_low, sample_negatives_high], dim=0)
sample_negatives[1] = torch.zeros([int(eeg_sample_count / 2), 1], dtype=torch.float32)

samples = [None, None] # Combine the two
samples[0] = torch.cat([sample_positives[0], sample_negatives[0]], dim = 0)
samples[1] = torch.cat([sample_positives[1], sample_negatives[1]], dim = 0)

## Create test data that isn't trained on
test_positives = torch.rand(10, eeg_sample_length) * 0.50 + 0.25 # Test 10 good samples
test_negatives_low = torch.rand(5, eeg_sample_length) * 0.25 # Test 5 bad low samples
test_negatives_high = torch.rand(5, eeg_sample_length) * 0.25 + 0.75 # Test 5 bad high samples
test_negatives = torch.cat([test_negatives_low, test_negatives_high], dim=0)

print("We have created a sample dataset with " + str(samples[0].shape[0]) + " samples")
print("Half of those are positive samples with a score of 100%")
print("Half of those are negative samples with a score of 0%")
print("We have also created two sets of 10 test samples to check the validity of the network")

rcParams['figure.figsize'] = 15, 5

plt.title("Sample Data Set")
plt.legend()
plt.plot(list(range(0, eeg_sample_length)), sample_positives[0][0], color = "#bbbbbb", label = "One Sample")
plt.plot(list(range(0, eeg_sample_length)), sample_positives[0].mean(dim = 0), color = "g", label = "Mean Positive")
plt.plot(list(range(0, eeg_sample_length)), sample_negatives_high[0], color = "#bbbbbb")
plt.plot(list(range(0, eeg_sample_length)), sample_negatives_high.mean(dim = 0), color = "r", label = "Mean Negative")
plt.plot(list(range(0, eeg_sample_length)), sample_negatives_low[0], color = "#bbbbbb")
plt.plot(list(range(0, eeg_sample_length)), sample_negatives_low.mean(dim = 0), color = "r")
plt.plot(list(range(0, eeg_sample_length)), [0.75] * eeg_sample_length, color = "k")
plt.plot(list(range(0, eeg_sample_length)), [0.25] * eeg_sample_length, color = "k")
plt.show()

# Classify our positive test dataset
predicted_positives = tutorial_model(test_positives).data.tolist()

# Print the results
for index, value in enumerate(predicted_positives):
  print("Positive Test {1} Value scored {0:.2f}%".format(value[0] * 100, index + 1))

print()

# Classify the negative test dataset
predicted_negatives = tutorial_model(test_negatives).data.tolist()

# Print the Results
for index, value in enumerate(predicted_negatives):
  print("Negative Test {1} Value scored: {0:.2f}%".format(value [0] * 100, index + 1))

print()

print("Below is a scatter plot of some of the samples")
print("Notice the distinct areas of red and green dots. If the input of this \n" +
"network was a simple x and y coordinate, the square band in the center would \n" +
"represent the \"solution space\" of our network. However, an actual EEG signal \n" +
"sample is an array of several points and can cross the boundary at any time.")
print("Plotted is one positive sample in green and two negative samples in red")

rcParams['figure.figsize'] = 10, 5
plt.scatter(list(range(0, eeg_sample_length)), test_positives[3], color = "#00aa00")
plt.plot(list(range(0, eeg_sample_length)), test_positives[3], color = "#bbbbbb")
plt.scatter(list(range(0, eeg_sample_length)), test_negatives[0], color = "#aa0000")
plt.plot(list(range(0, eeg_sample_length)), test_negatives[0], color = "#bbbbbb")
plt.scatter(list(range(0, eeg_sample_length)), test_negatives[9], color = "#aa0000")
plt.plot(list(range(0, eeg_sample_length)), test_negatives[9], color = "#bbbbbb")
plt.ylim([0 , 1])
plt.show()

## Retrieve Data from the MNE EED Dataset 
data_path = sample.data_path()
# In order to obtain this database using python, we need to set the path ot the specidic dataset we are going to use. 
# In this case it is the sample audiovisual database, where the brainwaves have been filtered from 0 to 40 Hz
# The data we obtain is raw
# This means that it is simply a collection of streamed brain signal samples from many EEG channels, as opposed to signals slices or focused to an event of interest
raw_fname = (data_path / "MEG" /"sample"/"sample_audvis_filt-0-40_raw.fif")
event_fname = (data_path / "MEG" /"sample"/"sample_audvis_filt-0-40_raw-eve.fif")

# Obtain a reference to the database and preload into RAM
raw_data = mne.io.read_raw_fif(raw_fname, preload=True)


# EEGs work by detecting the voltage between two points. The second reference
# point is set to be the average of all voltages using the following function.
# It is also possible to set the reference voltage to a different number.
raw_data.set_eeg_reference()

# Here we load the database and save it in a variable called raw_data. The pick function allows us to choose the sources of interest.
# For this tutorial we are picking the data from the EEG electrodes. EOG is also included as those are captured using the same electrodes.
# This dataset also includes the data from MEG (magnetoencephalography). However, MEG is still very far from being an accessible technology, due to the device being the size of a room. It also requires superconductors to function, similar to fMRI.

# Define what data we want from the dataset
raw_data = raw_data.pick(picks=["eeg", "eog"])
picks_eeg_only = mne.pick_types(raw_data.info, eeg=True, eog=True, meg=False, exclude='bads')

# The raw EEG file comes with events that allow us to know when something happened during the EEG recording.
# For example, events with id 5 correspond to when participants were presented with smiley faces, while events 1 through 4 corresponds to trials were participants were presented with a checkerboard either on the left side or the right side of the screen and with a tone presented to either the left ear or the right ear.
# We know that the trials were participants were presented with a smiley (events with id 5) will elicit a P300.
# we will start by slicing (or epoching) the data 0.5 seconds before the image was presented (to have a baseline) and 1 second after the image was presented. We can change this to values closer to 0.3 seconds, which would crop exactly to where the P300 is.

events = mne.read_events(event_fname)
event_id = 5
tmin = -0.5
tmax = 1
epochs = mne.Epochs(raw_data, events, event_id, tmin, tmax, proj=True,
                    picks=picks_eeg_only, baseline=(None, 0), preload=True,
                    reject=dict(eeg=100e-6, eog=150e-6), verbose = False)
print(epochs)

# This is the channel used to monitor the P300 response
channel = "EEG 058"

# Display a graph of the sensor position we're using
sensor_position_figure = epochs.plot_sensors(show_names=[channel])


# Below is a heat graph representing the 12 P300 events found within the dataset. If you look closely around the 0.3sec -> 0.4sec mark, you can see there is a noticeable deflection in the signal.
# That is the P300 component, and the difficulty of detecting it is immediately clear, even with the line graph below the heat graph being the average of the 12 samples.
epochs.plot_image(picks=channel)

# Gather all of the other miscellaneous events contianed within the dataset
event_id=[1,2,3,4]
epochsNoP300 = mne.Epochs(raw_data, events, event_id, tmin, tmax, proj=True, picks=picks_eeg_only, baseline=(None, 0), preload=True,
                    reject=dict(eeg=100e-6, eog=150e-6), verbose = False)
print(epochsNoP300)

mne.viz.plot_compare_evokeds({'P300': epochs.average(picks=channel), 'Other': epochsNoP300[0:12].average(picks=channel)})


eeg_data_scaler = RobustScaler()

# We have 12 P300 samples
p300s = np.squeeze(epochs.get_data(picks=channel))

# We have 208 non-p300 samples
others = np.squeeze(epochsNoP300.get_data(picks=channel))

# Scale the p300 data using the RobustScaler
p300s = p300s.transpose()
p300s = eeg_data_scaler.fit_transform(p300s)
p300s = p300s.transpose()

# Scale the non-p300 data using the RobustScaler
others = others.transpose()
others = eeg_data_scaler.fit_transform(others)
others = others.transpose()

## Prepare the train and test tensors
# Specify Positive P300 train and test samples
p300s_train = p300s[0:9]
p300s_test = p300s[9:12]
p300s_test = torch.tensor(p300s_test).float()

# Specify Negative P300 train and test samples
others_train = others[30:39]
others_test = others[39:42]
others_test = torch.tensor(others_test).float()

# Combine everything into their final structures
training_data = torch.tensor(np.concatenate((p300s_train, others_train), axis = 0)).float()
positive_testing_data = torch.tensor(p300s_test).float()
negative_testing_data = torch.tensor(others_test).float()

# Print the size of each of our data structures
print("training data count: " + str(training_data.shape[0]))
print("positive testing data count: " + str(positive_testing_data.shape[0]))
print("negative testing data count: " + str(negative_testing_data.shape[0]))

# Generate the training labels
labels = torch.tensor(np.zeros((training_data.shape[0], 1))).float()
labels[0:10] = 1.0
print("training labels count: " + str(labels.shape[0]))


# Make sure we're starting from untrained every time
tutorial_model = torch.load("null")

## Define a learning function, needs to be reintialized every load
optimizer = torch.optim.Adam(tutorial_model.parameters(), lr = learning_rate)

## Use our training procedure with the sample data
print("Below is the loss graph for dataset training session")
train_network(training_data, labels, iterations = 50)



# Classify our positive test dataset and print the results
classification_1 = tutorial_model(positive_testing_data)
for index, value in enumerate(classification_1.data.tolist()):
  print("P300 Positive Classification {1}: {0:.2f}%".format(value[0] * 100, index + 1))

print()

# Classify our negative test dataset and print the results 
classification_2 = tutorial_model(negative_testing_data)
for index, value in enumerate(classification_2.data.tolist()):
    print("P300 Negaive Classification {1}: {0:.2f}%".format(value[0] * 100, index + 1))

rcParams['figure.figsize'] = 15, 5

plt.plot(list(range(0, eeg_sample_length)), positive_testing_data[0], color = "g")
plt.plot(list(range(0, eeg_sample_length)), positive_testing_data[1], color = "g")
plt.plot(list(range(0, eeg_sample_length)), positive_testing_data[2], color = "g")
plt.show()
plt.plot(list(range(0, eeg_sample_length)), negative_testing_data[0], color = "black")
plt.plot(list(range(0, eeg_sample_length)), negative_testing_data[1], color = "r")
plt.plot(list(range(0, eeg_sample_length)), negative_testing_data[2], color = "r")
plt.show()