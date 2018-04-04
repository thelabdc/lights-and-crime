# Exploratory Analyses of Lighting and Crime in DC

There have been a number of studies of the deterrent effects of lighting on crime, most notably a large-scale experiment in New York City. 

This project seeks to exploit a kind of natural experiment by examining crime in close proximity to street lights before and after they have been repaired. 

## Initial Analyses
The simplest analysis we can conceive is simply examining crime the week before and the week after a repair. This will require (1) goecoding the crime data; (2) geocoding lighting; (3) drawing some reasonable polygon -- perhaps a circle or perhaps a city block) around each light; (4) joining the lighting polygons with the crime data surrounding each light for the week prior to and following the repair.  More sophisticated analyses will include standard statististical analyses and, possibly, machine learning analyses to predict where improved or upgraded lighting could do the most good. 

## Data Sources

Happily, DC maintains a great deal of open data about streetlight locations and crimes known to MPD. 

Streetlight repair data spans two data sources: the current CityWorks workorder management data system that DC adopted in 2016, and the now-retired iSlims work order management system that managed work orders prior to Cityworks. CityWorks data is available via a public API, and DDOT has generously provided us with access to data from the retired iSlims system. 

Streetlights: 
- location and features [information](http://opendata.dc.gov/datasets/street-lights) & [geojson](https://opendata.arcgis.com/datasets/6cb6520725b0489d9a209a337818fad1_90.geojson)
 - CityWorks service requests [information](http://opendata.dc.gov/datasets/cityworks-service-requests) & 
[geojson](https://opendata.arcgis.com/datasets/a1dd480eb86445239c8129056ab05ade_0.geojson)
 - CityWorks work orders [information](http://opendata.dc.gov/datasets/cityworks-workorders) & [geojson](https://opendata.arcgis.com/datasets/a1dd480eb86445239c8129056ab05ade_0.geojson)
- iSlims Work Orders: available in the data subfolder. (We know, we know, but it's not big and until we get it up on the open data portal, this is just the easiest thing to do.)

Crime: 

Public crime data, although exluding some offenses such as sexual assaults, is fairly extensive and includes many common offenses that one would expect to be influenced by lighting if lighting were to have an effect (theft from auto, robbery, assault, etc.). 

 - 2017 [information](http://opendata.dc.gov/datasets/crime-incidents-in-2017) & [geojson](https://opendata.arcgis.com/datasets/6af5cb8dc38e4bcbac8168b27ee104aa_38.geojson)
 - 2016 [information](http://opendata.dc.gov/datasets/crime-incidents-in-2016) & [geojson](https://opendata.arcgis.com/datasets/bda20763840448b58f8383bae800a843_26.geojson)
 - 2015 [information](http://opendata.dc.gov/datasets/crime-incidents-in-2015) & [geojson](https://opendata.arcgis.com/datasets/35034fcb3b36499c84c94c069ab1a966_27.geojson)
 - 2014 [information](http://opendata.dc.gov/datasets/crime-incidents-in-2014) & [geojson](https://opendata.arcgis.com/datasets/6eaf3e9713de44d3aa103622d51053b5_9.geojson)
 - 2013 [information](http://opendata.dc.gov/datasets/crime-incidents-in-2013) & [geojson](https://opendata.arcgis.com/datasets/5fa2e43557f7484d89aac9e1e76158c9_10.geojson)
 - 2012 [information](http://opendata.dc.gov/datasets/crime-incidents-in-2012) & [geojson](https://opendata.arcgis.com/datasets/010ac88c55b1409bb67c9270c8fc18b5_11.geojson)
 - 2011 [information](http://opendata.dc.gov/datasets/crime-incidents-in-2011) & [geojson](https://opendata.arcgis.com/datasets/9d5485ffae914c5f97047a7dd86e115b_35.geojson)
 - 2010 [information](http://opendata.dc.gov/datasets/crime-incidents-in-2010) & [geojson](https://opendata.arcgis.com/datasets/fdacfbdda7654e06a161352247d3a2f0_34.geojson)
