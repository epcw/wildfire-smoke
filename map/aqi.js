// set the dimensions and margins of the graph
var margin = {top: 20, right: 30, bottom: 30, left: 40},
    w = 1000,
    h = 1101;

// set-up unit projection and path
var projection = d3.geo.mercator()
    .scale(1)
    .translate([0, 0]);

var path = d3.geo.path()
    .projection(projection);

// append the svg object to the body of the page
var svg = d3.select("#mapdiv")
  .append("svg")
    .attr("id","map")
    .attr("width", w + margin.left + margin.right)
    .attr("height", h + margin.top + margin.bottom)
  .append("g")
    .attr("id", "contour_map")
    .attr("transform",
          "translate(" + margin.left + "," + margin.top + ")");

// set-up scale for colour coding contours
var cScale = d3.scale.linear()
    .domain([0, 1]);

const max_lat = 48
const min_lon = -123
const min_lat = 47
const max_lon = -122

d3.json("/aqi/map/seattle_contours_simplified.json", function(error, puget_sound) {
  if (error) return console.error(error);

  var bTopo = topojson.feature(puget_sound, puget_sound.objects.seattle_contours),
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

    svg.selectAll("path")
        .data(topo).enter()
        .append("path")
        .style("fill", "none")
        .style("stroke", function(d, i) {
            return interp(cScale(d.properties.ContourEle));
        })
        .attr("d", path)
        .on("mouseover", highlight) // just a little example of what's available in terms of interaction
        .on("mouseout", function (d,i) {unhighlight(this,d);
        });

});

// function to interpolate between to colours
// see http://stackoverflow.com/questions/12217121/continuous-color-scale-from-discrete-domain-of-strings

function interp(x) {
    var ans = d3.interpolateLab("#ffffe5", "#004529")(x);
    return ans
}
// A simple highlight example
function highlight(x) {

    var s = d3.select(this);

    s.style("stroke", "red");

}
function unhighlight(x,y) {

    var old = y.properties.ELEV;
    var u = d3.select(x);

    u.style("stroke", function(d, i) {
            return interp(cScale(old));
        })
}