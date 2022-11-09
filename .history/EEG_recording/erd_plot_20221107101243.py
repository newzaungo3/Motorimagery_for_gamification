
# importing packages
import seaborn as sns
import matplotlib.pyplot as plt
 
# loading dataset
data = sns.load_dataset("iris")
 
# draw lineplot
sns.lineplot(x="sepal_length", y="sepal_width", data=data)
 
# setting the title using Matplotlib
plt.title('Title using Matplotlib Function')
 
plt.show()