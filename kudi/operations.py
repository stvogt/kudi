#! /usr/bin/python

import sys, re, os, subprocess, shutil
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.ticker import MaxNLocator

# plt.switch_backend('agg')
from scipy.integrate import simps
from scipy.integrate import cumtrapz
from . import singlePoint as sp
from . import tvregdiff

header = """
-----------------------------------------------------------------------
          kudi: An Open-Source Reaction Path Proccesing Library
                            kudi 0.3.0

                            S. Vogt-Geisse
-----------------------------------------------------------------------
"""


def read_lines(outfile):
    if not os.path.exists(outfile):
        print(outfile + " does not exist there -> " + os.getcwd())
        sys.exit(2)
    outputfile = open(outfile, "r")
    outputLines = outputfile.readlines()
    outputfile.close()
    return outputLines


def simple_plot(x, y):
    plt.plot(x, y, "ro")
    # plt.axhline(y=0, color='red')
    plt.show()


def fit(x_coord, y_coord, rank):
    fx_coord = list(map(float, x_coord))
    fy_coord = list(map(float, y_coord))
    x = np.array(fx_coord)
    y = np.array(fy_coord)
    z = np.polyfit(x, y, rank)

    # creat polynomial function
    p = np.poly1d(z)

    # plot
    xp = np.linspace(frx_coord[0], frx_coord[-1], 100)
    plt.plot(x, y, ".", xp, p(xp), "-")
    plt.show()


def algo():
    print("algo")


def neg_derivative(x_coord, y_coord):
    fx_coord = list(map(float, x_coord))
    fy_coord = list(map(float, y_coord))
    x = np.array(fx_coord)
    y = np.array(fy_coord)
    f = -np.diff(y) / np.diff(x)
    return (fx_coord[1:], f)


def derivative(x_coord, y_coord):
    fx_coord = list(map(float, x_coord))
    fy_coord = list(map(float, y_coord))
    x = np.array(fx_coord)
    y = np.array(fy_coord)
    f = np.diff(y) / np.diff(x)
    return (fx_coord[1:], f)


def neg_derivative_smooth(x_coord, y_coord):
    fx_coord = list(map(float, x_coord))
    fy_coord = list(map(float, y_coord))
    x = np.array(fx_coord)
    y = np.array(fy_coord)
    f = -tvregdiff.TVRegDiff(
        y, 20, 1e-1, dx=0.05, ep=1e-2, scale="large", plotflag=0
    ) / tvregdiff.TVRegDiff(x, 20, 1e-1, dx=0.05, ep=1e-2, scale="large", plotflag=0)
    return (x, f)


def integrate(x_coord, y_coord):
    fx_coord = list(map(float, x_coord))
    fy_coord = list(map(float, y_coord))
    x = np.array(fx_coord)
    y = np.array(fy_coord)
    work = simps(y, x)
    # work = np.trapz(y, x)
    return work


def unique(List):
    output = []
    for x in List:
        if not x in output:
            output.append(x)
    return output


def print_lists(list1, list2, list1_name, list2_name, filename):
    f = open(filename + ".dat", "w")
    f.write(header)
    f.write("Generated output from print_lists routine\n\n")
    f.write("%2s %20s %20s" % (" ", list1_name, list2_name) + "\n")
    for j in range(0, len(list1)):
        f.write(
            "%2d %20f %20f"
            % (j + 1, round(float(list1[j]), 5), round(float(list2[j]), 5))
            + "\n"
        )


def general_print(filename, **kwargs):
    f = open(filename, "w")
    f.write("{0:s},".format("rx_coord"))
    for key in kwargs:
        if key == "Reaction Coordinate":
            iter_range = len(kwargs[key])
        if key != "Reaction Coordinate":
            f.write("{0:s},".format(key))
    f.write("\n")
    for j in range(0, iter_range):
        for key in kwargs:
            if key == "Reaction Coordinate":
                f.write("{0:.2f},".format(round(float(kwargs[key][j]), 3)))
            else:
                continue
        for key in kwargs:
            if key != "Reaction Coordinate":
                f.write("{0:.6f},".format(round(float(kwargs[key][j]), 6)))
        f.write("\n")


