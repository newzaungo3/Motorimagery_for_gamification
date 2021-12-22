# Motorimagery_for_gamification
## Progress
### 17/11/2021
1. Convo1D with 300 epoch 1 subject

    Train Acc: 82.29

    Val Acc : 37.50

    Train loss: 0.55

    Val loss: 0.68

2. Convo2D with 300 epoch 1 subject

    Train Acc: 91.67

    Valid Acc:50

    Train loss:0.355

    Valid Acc:0.709

3. Convo2D with 300 epoch all subject

    Train Acc: 66.83

    Valid Acc:65.34 / 65.67(max and save weight)

    Train loss: 0.61

    Valid loss:0.62

### 19/11/2021

4. Convo1D with 300 epoch all subject
    
    Train Acc: 66.97

    Valid Acc: 64.11 / 64.88 (max and save weight)

    Train loss:0.6113

    Valud loss:0.6164

### 20/11/2021
Insert batchnorm2D and dropout to all convolution 

5. Convo1D finetune with 300epoch all subject (use batchnorm2d)

    Train Acc: 54.94%

    Valid Acc: 49.54% / 51.92(max and save weight)

    Train loss: 0.685

    Valid loss: 0.6930

6. Convo1D finetune with 300epoch all subject (use batchnorm1d)

    Train Acc: 57.29%

    Valid Acc: 41.67% / 62.50(max and save weight)

    Train loss: 0.61

    Valid loss: 0.58

### 21/11/2021
7. Convo2D finetune with 300 epoch all subject(use batchnorm2d and max pooling2d)

    Train Acc: 52.76%

    Valid Acc: 53.37 / 52.76(max and save weight)

    Train loss: 0.69346

    Valid loss: 0.69341

### 22/11/2021
Adapt temporal and spatial, reduce third convolution in B block

8. Convo2D Newfinetune with 300 epoch all subject(batchnorm2d and max pooling2d)
    25 125 4
    Train Acc: 58.26

    Valid Acc: 51.38

    Train loss: 0.66

    Valid loss: 0.69

9. Convo2D normal with 300 epoch all subject (no maxpooling2d)

    Train Acc: 55.35

    Valid Acc: 51.30

    Train loss: 0.67

    Valid loss: 0.69