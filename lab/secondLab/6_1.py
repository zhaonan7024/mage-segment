import torch
import numpy as np
import torchvision
import torchvision.transforms as transforms
import matplotlib.pyplot as plt

#在多分类任务实验中手动实现实现𝑳_𝟐正则化
#多分类数据集问题
train_dataset = torchvision.datasets.MNIST(root='~/Datasets/MNIST',train=True,download=True,transform=transforms.ToTensor())
test_dataset = torchvision.datasets.MNIST(root='~/Datasets/MNIST',train=False,transform=transforms.ToTensor())

#批量读取数据
batch_size = 64
train_iter = torch.utils.data.DataLoader(train_dataset,batch_size = batch_size,shuffle = True,num_workers = 0)
test_iter = torch.utils.data.DataLoader(test_dataset,batch_size = batch_size,shuffle = True,num_workers = 0)


#模型参数定义和初始化
num_inputs,num_outputs,num_hiddens1 = 784,10,256
W1 = torch.tensor(np.random.normal(0,0.01,(num_hiddens1,num_inputs)),dtype=torch.float)
b1 = torch.zeros(num_hiddens1,dtype=torch.float)
W2 = torch.tensor(np.random.normal(0,0.01,(num_outputs,num_hiddens1)),dtype=torch.float)
b2 = torch.zeros(num_outputs,dtype=torch.float)
params = [W1,b1,W2,b2]
for param in params:
    param.requires_grad_(requires_grad=True)

#定义L2范数惩罚项
def l2_penalty(w):
    return (w**2).sum()/2

#定义激活函数 ReLU
def relu(X):
    return torch.max(input = X,other=torch.tensor(0.0))

#定义交叉损失函数
loss = torch.nn.CrossEntropyLoss()
#定义模型

def net(X):
    X = X.view((-1,num_inputs))
    H1 = (torch.matmul(X,W1.t())+b1).relu()
    return torch.matmul(H1,W2.t())+b2

#定义随机梯度下降函数
def SGD(params,lr):
    for param in params:
        param.data -=lr*param.grad


#计算模型在某个数据集上的准确率
def evaluate_accuracy(data_iter,net,loss):
    acc_sum,n = 0.0,0
    test_l_sum = 0.0
    for X,y in data_iter:
        acc_sum+=(net(X).argmax(dim=1)==y).float().sum().item()
        n+=y.shape[0]
        l = loss(net(X), y).sum()
        test_l_sum += l.item()
    return acc_sum/n,test_l_sum/n

#定义模型训练函数
def train(net,train_iter,test_iter,loss,num_epochs,batch_size,lambd,params=None,lr = None,optimizer = None):
    train_loss = []
    test_loss = []
    for epoch in range(num_epochs):
        train_1_sum,train_acc_sum,n = 0.0,0.0,0
        for X, y in train_iter:
            y_hat = net(X)
            l = loss(y_hat,y) +lambd* l2_penalty(W1)+lambd* l2_penalty(W2)
            l = l.sum()
            #梯度清零
            if optimizer is not None:
                optimizer.zero_grad()
            elif params is not None and params[0].grad is not None:
                for param in params:
                    param.grad.data.zero_()
            l.backward()
            if optimizer is None:
                SGD(params,lr)
            else:
                optimizer.step()
            train_1_sum+=l.item()
            train_acc_sum+=(y_hat.argmax(dim=1)==y).sum().item()
            n+=y.shape[0]
        test_acc,test_1 = evaluate_accuracy(test_iter,net,loss)
        train_loss.append(train_1_sum / n)
        test_loss.append(test_1)
        print('epoch %d,loss %.4f,train acc %.3f,test acc %.3f' %(epoch+1,train_1_sum/n,train_acc_sum/n,test_acc))
    return train_loss, test_loss

num_epochs = 10
lr = 0.1
lambd = 0.01
train_loss,test_loss=train(net,train_iter,test_iter,loss,num_epochs,batch_size,lambd,params,lr)


#绘制loss曲线
x = np.linspace(0,len(train_loss),len(train_loss))
plt.plot(x,train_loss,label="train_loss",linewidth = 1.5)
plt.plot(x,test_loss,label = "test_loss",linewidth = 1.5)
plt.xlabel("epoch")
plt.ylabel("loss")
plt.legend()
plt.show()
