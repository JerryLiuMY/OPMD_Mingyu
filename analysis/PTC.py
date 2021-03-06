import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from analysis.tools import CHANNEL_5
from analysis.tools import load_hdul, load_data
from analysis.tools import dip_remove, poly_fit
import matplotlib.gridspec as gridspec
sns.set()


def raw_PTC(file_name, ax):
    hdul, vbb, wideint, wwideint = load_hdul(file_name)
    for C in CHANNEL_5:
        channel_data = hdul[1].data[hdul[1].data['chans'] == C]
        mean, diffvr = channel_data['mn1db'], channel_data['diffvr']
        mean, diffvr = dip_remove(mean, diffvr)
        mean, diffvr = mean/1000, diffvr/1000
        ax.plot(mean, diffvr, 'o', label=f'Channel {str(C)}')

    ax.legend(loc='upper left')
    ax.set_xlabel('Mean (kADU)')
    ax.set_ylabel('Variance ($kADU^2$)')


def PTC(file_name, ax1, ax2, cutoff=1):
    hdul, vbb, wideint, wwideint = load_hdul(file_name)
    diffvr_els = 0
    for C in CHANNEL_5:
        mean_el, diffvr_el, corr, gain = load_data(hdul, C, cutoff=cutoff)
        mean_el, diffvr_el = mean_el/1000, diffvr_el/1000
        ax1.plot(mean_el, diffvr_el, 'o', label=f'Channel {str(C)}')
        ax2.plot(mean_el, diffvr_el - mean_el, 'o', label=f'Channel {str(C)}')

        diffvr_els += diffvr_el/4

    lin = np.linspace(0, 70 * cutoff, 5000)
    ax1.plot(lin, lin, '--')
    ax1.legend(loc='upper left')
    ax1.set_xlabel('Mean (kel)')
    ax1.set_ylabel('Variance ($kel^2$)')
    ax1.annotate('Possion Noise: $\sigma_{S}^{2}=\mu$', xy=(60, 60), xytext=(40, 69),
                 arrowprops=dict(width=2, headlength=4, facecolor='black'), fontsize=14)
    ax1.set_xlim(-2, 72 * cutoff)

    lin = np.linspace(0, 70 * cutoff, 5000)
    ax2.plot(lin, np.zeros(5000), '--')
    ax2.legend(loc='lower left')
    ax2.set_xlabel('Mean (kel)')
    ax2.set_ylabel('Variance ($kel^2$)')
    ax2.set_xlim(-2, 72 * cutoff)

    return diffvr_els


def PTC_fit(file_name, deg, ax3):
    hdul, vbb, wideint, wwideint = load_hdul(file_name)
    data_len = len(load_data(hdul, 5)[0])
    mean_el_ave, diffvr_el_ave = np.zeros(np.shape(data_len)), np.zeros(np.shape(data_len))

    for idx, C in enumerate(CHANNEL_5):
        mean_el, diffvr_el, corr, gain = load_data(hdul, C)
        mean_el, diffvr_el = mean_el/1000, diffvr_el/1000
        mean_el_ave, diffvr_el_ave = mean_el_ave + mean_el/4, diffvr_el_ave + diffvr_el/4
    diffvr_el_1, diffvr_el_n = poly_fit(mean_el_ave, diffvr_el_ave, deg)

    ax3.plot(mean_el_ave, diffvr_el_ave - diffvr_el_1, 'x', label=f'deg=1')
    ax3.plot(mean_el_ave, diffvr_el_ave - diffvr_el_n, 'x', label=f'deg={deg}')
    ax3.set_xlabel('Mean (kel)')
    ax3.set_ylabel('Residual ($kel^2$)')
    ax3.legend()

    # lin = np.linspace(0, 60000, 5000)
    # ax4.plot(lin, lin, '--', label=f'Poisson')
    # ax4.plot(mean_el_ave, diffvr_el_ave, 'o', label=f'PTC')
    # ax4.legend()


if __name__ == '__main__':
    raw_PTC, ax = plt.subplots(1, 1, figsize=(8, 5))
    PTC = plt.figure(figsize=(12, 12))
    gs = gridspec.GridSpec(7, 2)
    ax1 = plt.subplot(gs[0:5, 0])
    ax2 = plt.subplot(gs[0:5, 1])
    ax3 = plt.subplot(gs[5:, :])
    PTC('PTC20-29-04-00-22-54.fits', ax, ax1, ax2)
    PTC_fit('PTC20-29-04-00-22-54.fits', deg=2, ax3=ax3)
