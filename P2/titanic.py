
# coding: utf-8

# In[1]:


get_ipython().magic(u'matplotlib inline')

# Do below if you want interactive matplotlib plot ()
# %matplotlib notebook 

# https://ipython.org/ipython-doc/dev/config/extensions/autoreload.html
get_ipython().magic(u'load_ext autoreload')
get_ipython().magic(u'autoreload 2')

# %install_ext http://raw.github.com/jrjohansson/version_information/master/version_information.py
get_ipython().magic(u'load_ext version_information')
get_ipython().magic(u'version_information numpy, scipy, matplotlib, pandas;')


# In[2]:


# standard library

# thirdparty library
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats

# local imports


# In[3]:


# customizations
sns.set()  # matplotlib defaults

# see value of statements at once
from IPython.core.interactiveshell import InteractiveShell
InteractiveShell.ast_node_interactivity = "all"

# any tweaks that normally go in .matplotlibrc, etc., should explicitly go here
plt.rcParams['figure.figsize'] = (12, 8)
get_ipython().magic(u"config InlineBackend.figure_format = 'retina'")


# In[4]:


# global variables

passengers = pd.read_csv('./data/titanic-data.csv')


# # Titanic: 具备哪些条件的人在灾难中更有可能生还

# ## 加载并检查数据

# 浏览原始数据，明确数据中各字段含义，其中：
# 
# > | Variable | Definition  |
# | --- | --- |
# | pclass | Ticket class(1 = 1st, 2 = 2nd, 3 = 3rd) |
# | sibsp | # of siblings / spouses aboard the Titanic |
# | parch | # of parents / children aboard the Titanic |
# | embarked | Port of Embarkation(C = Cherbourg, Q = Queenstown, S = Southampton) |
# 
# > pclass: A proxy for socio-economic status (SES)
# > 1st = Upper
# > 2nd = Middle
# > 3rd = Lower
# 
# > age: Age is fractional if less than 1. If the age is estimated, is it in the form of xx.5
# 
# > sibsp: The dataset defines family relations in this way...
# > Sibling = brother, sister, stepbrother, stepsister
# > Spouse = husband, wife (mistresses and fiancés were ignored)
# 
# > parch: The dataset defines family relations in this way...
# > Parent = mother, father
# > Child = daughter, son, stepdaughter, stepson
# > Some children travelled only with a nanny, therefore parch=0 for them.

# 原始数据示例如下：

# In[5]:


passengers.head()


# 其中包含数据条数：

# In[6]:


passengers.PassengerId.count()


# 总人数：

# In[7]:


len(passengers.Name.unique())


# 可见其中不包含原始数据。幸存者人数和遇难者人数统计如下：

# In[34]:


passengers.groupby('Survived').Survived.count()


# ## 分析数据

# 现代社会中，当灾难发生时，逃生的妇孺优先原则是每个人都应该遵守的社会义务。下面就以性别、年龄等因素对于幸存与否的影响作为切入点，对现有数据进行分析。

# ### 1. 性别对于幸存与否的影响

# 选择饼图展示，可以清晰的看出男性与女性乘客幸存的比例。

# In[9]:


pies = passengers.groupby(['Survived', 'Sex']).Survived.count().unstack().plot.pie(subplots=True);
[p.axis('equal') for p in pies];


# 从上图可以看出，在 Titanic 沉船事故中女性具有更高的幸存几率，幸存率分别为：

# In[31]:


passengers.groupby('Sex').Survived.mean()


# 使用 X^2 检验计算性别与幸存与否的相关性。

# In[11]:


frequency_table = pd.crosstab(passengers.Survived, passengers.Sex); frequency_table


# In[12]:


chi2,pval,dof,expected = stats.chi2_contingency(frequency_table)
print 'Chi2 test statistic: {}'.format(chi2)
print 'p-value: {}'.format(pval)


# P value 趋近于零，可见性别与幸存与否存在明显相关性。

