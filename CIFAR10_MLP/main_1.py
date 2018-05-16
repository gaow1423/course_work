import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torchvision import datasets, transforms
from torch.autograd import Variable
import numpy as np
import matplotlib
import math
import matplotlib.pyplot as plt

cuda = torch.cuda.is_available()
print('Using PyTorch version:', torch.__version__, 'CUDA:', cuda)
##data preparation
batch_size = 40
kwargs = {'num_workers': 2, 'pin_memory': True} if cuda else {}
trainset = datasets.CIFAR10(root='./data', train=True, download=True, transform=transforms.Compose([transforms.ToTensor()]))
train_loader = torch.utils.data.DataLoader(trainset, batch_size, shuffle=True, **kwargs)

validationset = datasets.CIFAR10(root='./data', train=False, download=True, transform=transforms.Compose([transforms.ToTensor()]))
validation_loader = torch.utils.data.DataLoader(validationset, batch_size, shuffle=False, **kwargs)

classes = ('plane', 'car', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck')


class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.fc1 = nn.Linear(3*32*32, 100)
        self.fc1_drop = nn.Dropout(0.2)
        self.fc2 = nn.Linear(100,10)

    def forward(self, x):
        x = x.view(-1, 3*32*32)
        x = F.sigmoid(self.fc1(x))
        x = self.fc1_drop(x)
        return F.log_softmax(self.fc2(x), 1)

#model = Net()
#if cuda:
#    model.cuda()

#learningrate = [0.1, 0.01, 0.001, 0.0001]
#for k in learningrate:
#    optimizer = optim.SGD(model.parameters(), lr = k, momentum = 0.5)
    #print(model)

def train(epoch, k, model, log_interval = 100):
#    print (k)
    model.train()
    for batch_idx, (data, target) in enumerate(train_loader):
        if (batch_idx <= 999):
            if cuda:
                data, target = data.cuda(), target.cuda()
            data, target = Variable(data), Variable(target)
            optimizer = optim.SGD(model.parameters(), lr = k, momentum = 0.5)
            optimizer.zero_grad()
            output = model(data)
            loss = F.nll_loss(output, target)
            loss.backward()
            optimizer.step()
#                if batch_idx % log_interval == 0:
#                    print('Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}'.format(epoch, (batch_idx) * len(data), len(train_loader.dataset), 100. * batch_idx / len(train_loader), loss.data[0]))

def validate(loss_vector, accuracy_vector, epochs, model):
    model.eval()
    val_loss, correct = 0, 0
    for batch_idx, (data, target) in enumerate(train_loader):
        if (batch_idx > 999):
            if cuda:
                data, target = data.cuda(), target.cuda()
            data, target = Variable(data), Variable(target)
            output = model(data)
            val_loss += F.nll_loss(output, target).data[0]
            pred = output.data.max(1)[1] # get the index of the max log-probability
            correct += pred.eq(target.data).cpu().sum()
    val_loss /= (10000/batch_size)
    loss_vector.append(val_loss)
    accuracy = 100. * correct / len(validation_loader.dataset)
    accuracy_vector.append(accuracy)
    print('\nEpoch {}: Validation set: Average loss: {:.4f}, Accuracy: {}/{} ({:.0f}%)\n'.format(epochs, val_loss, correct, len(validation_loader.dataset), accuracy))

def test(loss_vector, accuracy_vector, epochs, model):
    model.eval()
    val_loss, correct = 0, 0
    for (data, target) in validation_loader:
        if cuda:
            data, target = data.cuda(), target.cuda()
        data, target = Variable(data), Variable(target)
        output = model(data)
        val_loss += F.nll_loss(output, target).data[0]
        pred = output.data.max(1)[1] # get the index of the max log-probability
        correct += pred.eq(target.data).cpu().sum()
    val_loss /= len(validation_loader)
    loss_vector.append(val_loss)
    accuracy = 100. * correct / len(validation_loader.dataset)
    accuracy_vector.append(accuracy)
    print('\nEpoch {}: Test set: Average loss: {:.4f}, Accuracy: {}/{} ({:.0f}%)\n'.format(epochs, val_loss, correct, len(validation_loader.dataset), accuracy))


def main():
#    learningrate = [0.1, 0.01, 0.001, 0.0001]
#    for k in learningrate:
    model = Net()
    if cuda:
        model.cuda()
    epochs = 150
    lossv, accv = [], []
    for epochs in range(1, epochs + 1):
        train(epochs, 0.1, model)
#        validate(lossv, accv, epochs, model)
        test(lossv, accv, epochs, model)
    l = range(1, epochs + 1)
    plt.plot(l, accv, label = "learning rate = 0.1")

    plt.title('Performance with various learning rate and Sigmoid function')
    plt.xlabel('x-axis: the Number of Epochs')
    plt.ylabel('y-axis: Accuracy of Test set (%)')
    plt.legend()
    plt.show()

if __name__ == '__main__':
    main()