def num_valence_orbs(atom_list):
    val_dict = {
        "1": 1,
        "2": 2,
        "3": 1,
        "4": 2,
        "5": 3,
        "6": 4,
        "7": 5,
        "8": 6,
        "9": 7,
        "10": 8,
        "11": 1,
        "12": 2,
        "13": 3,
        "14": 4,
        "15": 5,
        "16": 6,
        "17": 7,
        "18": 8,
        "19": 1,
        "20": 2,
    }
    val_elec = 0
    for atom in atom_list:
        val_elec = val_elec + val_dict[atom]
    val_orbs = val_elec / 2
    return val_orbs


def general_plot(
    plotname,
    ylabel,
    limit_list,
    bullets,
    yspacing,
    works,
    zeroline,
    show,
    latex,
    **kwargs
):
    count = 0
    if latex:
        plt.rc("text", usetex=True)
    plt.rc("font", family="serif")
    for key in kwargs:
        if key == "Reaction Coordinate":
            x = kwargs[key]
            plt.xlabel(r"$\mathbf{\xi}$ (a$_{0}$amu$^{\frac{1}{2}}$)", fontsize=18)
            plt.xticks(fontsize=18)
    for key in kwargs:
        if key != "Reaction Coordinate":
            plt.plot(x, kwargs[key], bullets[count], markeredgecolor="none")
            count = count + 1
    if zeroline:
        plt.axhline(y=0, color="red")
    if works:
        plt.axvline(x=works[4], color="black", linestyle="dashed")
        plt.axvline(x=works[5], color="black", linestyle="dashed")
    if not limit_list:
        plt.yticks(fontsize=18)
    if limit_list:
        if not yspacing:
            yspacing = (max(limit_list) - min(limit_list)) / 5
        plt.yticks(np.arange(min(limit_list), max(limit_list), yspacing), fontsize=18)
        # axes.set_ylim(limit_list)
    plt.ylabel(ylabel, fontsize=22)
    axes = plt.gca()
    print("Saving the plot in ./figures as " + plotname)
    print("----------------------------------------------------------")
    plt.savefig(plotname)
    if show:
        plt.show()
    plt.clf()


def general_plot_props(
    plotname,
    ylabel,
    proplist,
    limit_list,
    yspacing,
    bullets,
    works,
    zeroline,
    show=True,
    **kwargs
):
    count = 0
    # plt.rc('text', usetex=True)
    plt.rc("font", family="serif")
    for key in kwargs:
        if key == "Reaction Coordinate":
            x = kwargs[key]
            plt.xlabel(r"$\mathbf{\xi}$ (a$_{0}$amu$^{\frac{1}{2}}$)", fontsize=18)
            plt.xticks(fontsize=18)
    for key in proplist:
        if key != "Reaction Coordinate":
            plt.plot(x, kwargs[key], bullets[count], label=key, markeredgecolor="none")
            count = count + 1
    if zeroline:
        plt.axhline(y=0, color="red")
    if works:
        plt.axvline(x=works[4], color="black", linestyle="dashed")
        plt.axvline(x=works[5], color="black", linestyle="dashed")
    if not limit_list:
        plt.yticks(fontsize=18)
    if limit_list:
        if not yspacing:
            yspacing = (max(limit_list) - min(limit_list)) / 5
        plt.yticks(np.arange(min(limit_list), max(limit_list), yspacing), fontsize=18)

    plt.ylabel(ylabel, fontsize=22)
    plt.legend(loc=0, bbox_to_anchor=(1.05, 1))  # Not sure why this is not working
    axes = plt.gca()
    axes.set_ylim(limit_list)
    print("Saving the plot in ./figures as " + plotname)
    print("----------------------------------------------------------")
    plt.savefig(plotname)
    if show:
        plt.show()
    plt.clf()


