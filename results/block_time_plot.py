import matplotlib.pyplot as plt

# Given the results for 5 and 10 nodes, create the comparison plots
bl_5 = [1.7320635300081186, 2.7912658330940068, 1.275965280424828, 2.1529532075327613, 4.6646684945784305, 3.358282789706025]
bl_10 = [3.0320635300081186, 4.4012658330940068, 2.275965280424828, 4.1529532075327613, 8.6646684945784305, 5.358282789706025]

x = [5, 10]

pl_4_1 = [bl_5[0], bl_10[0]]
pl_4_10 = [bl_5[1], bl_10[1]]
pl_4_5 = [bl_5[2], bl_10[2]]
pl_5_1 = [bl_5[3], bl_10[3]]
pl_5_10 = [bl_5[4], bl_10[4]]
pl_5_5 = [bl_5[5], bl_10[5]]

# plotting the points  
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
plt.ylabel('Average Block Time (sec)')
# giving a title to my graph
plt.title('Block time of the system according to number of nodes, capacity and difficulty')

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



