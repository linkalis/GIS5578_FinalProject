## Part 0: Tools setup

One of the more difficult hurdles for this project was choosing among various tools and setup options, and getting all of the tools to run and connect to each other effectively.  Below, I offer some step-by-step instructions on the trickier tasks required to get these tools to run, in the hopes of sparing future users some time and headaches.  These steps assume the user is working on a Mac computer, and has access to Parallels desktop virtualization software.  Windows users should find decent documentation online for some of these setup steps, as well.


### A note on Python bindings, Mac, and Ubuntu

Most of the raster classification tasks in this project leverage Orfeo Toolbox, which is a C++ library that offers Python bindings so its toolkit can be invoked in via Python.  Unfortunately, getting Python to _find_ these bindings can cause a lot of head scratching.  Some of this has to do with the fact that Mac computers feature a pre-installed, system version of Python that is somewhat limited in is execution permissions, and that can sometimes crop up in the midst of the setup process and cause a lot of confusion when trying to set Python paths and expose bindings.  

In general, then, it seems to be a common recommendation among online forums that users bypass this system Python altogether and run Python in a different way.  To mitigate some of this confusion between Python versions on Mac, I recommend installing a clean version of Ubuntu 16.04 using Parallels for Mac and working within that environment for processing tasks.  This keeps things a little cleaner, and nicely isolates the batch processing workflows into an Ubuntu environment that could eventually be more readily deployed on a more powerful computing cluster, if the user has access to these resources, as they often rely on Linux-based machines.


### Anaconda setup (version 4.3.1, Python 2.7; installed on Ubuntu 16.04 running on Mac Parallels)

What is Anaconda? And why? Anaconda is a version of Python that bundles a lot of standard modules--like numpy, pandas, etc.--together in one easy-to-install package. It provides a good set of base tools on top of which we can run Orfeo Toolbox without having to install each dependency separately.

1. Download Anaconda 2.7 (version 4.3.1) from: https://www.continuum.io/downloads. Save the installer to your home directory. _Note:_ We need to use Python version 2.7, because Orfeo Toolbox does not currently support Python 3+.

2. Open up the Terminal to your home directory. Install Anaconda by typing the following command: `bash Anaconda2-4.3.1-Linux-x86_64.sh `

3. Review the license agreement, and type 'yes' to accept.  Allow Anaconda to install to the default location.  This will install Anaconda to the user's home directory, under a folder called 'anaconda2' (ex: `/home/<username>/anaconda2`).

3. Set Anaconda as the default Python version to use on your system. By default, Anaconda should prompt you: `Do you wish the installer to prepend the Anaconda2 installation location to PATH in your /home/<username>/.bashrc?`. Type 'yes' to add Anaconda to your user's PATH.

4. Close and reopen the Terminal to refresh the installation changes. To verify that Anaconda is now your default Python version, run the following command: `echo $PATH`.  You should see '/home/<username>/anaconda2/bin' as the first item listed in your path.  This indicates that Anaconda will run as your default Python version.  You can also launch python from the Terminal by typing `python` and hitting [ENTER].  There you should see `Python 2.7.13 |Anaconda custom (64-bit)` listed as your Python version.


### Amazon Web Services (AWS) S3 credentials setup

To download NAIP imagery from AWS, there are a few brief setup steps required to be able to access Amazon's public datasets hosted in S3 buckets:

1. If you don't have an Amazon account, create one.  Then, log into the Amazon Web Services console at: https://aws.amazon.com

2. Once you're logged into AWS, go to the IAM Management Console.  Here, you'll create a separate user with minimal access permissions that you can use to credential yourself in order to access Amazon's public S3 buckets.

3. Click 'Add User', then type in a username you'll remember (ex: 'my-public-s3-user'). Check the box to give the user 'Programmatic Access'.

4. Next, you'll need to set up your user's permissions.  Choose the option to attach existing Amazon permissions policies, then search for the 'AmazonS3ReadOnlyAccess' permission and check the box to assign that permission to your new user.

5. Finally, finish by creating your user.  Once your user is successfully created, download the .CSV file containing the user's access key ID and secret.

6. Create a hidden folder called '/.aws' in the home directory on your computer by executing the command: `sudo mkdir ~/.aws`. Then, copy the credentials file into this folder.  (Note: For more information on setting up your credentials file, see Amazon's [boto3 documentation](http://boto3.readthedocs.io/en/latest/guide/quickstart.html).)

7. Finally, install Amazon's Python toolkit, called 'boto3' by running the following command in the Terminal: `pip install boto3`


### Orfeo Toolbox setup (version 5.10.1; installed on Ubuntu 16.04 running on Mac Parallels)

Why Orfeo Toolbox? This is a powerful library that offers a number of training and classification algorithms tailored for processing common GIS filetypes (.TIF, .SHP) and preserving geometadata information in the process.

1. Make sure libexpat is installed by executing the following command in the Terminal: `sudo apt-get install libexpat1-dev`

2. Download Orfeo Toolbox for Linux from the Orfeo website: https://www.orfeo-toolbox.org/download/. Save the file to your home directory.

3. Open up the Terminal to your home directory, and make sure the file is executable by executing the following command: `chmod +x OTB-5.10.1-Linux64.run`

4. Install Orfeo Toolbox with the following command: `./OTB-5.10.1-Linux64.run`

5. At this point, Orfeo Toolbox is installed, but this still doesn't guarantee that Python/Anaconda will be able to find the Orfeo Toolbox Python bindings that will allow you to use Orfeo Toolbox from within Python. To fix this, you will need to create a path file called `orfeo_toolbox.pth` that sits inside of your Anaconda Python installation and points towards the install location of Orfeo Toolbox. To set this up:

a. From the Terminal, navigate to the site-packages folder in your anaconda2 installation: `cd /home/<username>/anaconda2/lib/python2.7/site-packages`.  

b. From within the site-packages folder, create a file called orfeo_toolbox.pth and open it up for editing: `sudo nano orfeo_toolbox.pth`.  

c. Finally, copy the following line into the orfeo_toolbox.pth file: `/home/<username>/OTB-5.10.1-Linux64/lib/python`.  Then, [CTRL] + [X] to save the file and exit the text editor.  

When you're finished, any time you launch Python/Anaconda, Python will know where to find the bindings for your Orfeo Toolbox installation.

6. Now, you can test whether the Orfeo Toolbox Python bindings are working. From the Terminal, launch python by typing `python` and hitting [ENTER]. Then, at the Python prompt, type `import otbApplication`.  If you don't see an error, the Python bindings should be working properly.