def plot_multi(
    plotname,
    ylabel,
    prop_list,
    limit_list,
    yspacing,
    bullets,
    works,
    zeroline,
    show=False,
):
    keys = []
    count = 0
    # plt.rc('text', usetex=True)
    plt.rc("font", family="serif")
    for dicto in prop_list:
        for key in dicto.keys():
            if key == "Reaction Coordinate":
                x = dicto[key]
                plt.xlabel(r"$\mathbf{\xi}$ (a$_0$amu$^{\frac{1}{2}}$)", fontsize=18)
                plt.xticks(fontsize=18)
        for key in dicto.keys():
            if key != "Reaction Coordinate":
                y = dicto[key]
                count = count + 1
                plt.plot(x, y, bullets[count], label=key, markeredgecolor="none")
    if zeroline:
        plt.axhline(y=0, color="red")
    if works:
        plt.axvline(x=works[4], color="black", linestyle="dashed")
        plt.axvline(x=works[5], color="black", linestyle="dashed")
    if not limit_list:
        plt.yticks(fontsize=18)
    if limit_list:
        if not yspacing:
            yspacing = (max(limit_list) - min(limit_list)) / 5
        plt.yticks(np.arange(min(limit_list), max(limit_list), yspacing), fontsize=18)
    plt.ylabel(ylabel, fontsize=22)
    axes = plt.gca()
    axes.set_ylim(limit_list)
    plt.legend(loc=0, bbox_to_anchor=(1.05, 1))
    print("Saving the plot in ./figures as " + plotname)
    print("----------------------------------------------------------")
    plt.savefig(plotname)
    if show:
        plt.show()
    plt.clf()


def general_plot_prop_with_cuts(
    plotname,
    ylabel,
    proplist,
    limit_list1,
    limit_list2,
    yspacing1,
    yspacing2,
    bullets,
    works,
    show=False,
    **kwargs
):
    # ONLY WORKS FOR TWO DIFFERENT PORPERTIES!!!
    count = 0
    # plt.rc('text', usetex=True)
    plt.rc("font", family="serif")
    f, axarr = plt.subplots(2, 1, sharex=True)
    count = 0
    if not yspacing1:
        yspacing1 = (max(limit_list1) - min(limit_list1)) / 4
    if not yspacing2:
        yspacing2 = (max(limit_list2) - min(limit_list2)) / 4
    for key in kwargs:
        if key == "Reaction Coordinate":
            x = kwargs[key]
            plt.xlabel(r"$\mathbf{\xi}$ (a$_{0}$amu$^{\frac{1}{2}}$)", fontsize=18)
            plt.xticks(fontsize=18)
    for key in proplist:
        if key != "Reaction Coordinate":
            axarr[count].plot(
                x, kwargs[key], bullets[count], label=key, markeredgecolor="none"
            )
            axarr[count].legend(loc=0, bbox_to_anchor=(1.05, 1))
            count = count + 1
    if works:
        axarr[0].axvline(x=works[4], color="black", linestyle="dashed")
        axarr[0].axvline(x=works[5], color="black", linestyle="dashed")
        axarr[1].axvline(x=works[4], color="black", linestyle="dashed")
        axarr[1].axvline(x=works[5], color="black", linestyle="dashed")
    plt.ylabel(ylabel, fontsize=22)
    axarr[0].set_ylim(limit_list1[0], limit_list1[1])  # outliers only
    axarr[0].yaxis.set_ticks(np.arange(min(limit_list1), max(limit_list1), yspacing1))
    axarr[1].set_ylim(limit_list2[0], limit_list2[1])  # most of the data
    axarr[1].yaxis.set_ticks(np.arange(min(limit_list2), max(limit_list2), yspacing2))

    axarr[0].spines["bottom"].set_visible(False)
    axarr[1].spines["top"].set_visible(False)
    axarr[0].xaxis.tick_top()
    axarr[0].tick_params(
        labeltop="off", labelsize=18
    )  # don't put tick labels at the top
    axarr[1].tick_params(labelsize=18)  # don't put tick labels at the top
    axarr[1].xaxis.tick_bottom()

    d = 0.015  # how big to make the diagonal lines in axes coordinates
    # arguments to pass plot, just so we don't keep repeating them
    kwargs = dict(transform=axarr[0].transAxes, color="k", clip_on=False)
    axarr[0].plot((-d, +d), (-d, +d), **kwargs)  # top-left diagonal
    axarr[0].plot((1 - d, 1 + d), (-d, +d), **kwargs)  # top-right diagonal
    kwargs.update(transform=axarr[1].transAxes)  # switch to the bottom axes
    axarr[1].plot((-d, +d), (1 - d, 1 + d), **kwargs)  # bottom-left diagonal
    axarr[1].plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)  # bottom-right diagonal

    # axes.set_ylim(limit_list)
    print("Saving the plot in ./figures as " + plotname)
    print("----------------------------------------------------------")
    plt.savefig(plotname)
    if show:
        plt.show()
    plt.clf()


