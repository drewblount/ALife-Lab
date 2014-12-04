import matplotlib.pyplot as plt
import numpy as np

## makes a heatmap out of the 2d numpy array made by arraymaker

arr = np.load('emp_neut_2darray.npy')

#clipped = np.clip(arr, 0, 10)

arr = np.log(np.transpose(arr))[:100]

max = round(np.max(arr),1)



plt.imshow(arr,origin='lower',aspect=25./2)

cbar = plt.colorbar(ticks=[0,max])
cbar.ax.set_yticklabels([0,max])
cbar.set_label(r'log of citation count')



plt.title('Empirical Cite Distribution')
plt.xlabel('parent age in weeks (at citation)')
plt.ylabel('prior cites to parents')
plt.show()