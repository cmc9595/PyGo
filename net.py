import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset
from torch import optim
from tqdm.auto import tqdm
from torchsummary import summary

class GoValueDataset(Dataset):
    def __init__(self):
        dat = np.load("/gdrive/MyDrive/Colab Notebooks/PythonGo/jgdb/1000.npz")
        self.X = dat['arr_0']
        self.Y = dat['arr_1']
        print("loaded", self.X.shape, self.Y.shape)
    def __len__(self):
        return self.X.shape[0]
    def __getitem__(self, idx):
        return (self.X[idx], self.Y[idx])

class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()

        self.layer1 = nn.Conv2d(4, 32, kernel_size=5, stride=1, padding=2)  # stride로 크기조절, no need MaxPool2d (i think)
        self.layer2 = nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1)
        self.layer3 = nn.Conv2d(64, 128, kernel_size=1, stride=1, padding=0)

        self.last = nn.Linear(128*19*19, 361)
        
    def forward(self, x):
        x = F.relu(self.layer1(x))
        x = F.relu(self.layer2(x))
        x = F.relu(self.layer3(x))
        
        x = x.view(-1, 128*19*19)
        x = self.last(x)

        return x

if __name__ == "__main__":
    device = "cuda"
    go_dataset = GoValueDataset()
    
    train_loader = torch.utils.data.DataLoader(go_dataset, batch_size=256, shuffle=True)
    model = Net().to(device)

    #****summary****
    summary(model, (4, 19, 19))

    optimizer = optim.Adam(model.parameters())
    floss = nn.MSELoss()
    #floss = torch.nn.CrossEntropyLoss().to(device)

    if device == "cuda":
        model.cuda()
   
    model.train()
    for epoch in tqdm(range(5)):
        all_loss = 0
        num_loss = 0
        for batch_idx, (data, target) in enumerate(tqdm(train_loader)):
            #target = target.unsqueeze(-1)
            data, target = data.to(device), target.to(device)
            data = data.float()
            target = target.float()
            
            #target = target.squeeze()

            optimizer.zero_grad()
            output = model(data)
            #print("data :", data.shape)
            #print("target :", target.shape) 
            #print("output:", output.shape)
            loss = floss(output, target)
            loss.backward()
            optimizer.step()

            all_loss += loss.item()
            num_loss += 1
        
        print("%3d: %f" % (epoch, all_loss/num_loss))
        torch.save(model.state_dict(), "/gdrive/My Drive/Colab Notebooks/PythonGo/jgdb/tmp.pth")
        #SL2 -> Layer4, epoch=100, batch=256, time=30min
        #SL3 -> Layer10 version!

            
    