def general_plot_scales(
    plotname,
    ylabel1,
    ylabel2,
    dictos,
    proplist,
    limit_list1,
    limit_list2,
    yspacing1,
    yspacing2,
    works,
    zeroline,
    show=False,
):
    # ONLY WORKS FOR TWO DIFFERENT PORPERTIES!!!
    print("Generating the plot....")
    bullets = ["bo", "rs", "k^", "b-", "m-.", "bo", "rs", "k^", "g-", "m-."]
    count = 0
    # plt.rc('text', usetex=True)
    plt.rc("font", family="serif")
    count = 0
    count1 = 0

    fig, ax1 = plt.subplots()
    for dic in dictos:
        if count == 0:
            x = dic["Reaction Coordinate"]
            ax1.set_xlabel(r"$\mathbf{\xi}$ (a$_{0}$amu$^{\frac{1}{2}}$)", fontsize=18)
            plt.xticks(fontsize=18)
            for key in dic:
                if key != "Reaction Coordinate":
                    y = dic[key]
                    ax1.plot(x, y, bullets[count1], label=key, markeredgecolor="none")
                    ax1.set_ylabel(ylabel1, fontsize=18)
                    count1 += 1

        if count == 1:
            count2 = count1
            x = dic["Reaction Coordinate"]
            for key in dic:
                if key != "Reaction Coordinate":
                    y = dic[key]
                    ax2 = ax1.twinx()
                    ax2.plot(x, y, bullets[count2], label=key, markeredgecolor="none")
                    if count2 == count1:
                        ax2.set_ylabel(ylabel2, fontsize=18)
                    count2 += 1
        count += 1
    if works:
        plt.axvline(x=works[4], color="black", linestyle="dashed")
        plt.axvline(x=works[5], color="black", linestyle="dashed")
    print("Saving the plot in ./figures as " + plotname)
    print("----------------------------------------------------------")
    plt.savefig(plotname)
    if show:
        plt.show()
    plt.clf()


def atom_label(atom_num_list):
    atom_dict = {
        "1": "H",
        "2": "He",
        "3": "Li",
        "4": "Be",
        "5": "B",
        "6": "C",
        "7": "N",
        "8": "O",
        "9": "F",
        "10": "Ne",
        "11": "Na",
        "12": "Mg",
        "13": "Al",
        "14": "Si",
        "15": "P",
        "16": "S",
        "17": "Cl",
        "18": "Ar",
        "19": "K",
        "20": "Ca",
        "21": "Sc",
        "22": "Ti",
        "23": "V",
        "24": "Cr",
        "25": "Mn",
        "26": "Fe",
        "27": "Co",
        "28": "Ni",
        "29": "Cu",
        "30": "Zn",
        "31": "Ga",
        "32": "Ge",
        "33": "As",
        "34": "Se",
        "35": "Se",
        "36": "Br",
        "36": "Kr",
        "37": "Rb",
        "38": "Sr",
        "39": "Y",
        "40": "Zr",
        "41": "Nb",
        "42": "Mo",
        "43": "Tc",
        "44": "Ru",
        "45": "Rh",
        "46": "Pd",
        "47": "Ag",
        "48": "Cd",
        "49": "In",
        "50": "Sn",
        "51": "Sb",
        "52": "Te",
        "55": "Cs",
        "56": "Ba",
        "72": "Hf",
        "73": "Ta",
        "74": "W",
        "75": "Re",
        "76": "Os",
        "77": "Ir",
        "78": "Pt",
        "79": "Au",
        "80": "Hg",
        "81": "Ti",
        "82": "Pb",
        "83": "Bi",
        "84": "Po",
    }
    atom_label = []
    for atom_num in atom_num_list:
        atom_label.append(atom_dict[atom_num])
    return atom_label


