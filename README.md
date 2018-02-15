# Exploratory Analyses of Lighting and Crime in DC

There have been a number of studies of the deterrent effects of lighting on crime, most notably a large-scale experiment in New York City. 
This project seeks to exploit a kind of natural experiment by examining crime in close proximity to street lights before andA the week after they have been repaired. 

## Initial Analyses
The simplest analysis we can conceive is simply examining crime the week before and the week after a repair. This will require (1) goecoding the crime data; (2) geocoding lighting; (3) drawing some reasonable polygon -- perhaps a circle or perhaps a city block) around each light; (4) joining the lighting polygons with the crime data surrounding each light for the week prior to and following the repair. 

## Further Analyses
We could add more variables (time of day, day of week, holidays, weather conditions, neighborhood demographics, etc.) to measure the relative impact of lighting across heterogenous conditions. We could model the effects of lighting density across the city to see where adding more lighting could have the largest impact on crime. 

## Tools
We'll explore the data using geopandas, postgis, statsmodels, and sklearn. 

## Data Sources

Streetlights: 
 - https://opendata.arcgis.com/datasets/6cb6520725b0489d9a209a337818fad1_90.geojson
We want:
- wattage
- pole height
- number of arms
- active status and why
- type of pole
- type of light
- arms
 
Crime: 
 - 2018: https://opendata.arcgis.com/datasets/38ba41dd74354563bce28a359b59324e_0.geojson
 - 2017: https://opendata.arcgis.com/datasets/6af5cb8dc38e4bcbac8168b27ee104aa_38.geojson
 - 2016: https://opendata.arcgis.com/datasets/bda20763840448b58f8383bae800a843_26.geojson
 - 2015: https://opendata.arcgis.com/datasets/35034fcb3b36499c84c94c069ab1a966_27.geojson
 - 2014: https://opendata.arcgis.com/datasets/6eaf3e9713de44d3aa103622d51053b5_9.geojson
 - 2013: https://opendata.arcgis.com/datasets/5fa2e43557f7484d89aac9e1e76158c9_10.geojson
 - 2012: https://opendata.arcgis.com/datasets/010ac88c55b1409bb67c9270c8fc18b5_11.geojson
 - 2011: https://opendata.arcgis.com/datasets/9d5485ffae914c5f97047a7dd86e115b_35.geojson
 - 2010: https://opendata.arcgis.com/datasets/fdacfbdda7654e06a161352247d3a2f0_34.geojson

We want:
- Time of day
- indoor/outdoor (dont have)
- offense

Cityworks Service Requests:
Comes in from citizens or possibly DoT when doing monthly inspection.
 - 2010 https://opendata.arcgis.com/datasets/ba150a4170bc484b8cc204be308fa70c_1.geojson
 - 2011 https://opendata.arcgis.com/datasets/310e9e84ad7f4af7a31e7115395d7b57_2.geojson
 - 2012 https://opendata.arcgis.com/datasets/65a81d0a91654b9692c08ca37809c3c3_3.geojson
 - 2013 https://opendata.arcgis.com/datasets/20dc3ba98d494e51bee18a42f8430824_4.geojson
 - 2014 https://opendata.arcgis.com/datasets/17cafb3ffab347409def7e85e14c56bd_5.geojson
 - 2015 https://opendata.arcgis.com/datasets/b93ec7fc97734265a2da7da341f1bba2_6.geojson
 - 2016 https://opendata.arcgis.com/datasets/0e4b7d3a83b94a178b3d1f015db901ee_7.geojson
 - 2017 = "https://opendata.arcgis.com/datasets/19905e2b0e1140ec9ce8437776feb595_8.geojson
 
Cityworks Work Orders: 
Creates workorder for repeair.
 - https://opendata.arcgis.com/datasets/a1dd480eb86445239c8129056ab05ade_0.geojson
 
