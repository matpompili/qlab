import numpy as np
import matplotlib.pyplot as plt
from scipy import optimize
plt.style.use('ggplot')

def HOM_func(x, *p):
    a, vis, x0, sigma = p
    return a * (1 - vis * np.exp( - 4 * np.log(2) * ((x-x0) / sigma)**2))

def hom_plot(steps_number, channels_number, file_name,  exclude_channels = [], center = -1):
    if center == -1:
        center = steps_number/2
    #create and populate the dictionary
    channel_dict = {}
    inv_channel_dict = {}

    coinc_counts = np.zeros((channels_number*(channels_number-1), steps_number), dtype=int)
    i = 0
    for c1 in np.arange(1, channels_number + 1):
        for c2 in np.arange(c1 + 1, channels_number + 1):
                if (c1 not in exclude_channels and c2 not in exclude_channels):
                    ch_tag = "%02d_%02d" % (c1,c2)
                    channel_dict.update({ch_tag : i})
                    inv_channel_dict.update({i : ch_tag})
                    #ch_tag = "%d_%d" % (c1,c2)
                    #channel_dict.update({ch_tag : i})
                    #ch_tag = "%d_%d" % (c2,c1)
                    #channel_dict.update({ch_tag : i})
                    i += 1

    #open the file
    with open(file_name) as coinc_file:
        #run through the file
        for line in coinc_file:
            #check if the line is a step marker
            if (len(line.strip()) >= 1  and line.find("_") == -1):
                step = int(line.strip())
            elif len(line.strip()) > 1:
                part_line = line.strip().partition(" ")
                try:
                    coinc_counts[channel_dict[part_line[0]], step] += int(part_line[-1])
                except KeyError:
                    print("What? Key: " + part_line[0])
                    pass

    for i in range(channels_number * (channels_number-1)) :
        if (coinc_counts[i].sum() != 0):
            starting_par = np.max(coinc_counts[i,...]), 0.5, center, steps_number/10
            points = np.arange(1,steps_number + 1)
            could_fit = True
            try:
                popt, pcov = optimize.curve_fit(f = HOM_func,
                                             xdata = points,
                                             ydata = coinc_counts[i],
                                             p0 = starting_par,
                                             sigma = np.sqrt(coinc_counts[i]),
                                             absolute_sigma = True)
            except RuntimeError:
                could_fit = False
                pass

            print(inv_channel_dict[i])
            plt.figure(figsize=(8,5))
            if (could_fit):
                print('x0 = %f | sigma = %f' % (popt[2], np.sqrt(pcov[2,2])))
                print('vis = %f | sigma = %f' % (popt[1], np.sqrt(pcov[1,1])))
                plt.plot(points, HOM_func(points, *popt), '--')
                plt.plot((popt[2], popt[2]), (0, np.min(coinc_counts[i])/2), '--')

            plt.errorbar(y = coinc_counts[i], x = points, yerr= np.sqrt(coinc_counts[i]), fmt='o', color='indianred')
            plt.ylim(ymin = 0)
            plt.ylabel('Coincidences')
            plt.xlabel('Displacement')
            plt.show()
