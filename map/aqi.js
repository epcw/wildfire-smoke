// set the dimensions and margins of the graph
var margin = {top: 20, right: 30, bottom: 30, left: 40},
    w = 1000,
    h = 1101;

// set-up unit projection and path
const projection = d3.geoMercator()
    .scale(1)
    .translate([0, 0]);

var path = d3.geoPath()
    .projection(projection);

// append the svg object to the body of the page
var svg = d3.select("#mapdiv")
  .append("svg")
    .attr("id","map")
    .attr("width", w + margin.left + margin.right)
    .attr("height", h + margin.top + margin.bottom);

// create contour layer
svg.append("g")
    .attr("id", "contour_map")
    .attr("transform",
          "translate(" + margin.left + "," + margin.top + ")")
    // create background rect
    .append("rect")
    .attr("id","basemap");

// create stations layer
svg.append("g")
    .attr("id","stations")
    .attr("transform",
          "translate(" + margin.left + "," + margin.top + ")");

// set-up scale for colour coding contours
var cScale = d3.scaleLinear()
    .domain([0, 1]);

// bounds of the station data - possibly irrelevant and not getting used right now anyways
//const max_lat = 48
//const min_lon = -123
//const min_lat = 47
//const max_lon = -122

// this is where the timestamp slider function and whatnot goes.
//var time_stamp = 1672617600

// load the station data and map it onto the existing projection defined above
function stations() {
d3.csv("/aqi/map/stations.csv", function(data) {

    svg.select("g#stations")
    .append("g")
    .selectAll("dot")
    .data(data)
    .enter()
    .append("circle")
    .attr("cx", function(d) { var coords = projection([d.longitude, d.latitude]); return coords[0];})
    .attr("cy", function(d) { var coords = projection([d.longitude, d.latitude]); return coords[1];})
    .attr("r", 5)
    .style("fill", function(d) { var aqi = d.pm2_5_AVG; return colorize(aqi)})
    .style("stroke", "#2e2e2e")
    .style("stroke-width", "1")
    .on("mouseover", highlight)
    .on("mouseout", function (d,i) {unhighlight(this,d);
    })

});
}

// function to assign AQI colors per EPA's colorscale
function colorize (aqi) {

    if (aqi < 5) {
        color = "green"
        }
    else if (aqi >= 5 && aqi < 10) {
        color = "yellow"
        }
    else if (aqi >= 10 && aqi < 15) {
        color = "orange"
        }
    else if (aqi >= 15 && aqi < 20) {
        color = "red"
        }
    else if (aqi >= 20 && aqi < 30) {
        color = "purple"
        }
    else if (aqi >= 30 && aqi < 50) {
        color = "#800000"
        }
    // I THINK AQIs above 500 are impossible since it's a 0-500 scale, but just in case there's a weird data blurp, make them black.
    else {
        color = "#000000"
        }
    return color
}

// Make me a contour map WORTHY of Mordor (aka main drawing script)
d3.json("/aqi/map/filtered_seattle_contours.json", function(error, puget_sound) {
  if (error) return console.error(error);

  var bTopo = topojson.feature(puget_sound, puget_sound.objects.filtered_seattle_contours),
        topo = bTopo.features;

    var hRange = d3.extent(topo, function(d, i) {
        return d.properties.ELEV
    });

    cScale.domain(hRange);

    // calculate bounds, scale and transform
    // see http://stackoverflow.com/questions/14492284/center-a-map-in-d3-given-a-geojson-object
    var b = path.bounds(bTopo),
        s = .95 / Math.max((b[1][0] - b[0][0]) / w, (b[1][1] - b[0][1]) / h),
        t = [(w - s * (b[1][0] + b[0][0])) / 2, (h - s * (b[1][1] + b[0][1])) / 2];

    projection.scale(s)
        .translate(t);

    svg.select("g#contour_map").selectAll(".path")
        .data(topo).enter()
        .append("path")
        .style("fill", "none")
        .style("stroke", function(d, i) {
            return interp(cScale(d.properties.ContourEle));
        })
        .attr("d", path);

    // creates placeholder blue rect instead of a real basemap

    var mapwidth = d3.select("#contour_map").node().getBBox().width;
    var mapheight = d3.select("#contour_map").node().getBBox().height;

    svg.select("#basemap")
        .attr("width", mapwidth)
        .attr("height", mapheight)
        .attr("transform",
          "translate(140,28)")
        .attr("fill","#D6EAFF");

    // now add stations: this ensures they get added AFTER the contour map's dimensions are created, since we're mapping the stations onto its lat/lon
        stations();
});

// function to interpolate between two colours
// see http://stackoverflow.com/questions/12217121/continuous-color-scale-from-discrete-domain-of-strings
function interp(x) {
    var ans = d3.interpolateLab("#ffffe5", "#004529")(x);
    return ans
}
// A simple highlight example
function highlight(x) {

    var s = d3.select(this);

    s.attr("r", 15)
    .style("stroke", "#39ff14")
    .style("stroke-width","5");

    s.raise();
}
function unhighlight(x,y) {

//    var old = y.properties.ContourEle; // not using right now, legacy from the contour coloring
    var u = d3.select(x);

//    u.style("stroke", function(d, i) {
//            return interp(cScale(old));
//        })
      u.attr("r", 5)
      .style("stroke","#2e2e2e")
      .style("stroke-width",1);
}