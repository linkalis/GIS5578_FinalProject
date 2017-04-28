import os
import glob
import time

# Set the OTB_APPLICATION_PATH environment variable to point to where our OTB applications
# are installed so Python can invoke them
os.environ["OTB_APPLICATION_PATH"] = "/home/linkalis/OrfeoToolbox/OTB-5.10.0-Linux64/lib/otb/applications"

# Import Orfeo Toolbox via Python bindings
import otbApplication


def argument_parser():
    '''
    Parse arguments and return
    '''
    import argparse
    parser = argparse.ArgumentParser(description= "Use Orfeo Toolbox to compute image statistics on a directory of .TIF files; output .XML file with computed statistics")
    parser.add_argument("--indir", required=True, help="The directory that contains the .TIF files you want to compute statistics on", dest="indir")
    parser.add_argument("--outdir", required=True, help="The directory where you want to save the .XML file containing the computed statistics", dest="outdir")
    return parser


def main(indir, outdir):
    # If user forgot to put trailing slashes at the end of their indir and outdir,
    # add those or we may accidentally try to read from or save to an invalid directory!
    if indir[-1:] != "/":
        indir = indir + "/"

    if outdir[-1:] != "/":
        outdir = outdir + "/"

    # Check if target save directory exists; if not, warn the user and exit
    if os.path.exists(outdir):
        start_time = time.time() # Start the clock

        # Create an instance of the ComputeImagesStatistics application
        ComputeImagesStatistics = otbApplication.Registry.CreateApplication("ComputeImagesStatistics")

        # Get the list of all files in the input directory that end in .tif
        files_list = glob.glob(indir + "*.tif")
        #print files_list

        # Set application parameters
        ComputeImagesStatistics.SetParameterStringList("il", files_list)
        ComputeImagesStatistics.SetParameterString("out", outdir + "image_stats.xml")

        # Execute the application
        ComputeImagesStatistics.ExecuteAndWriteOutput()

        end_time = time.time() # Stop the clock
        elapsed_time = end_time - start_time

        print "Finished computing image statistics. File saved as 'image_stats.xml' to: " + outdir
        print "Elapsed time: " + str(elapsed_time)
    else:
        print "Sorry! Couldn't find target save directory. Please check your --outdir argument and try again."
        return


if __name__ == '__main__':
    args = argument_parser().parse_args()

    main(args.indir, args.outdir)
