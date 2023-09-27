import matplotlib.pyplot as plt

# Given the results for 5 and 10 nodes, create the comparison plots

thr_5 = [0.15894015578116263, 3.430502391723948, 1.3902643902656862, 0.10502629272409461, 1.5983972285353045, 0.7322081821666063]
thr_10 = [0.04894015578116263, 1.930502391723948, 0.6902643902656862, 0.01802629272409461, 0.8083972285353045, 0.2322081821666063]

# number of nodes
x = [5, 10]

pl_4_1 = [thr_5[0], thr_10[0]]
pl_4_10 = [thr_5[1], thr_10[1]]
pl_4_5 = [thr_5[2], thr_10[2]]
pl_5_1 = [thr_5[3], thr_10[3]]
pl_5_10 = [thr_5[4], thr_10[4]]
pl_5_5 = [thr_5[5], thr_10[5]]

plt.plot(x, pl_4_1, color='orange', linestyle='dashed', linewidth = 1,
         marker='o', markerfacecolor='orange', markersize=4, label = "d4-c1")
plt.plot(x, pl_4_10, color='purple', linestyle='dashed', linewidth = 1,
         marker='o', markerfacecolor='purple', markersize=4, label = "d4-c10")
plt.plot(x, pl_4_5, color='green', linestyle='dashed', linewidth = 1,
         marker='o', markerfacecolor='green', markersize=4, label = "d4-c5")
plt.plot(x, pl_5_1, color='blue', linestyle='dashed', linewidth = 1,
         marker='o', markerfacecolor='blue', markersize=4, label = "d5-c1")
plt.plot(x, pl_5_10, color='red', linestyle='dashed', linewidth = 1,
         marker='o', markerfacecolor='red', markersize=4, label = "d5-c10")
plt.plot(x, pl_5_5, color='black', linestyle='dashed', linewidth = 1,
         marker='o', markerfacecolor='black', markersize=4, label = "d5-c5")
    
  
# naming the x axis
plt.xlabel('Number of nodes in the system')
# naming the y axis
plt.ylabel('Throughput (transactions/sec)')
# giving a title to my graph
plt.title('Throughput of the system according to number of nodes, capacity and difficulty')

plt.text(x[-1], pl_4_1[-1], 'd4-c1', fontsize=9, verticalalignment='bottom', horizontalalignment='right', color='orange')
plt.text(x[-1], pl_4_10[-1], 'd4-c10', fontsize=9, verticalalignment='top', horizontalalignment='right', color='purple')
plt.text(x[-1], pl_4_5[-1], 'd4-c5', fontsize=9, verticalalignment='bottom', horizontalalignment='right', color='green')
plt.text(x[-1], pl_5_1[-1], 'd5-c1', fontsize=9, verticalalignment='top', horizontalalignment='right', color='blue')
plt.text(x[-1], pl_5_10[-1], 'd5-c10', fontsize=9, verticalalignment='bottom', horizontalalignment='right', color='red')
plt.text(x[-1], pl_5_5[-1], 'd5-c5', fontsize=9, verticalalignment='top', horizontalalignment='right', color='black')

# show a legend on the plot
plt.legend()
  
# function to show the plot
plt.show()