# ## 2. 年龄对于幸存与否的影响

# 提取幸存者的年龄数据，并将空数据丢弃。

# In[ ]:


survivors_age = survivors.Age.dropna()


# 对于年龄数据中存在小数点的情况，将其向上取整。

# In[14]:


survivors_age = np.ceil(survivors_age)


# In[15]:


survivors_age.describe()


# 幸存乘客年龄分布，及其在全部乘客中所占比例如下：

# In[16]:


passengers_age = np.ceil(passengers.Age.dropna())
passengers_age.hist(bins=40);
survivors_age.hist(bins=40);
plt.xlabel('Age');
plt.ylabel('Number of Person');
plt.legend(['all', 'survivor']);


# 当灾难发生时，除了女性外，社会伦理导致小孩同样具有优先获救的可能。在 Titanic 沉船事故中，12 岁以下的小孩和其余成年人的幸存率分别为：

# In[17]:


def child(index):
    if index <= 12:
        return 'child'
    else:
        return 'adult'
survivors_age.apply(child).value_counts() / passengers_age.apply(child).value_counts()


# 可见，在 Titanic 沉船事故中，小孩同样具有更高的幸存几率。同样使用 X^2 检验验证相关性。

# In[18]:


crosstab = pd.crosstab(passengers.Survived, passengers_age.apply(child));crosstab


# In[19]:


chi2,pval,dof,expected = stats.chi2_contingency(crosstab)
print 'p-value: {}'.format(pval)


# P-value 远小于 5%，说明 12 岁以下的小孩更有可能幸存。

# ## 3. Titanic 事件中是否存在“头等舱”妇孺优先的问题

# 在 Titanic 的电影中，有一个情节是为了保证头等舱中有较高社会地位的乘客优先登上救生艇，船员们甚至临时关闭了下层夹板乘客通往船桥夹板的通道。这在我们的统计数据中也得到了验证，其中社会经济地位高或中等的乘客幸存的比例远远大于社会地位较低的乘客。

# In[20]:


passengers.groupby(['Pclass', 'Survived']).Survived.count().unstack().plot.bar();
plt.ylabel('Count of Passengers');


# 灾难危机事件中，逃生的妇孺优先原则是现代社会人人都要遵守的义务。通过对于年龄和性别因素的分析，在 Titanic 灾难中，这一原则似乎有被遵守。但是也有一种说法认为，Titanic 遵守的只是"头等舱"乘客的妇孺优先原则。

# In[21]:


female_child_fq = passengers[(passengers.Sex == 'female') | (passengers.Age <= 12)].groupby(['Pclass', 'Survived']).Survived.count().unstack()
female_child_fq


# 通过上述统计数据也的确可以看出这样的趋势，社会经济地位高或中等的乘客中妇女和儿童绝大部分都已获救，但社会经济地位较低的乘客中的妇女和儿童获救的比例甚至不足 50%。

# 对上述频率表执行 X^2 检验：

# In[22]:


chi2,pval,dof,expected = stats.chi2_contingency(female_child_fq)
print 'P-value: {}'.format(pval)


# P-value 的值接近于零。可见，妇女、儿童是否可以获救与他们的社会地位存在很强的相关性。

# ## 结论

# 可见，在 Titanic 沉船事故中，妇孺优先原则能够被比较好的遵守。但是遗憾的是，最终能否获救与他们所处的社会地位仍然有很大关系。

# ## References
# 
# * https://svds.com/jupyter-notebook-best-practices-for-data-science/
# * https://www.kaggle.com/mrisdal/exploring-survival-on-the-titanic
# * http://wiki.mbalib.com/wiki/%E6%98%BE%E8%91%97%E6%80%A7%E6%A3%80%E9%AA%8C#.E6.98.BE.E8.91.97.E6.80.A7.E6.A3.80.E9.AA.8C.E5.BA.94.E6.B3.A8.E6.84.8F.E7.9A.84.E9.97.AE.E9.A2.98
