## Introduction: Get acquainted with the data, and focus the project

The U.S. Department of Agriculture maintains a [National Agriculture Imagery Program (NAIP)](https://www.fsa.usda.gov/programs-and-services/aerial-photography/imagery-programs/naip-imagery/) that takes 1m-resolution aerial imagery of agricultural and urban regions across the country.  This dataset offers a wonderful opportunity for researchers and curious citizens to examine how their rural and urban spaces are changing with the passage of time.  In some cases, historic data is available dating back as far as the mid-1950s.  While much of the older data is locked up on microfilm, data from recent years (2012-2015) is more readily accessible in digital format.  Amazon Web Services, for example, has recently made a number of large-scale datasets, including the most recent NAIP data, available in a [publicly-accessible S3 repository](https://aws.amazon.com/public-datasets/naip/).  These images are available as georectified .TIF files, each about 160-170 MB in size.

This project takes advantage of the convenience of Amazon’s public datasets' NAIP image repository, and provides a basic approach to leveraging these NAIP images in order to perform supervised classification of land usage and do some very basic analysis of rural/urban development over time.  This project outlines a workflow, supported by Python scripting, that aids the user in performing supervised image classification on NAIP raster imagery.  All of the tools required for this kind of supervised classification task are already available as free/open source software; this project's primary aim, then, is simply to provide scripts and other processing aids that make the task of NAIP raster classification and analysis slightly easier for the user to manage in bulk.  The sections of this write-up will provide an overview of each step of the workflow, a description of the tools used, along with some code snippets and comments.  Ultimately, this process is a lot like 'painting by numbers' in reverse: the user can train an algorithm to recognize specific types of land usage, and have the computer assign classification numbers to regions of a raster based on which land use is likely to be present.


### A note about speed and project focus

One of the biggest difficulties of raster classification and analysis is the sheer computational power it requires to process high-resolution imagery at scale.  NAIP data is organized into "quads" that are 3.75 x 3.75 minutes in dimension (or about 7km x 7km at the Twin Cities' latitude).  NAIP data is also tiled very precisely, in a format that remains consistent from from year to year.  A user's particular feature of interest may span multiple tiles (ex: rivers, metropolitan areas), or may be contained within a single file (ex: neighborhoods, small lakes).  Project compute time can vary, then, depending on how many tiles need to be processed to address a particular question at hand.  

The steps discussed in this write-up were tested on a MacBook Pro (8GM memory, 2.9 GHz Intel Core i5 processor) and an Ubuntu 16.04 installation running in Parallels on the same computer.  The code and steps outlined in this project, then, can be performed by a user equipped with a reasonably up-to-date home laptop, but may require some patience, and a willingness to scale back to smaller areas of analysis that encompass only a few NAIP "quads".

For this demo project, I had initially hoped that this I could examine the entire Twin Cities metro region.  I discovered over the course of my research that this region comprises just over 50 NAIP quad images, and the compute time for a project of that scale became prohibitively long for a user working on a home laptop.  I ultimately had to scale back a bit, and chose instead to develop a supervised classification workflow using 4 specific NAIP quads comprising the region where the Twin Cities Metro Transit Green Line is located.  The NAIP years I examine here are 2013 and 2015, which nicely bookend the opening of the Metro Transit Green Line, which officially started running in June of 2014.  In the discussion surrounding the construction of the Green Line, residents expressed varying degrees of curiosity and concern about the impact this construction could have on the surrounding neighborhoods and businesses (see, for example, [Melo, 2016](http://www.twincities.com/2016/06/17/the-green-line-is-2-years-old-what-has-it-accomplished/)).  Examining the NAIP imagery surrounding this important civic construction event, then, may offer an interesting "pre-" and "post-" comparison opportunity to help residents understand how this transit project is shaping the land use in their neighborhoods.

### So, what's the point?

Ultimately, the workflow outlined in this project that I will use to examine the Twin Cities Metro Transit Green Line should be generalizable enough that it can be applied to other scenarios, bringing the user several steps closer to addressing questions like:

* What areas of the metro region have seen the most change in their built spaces in recent years?

* How has the mix between agricultural and urban areas been changing in recent years?

* Can we detect any interesting patterns of land use that seem to characterize “urbanization” or “agriculturalization”?