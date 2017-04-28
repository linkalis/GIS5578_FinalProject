## Conclusion: Identifying changes, confusion, and next steps

### Preview classified images in QGIS

Now that our model is trained and the NAIP raster images are classified, we can finally get a look at how our predicted land usage classes are distributed across the rasters, and examine how these uses may have change between the two years in our datasets.

To help streamline the previewing process, I've created one final QGIS helper script: first load all of the classified raster images as layers into QGIS, then you can run the `QGIS_StyleRaster.py` script (located in the `QGIS_Scripts` folder of this write-up).  Simply open this script up in the QGIS Python console, click the "play" button, and the script will automatically apply the same color styles used for labeling regions of interest to the classes present in the newly-classified raster file.  Instantly, we get a nice rainbow of classifications to preview.

Here's what the land use classes look like for 2013 for the target region around the Metro Transit Green Line:

![NAIP classified four quads for 2013](/img/NAIP_classified_2013.png)

And here's what the classes look like for 2015:

![NAIP classified four quads for 2015](/img/NAIP_classified_2015.png)


### Identifying major changes

So now the question is: what seems to have changed in these images between 2013 and 2015?  One relatively effective--albeit somewhat "manual"--way of identifying places where change has occurred is simply to toggle back and forth between the layers in QGIS, inspecting the land use classifications visually.  Because they are styled in bright colors, and are simplified to just eight classes, changes jump out at the viewer much more prominently than if we were examining the original NAIP images themselves.

We need to keep in mind that these classifications are merely the computer's best attempt, based on the human-provided region of interest classification labels, to guess at the land use for each pixel in the NAIP rasters along the Metro Transit Green Line corridor and in the Minneapolis and St. Paul downtown regions.  There is still a lot of "noise" in these classifications, but nevertheless we can see that there _are_ some land usage changes that seem to get correctly identified, and that show some semblance of change.  Let's look at a few examples:

**Example 1:** I-35E construction north of St. Paul

Between 2013 and 2015, road work was being done on highway I-35E just north of downtown St. Paul:

![I-35E NAIP images unclassified](/img/NAIP_change_example_1.gif)

A closer look at the classified images reveals that a lot of the dirt from construction that was present in the 2013 image has been converted into asphalt roadbed and driveways in the 2015 image:

![I-35E NAIP images classified](/img/NAIP_change_example_1_classified.gif)


**Example 2:** The disappearing baseball field

In one of the neighborhoods just south of the light rail, it appears that a baseball field has been dismantled and is being turned into a construction zone:

![disappearing baseball field NAIP images unclassified](/img/NAIP_change_example_2.gif)

I wouldn't have discovered this change, if the sudden prominence of dirt in this region in the 2015 classified image hadn't been so obvious when skimming over the image with the naked eye:

![disappearing baseball field NAIP images classified](/img/NAIP_change_example_2_classified.gif)

**Example 3:** Powderhorn lake algae problem

