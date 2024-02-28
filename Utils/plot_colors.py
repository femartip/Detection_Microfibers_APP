import matplotlib.pyplot as plt

colors = ["red", "green", "yellow", "blue", "pink","blue","blue","blue","yellow","blue","black","blue","black","blue","red","pink","pink","yellow","black", "blue"]
values = [[0,100,50],[147,50,47],[39,100,50],[240,100,50],[300,76,72],[206,20,49],[223,32,48],[225,25,32],[64,31,56],[216,35,61],[223, 19, 36],[216, 57, 55],[199, 29, 61],[206, 8, 52],[317, 45, 58],[252, 20, 51],[254, 18, 68],[58, 32, 50],[123, 10, 43],[197,20,49]]

# Make a 3d scatter plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
print(len(colors))
print(len(values))
for i, color in enumerate(colors):
    if i < 5:
        print(color)
        ax.scatter(values[i][0], values[i][1], values[i][2], c=color, marker='d')
    else:
        ax.scatter(values[i][0], values[i][1], values[i][2], c=color, marker='o')
ax.set_xlabel('Hue')
ax.set_ylabel('Saturation')
ax.set_zlabel('Lightness')
plt.show()