def Num2atom(atom_num):
    atom_dict = {
        "1": "H",
        "2": "He",
        "3": "Li",
        "4": "Be",
        "5": "B",
        "6": "C",
        "7": "N",
        "8": "O",
        "9": "F",
        "10": "Ne",
        "11": "Na",
        "12": "Mg",
        "13": "Al",
        "14": "Si",
        "15": "P",
        "16": "S",
        "17": "Cl",
        "18": "Ar",
        "19": "K",
        "20": "Ca",
        "21": "Sc",
        "22": "Ti",
        "23": "V",
        "24": "Cr",
        "25": "Mn",
        "26": "Fe",
        "27": "Co",
        "28": "Ni",
        "29": "Cu",
        "30": "Zn",
        "31": "Ga",
        "32": "Ge",
        "33": "As",
        "34": "Se",
        "35": "Se",
        "36": "Br",
        "36": "Kr",
        "37": "Rb",
        "38": "Sr",
        "39": "Y",
        "40": "Zr",
        "41": "Nb",
        "42": "Mo",
        "43": "Tc",
        "44": "Ru",
        "45": "Rh",
        "46": "Pd",
        "47": "Ag",
        "48": "Cd",
        "49": "In",
        "50": "Sn",
        "51": "Sb",
        "52": "Te",
        "55": "Cs",
        "56": "Ba",
        "72": "Hf",
        "73": "Ta",
        "74": "W",
        "75": "Re",
        "76": "Os",
        "77": "Ir",
        "78": "Pt",
        "79": "Au",
        "80": "Hg",
        "81": "Ti",
        "82": "Pb",
        "83": "Bi",
        "84": "Po",
    }
    return atom_dict[atom_num]


def render_image(cubefile, jmolfile):
    print("Generating image corresponding to file:  " + cubefile)
    lines = read_lines(jmolfile)
    f = open("jmol.spt", "w")
    for line in lines:
        if "%full_file_dir" in line:
            f.write(line.replace("%full_file_dir", os.getcwd() + "/" + cubefile))
        elif "%image_file" in line:
            f.write(line.replace("%image_file", cubefile.split(".")[0] + ".png"))
        else:
            f.write(line)
    f.close()
    if not os.path.isdir("orb_images"):
        os.makedirs("orb_images")
    os.chdir("orb_images")
    input0 = "/home/stvogt/.jmol/jmol.sh -n -s ../jmol.spt"
    print(os.getcwd())
    print(input0)
    job0 = subprocess.getstatusoutput(input0)
    os.chdir("../")


def fchk_gen(chk_folder):
    for file_ in os.listdir(chk_folder):
        print("Generating formated checkpoint file for:  " + file_)
        input0 = "formchk " + chk_folder + "/" + file_
        print(input0)
        job0 = subprocess.getstatusoutput(input0)


def cube_files(orb_range, atom_list, lines):
    print("HERE")
    if os.path.isdir("CHK"):
        f = open("cube.log", "w")
        f.write("Log file for cube generation\n\n")
        if not os.path.isdir("cubes"):
            os.makedirs("cubes")
        # fchk_gen("CHK/")
        for file_ in os.listdir("CHK"):
            print("generating checkpoint file for:  " + file_)
            input0 = "formchk " + "CHK/" + file_
            print(input0)
            job0 = subprocess.getstatusoutput(input0)
            os.chdir("cubes")
            print("Entering this directory --> " + os.getcwd())
            fchk = "../CHK/" + file_.split(".")[0] + ".fchk"
            cube_output = file_.split(".")[0] + ".cub"
            generate_cubes(orb_range, fchk, cube_output, lines)
            print("ordering orbital cubes into directories")
            for i in orb_range:
                if not os.path.isdir("orbitals_" + str(i)):
                    os.makedirs("orbitals_" + str(i))
                os.chdir("orbitals_" + str(i))
                original = "../orbitals_" + str(i) + "_" + file_.split(".")[0] + ".cub"
                destiny = "orbitals_" + str(i) + "_" + file_.split(".")[0] + ".cub"
                if os.path.isfile(original):
                    shutil.move(original, destiny)
                else:
                    print(
                        "Cube file "
                        + original
                        + " not found, please check your checkpoint file"
                    )
                    f.write(
                        "Cube file "
                        + original
                        + " not found, please check your checkpoint file\n"
                    )
                os.chdir("../")
            os.chdir("../")
        f.close()

    else:
        print("No checkpoint folder CHK!")
        sys.exit(1)


def generate_cubes(orbitals, fchk, cube_output, lines, sq=False):
    count = 0
    orb_name = []
    for i in orbitals:
        print("Genrating cube for orbital number: " + str(i))
        cub_i = "orbitals_" + str(i) + "_" + cube_output
        orb_name.append(cub_i)
        input1 = "cubegen 0 MO=" + str(i) + " " + fchk + " " + cub_i + " 0 h"
        print(input1)
        job1 = subprocess.getstatusoutput(input1)