And finally, since I had discovered so much algae in the metro lakes during the labeling phase of the workflow, that led me to wonder: are there any lakes that seem to have developed a major algae problem during this time period?  As it turns out, Powerderhorn Park lake has some history of ongoing attempts to clean up its algae problem (see [Marcotty, 2012](http://www.startribune.com/powderhorn-lake-scrubs-out-pollution/171245271/)):

![algae problem NAIP images unclassified](/img/NAIP_change_example_3.gif)

Unfortunately, the situation seems to have gotten _worse_ in the years between 2013 and 2015, not better.  It was toggling back and forth between the classified rasters that made this change so apparent to the naked eye:

![algae problem NAIP images classified](/img/NAIP_change_example_3_classified.gif)


### Examine the confusion matrix

In examining the classified rasters, however, it quickly becomes obvious that the classes sometimes get "confused" with each other.  For example, buildings are often classified as asphalt, and vice-versa.  This is likely because a lot of building roofs are lined with asphalt-like materials.  Similarly, a lot of grassy park areas are classified as agricultural areas.  This likely has to do with the fact that the agricultural areas I labeled during the training process generally featured short foliage/greenery that is very similar to grass.  In fact, in some cases I suspect I labeled as "agricultural" areas that were lying fallow and left to grow over in grass to rejuvenate for the next growing season.  These kinds of confusion in the classifications are a good illustration that a classification model is only as good as the information that is used to train it.  Any laziness or uncertainty on the part of the human "supervisor" when labeling classes--and believe me, there were plenty of confused "judgement calls" I made when classifying--gets translated into poorer model performance down the road.

Fortunately, we can quantify the extent of this confusion using the confusion matrix output during the model training process.  Let's examine the confusion matrices for each of the models to see what they might suggest about our model performance...

Confusion matrix for 2013 training set:
```
      [0]  [1]  [2]  [3]  [4]   [5] [6]  [7]  [8]
[ 0] 5067  104  159   49    0    0   14    6  146
[ 1]  235 3601 1338   72    0    0    4  297    0
[ 2]  160 1133 3825   47    0    1    8  369    2
[ 3]    7  125    3 5394    0   18    0    0    0
[ 4]    0    0    0    0 4510  338  676    0   22
[ 5]    2    0    0    0  341 5174   23    0    4
[ 6]    2    0    1    0 1193   71 4232   10   37
[ 7]    7  281  851   17    0    4   41 4342    2
[ 8]   79    0    0   15  126   11   72    0 5244
```

Confusion matrix for 2015 training set:
```
      [0]  [1]  [2]  [3]  [4]  [5]  [6]  [7]  [8]
[ 0] 5122  149  620   84    1   11   91  363    5
[ 1]  118 4902 1002   19    4    2   17  378    3
[ 2]  278 2108 2356   13    2   12   64 1613    0
[ 3]    4    0    0 6434    0    3    0    2    2
[ 4]    6    0    0    4 4591  781  823    1  239
[ 5]    8    0    0   58 1052 5159   59    1  109
[ 6]   15    0    0    2 1455  114 3975  355  530
[ 7]   56  542 1085   47   20   27  657 4007    3
[ 8]   32    0    0   17  135   95  130    0 6037
```

The row labels of the confusion matrices represent the true labels for the classes, as labeled by the human user.  The column labels of the matrices represent the labels generated by the model.  An "ideal" matrix with a perfectly accurate model would have all values perfectly classified down the diagonal of the matrix, with zeroes in every other cell outside of the diagonal.  Any time, then, that we see values that are non-zero that occur outside of the diagonal of the confusion matrix, it suggests that the model is having trouble discerning differences between classes.  

Both of these matrices suggest, that our models are commonly confusing two classes--class 1 (asphalt) and class 2 (buildings)--as we suspected from visual inspection of the classified images.  Similarly, class 4 (grass), 5 (trees), and 6 (agriculture) sometimes appear to be misclassified amongst each other.  The best-performing classes appear to be class 3 (water) and class 8 (algae), as they are only rarely confused with other classes.


### Limitations, lessons learned, and next steps

There are a number of things I could do to improve model performance, if I were to go through another iteration of the model training workflow.  Some helpful improvements, for example, might be:

* Allow less 'noise' when labeling features. I was somewhat lazy about zooming in close at the pixel level and making sure my feature boundaries coincided exactly with the pixel outlines in the original raster images.  On a second iteration, I could be much more precise in the approach.

* Label more images from each dataset.  In this demo, I only chose three random images from each dataset (2013 and 2015) for labeling and training.  Labeling more images would allow more land use variations to surface in the training images, and may help tease out some additional nuances in the model.

* Label more features within the classes that were most commonly confused.  Asphalt and buildings, in particular, could be good candidates for classes that could use more precise labeling, and a greater number of labeled features.  Being more deliberate in picking buildings with varying roof types, and labeling more roadbeds with varying asphalt types, may help surfance more distinction between the classes.  Unfortunately, if a number of buildings in the training are roofed with asphalt, then the model may ultimately not be able to decipher well between these two classes, and an additional algorithm or other creative segmentation approach may be necessary (see [Pelletier, 2014](https://www.youtube.com/watch?v=TpuV7DT6seI)).

* Finally, I would like to figure out what to do with shadows.  These were commonly getting misclassified as "water" or "other" in the classified rasters.  To mitigate this, I suspect I may need to include an entirely separate class for "shadows", and label those directly as separate regions of interest.  Unfortunately, this may mean that we cannot access much information on what land use classes lie _beneath_ the shadows, but adding shadows as a separate class unto itself could at least avoid having these shadows lead to misclassification and "muddying up" the other classes.

Ultimately, one of the biggest lessons learned in this project is that _timing is critical_!  At the outset of this project, I had originally hoped to be able to analyze a much larger region, and to try to spend some time developing tools and tricks for analyzing changes in land use over time.  Unfortunately, the supervised labeling, training, and classification process took _far_ too long to leave me much time for anything else.

Fortunately, what I'm left with at this point is a very valuable data product: NAIP rasters for the areas surrounding the Metro Transit Green Line, taken from 2013 and 2015 image captures, and classified by probable land usage categories.  The questions we can ask of these rasters are endless!  My hope now is to spend some additional time figuring out ways to make the change detection process less manual, and leverage Python scripting for some basic comparisons.  I have been intrigued by a few, relatively straightforward approaches to change detection (see Singh, 1989) that seem like they would be easy to implement with a combination of numpy and GDAL.  Moving forward, I hope to create some additional scripts that will allow for different approaches to identifying, slicing, and dicing up the probable land use changes between classified NAIP images captured across years.
