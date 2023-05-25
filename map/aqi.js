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

// tooltip div
d3.select('body').append('div').attr('id', 'tooltip').attr('style', 'position: absolute; opacity: 0;');
d3.select('body').append('div').attr('id', 'tooltip2').attr('style', 'position: absolute; opacity: 0;');
d3.select('body').append('div').attr('id', 'tooltip3').attr('style', 'position: absolute; opacity: 0;');

const zoom = d3.zoom()
    .scaleExtent([1,40])
    .on("zoom",function () {svg.attr("transform", d3.event.transform)});

// append the svg object to the body of the page
var svg = d3.select("#mapdiv")
  .append("svg")
    .attr("id","map")
    .attr("width", w + margin.left + margin.right)
    .attr("height", h + margin.top + margin.bottom)
//    .call(d3.zoom().on("zoom", function () {svg.attr("transform", d3.event.transform)}))
    .call(zoom)
    ;

function zoomed({transform}) {
    g.attr("transform", transform);
  }
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
function time_convert (time_stamp) {
// initialize new Date object
var date_ob = new Date(time_stamp * 1000);
var year = date_ob.getFullYear();
var month = ("0" + (date_ob.getMonth() + 1)).slice(-2);
var day = ("0" + date_ob.getDate()).slice(-2);
var date_human = (year + "-" + month + "-" + day)
return date_human
}

// translate pm2.5 to AQI
function aqiFromPM(pm) {
    if (isNaN(pm)) return "-";
    if (pm == undefined) return "-";
    if (pm < 0) return pm;
    if (pm > 1000) return "-";
    /*                                  AQI         RAW PM2.5
    Good                               0 - 50   |   0.0 – 12.0
    Moderate                          51 - 100  |  12.1 – 35.4
    Unhealthy for Sensitive Groups   101 – 150  |  35.5 – 55.4
    Unhealthy                        151 – 200  |  55.5 – 150.4
    Very Unhealthy                   201 – 300  |  150.5 – 250.4
    Hazardous                        301 – 400  |  250.5 – 350.4
    Hazardous                        401 – 500  |  350.5 – 500.4
    */
    if (pm > 350.5) {
        return calcAQI(pm, 500, 401, 500.4, 350.5); //Hazardous
    } else if (pm > 250.5) {
        return calcAQI(pm, 400, 301, 350.4, 250.5); //Hazardous
    } else if (pm > 150.5) {
        return calcAQI(pm, 300, 201, 250.4, 150.5); //Very Unhealthy
    } else if (pm > 55.5) {
        return calcAQI(pm, 200, 151, 150.4, 55.5); //Unhealthy
    } else if (pm > 35.5) {
        return calcAQI(pm, 150, 101, 55.4, 35.5); //Unhealthy for Sensitive Groups
    } else if (pm > 12.1) {
        return calcAQI(pm, 100, 51, 35.4, 12.1); //Moderate
    } else if (pm >= 0) {
        return calcAQI(pm, 50, 0, 12, 0); //Good
    } else {
        return undefined;
    }
}

function calcAQI(Cp, Ih, Il, BPh, BPl) {
    var a = (Ih - Il);
    var b = (BPh - BPl);
    var c = (Cp - BPl);
    return Math.round((a/b) * c + Il);
}

// attempt to set a slider to handle dates
const niceFormat = d3.timeFormat("%B %d, %Y");
const dataFormat = d3.timeFormat("%Y-%m-%d"); // MMMM-DD-YY

const startDate = new Date("2017-07-12");
const millisecondsPerDay = 24 * 60 * 60 * 1000;
const lastday = new Date("2023-03-12"); // set manually based on last pull
const availableDays = (lastday.getTime() - startDate.getTime())/ (1000 * 3600 * 24);

d3.select("#date-value").text(niceFormat(startDate));

d3.select("#slider")
  .attr("max", availableDays)
  .on("input", function() {
    var selected_date = new Date(+startDate + (millisecondsPerDay * this.value));
    d3.select("#date-value").text(niceFormat(selected_date));
    // UPDATE LOOP GOES THROUGH HERE FOR THE MAP
    d3.selectAll(".station_circle").remove();
    var slice_date = dataFormat(selected_date);
    stations(slice_date);
  });

// load the station data and map it onto the existing projection defined above
function stations(slice_date) {
d3.csv("/aqi/map/station_list.csv", function(data) {
    console.log(slice_date);

    var dataFilter = data.filter(function(d){ return d.date == slice_date });
    // create data slice HERE

    svg.select("g#stations")
    .append("g")
    .selectAll("dot")
    .attr("class","station_circle")
    .data(dataFilter)
//    .data(data)
    .enter()
    .append("circle")
    .attr("cx", function(d) { var coords = projection([d.longitude, d.latitude]); return coords[0];})
    .attr("cy", function(d) { var coords = projection([d.longitude, d.latitude]); return coords[1];})
    .attr("r", 5)
    .style("fill", function(d) { var aqi = aqiFromPM(d.pm2_5_AVG); return colorize(aqi)})
    .style("stroke", "#2e2e2e")
    .style("stroke-width", "1")
    .on("mouseover", function(d) {
//        highlight();
        var s = d3.select(this);

    s.attr("r", 15)
    .style("stroke", "#39ff14")
    .style("stroke-width","5");

    s.raise();
        var station = d.name; var index = d.station_index; var aqi = aqiFromPM(d.pm2_5_AVG); var date = d.date; var color = colorize(aqi);
//        var station = d.name; var index = d.station_index; var aqi = aqiFromPM(d.pm2_5_AVG); var date = d.time_stamp; var color = colorize(aqi);
        d3.select('#tooltip').transition().duration(200).style('opacity', 1).text(station + " (" + index + ")");
        d3.select('#tooltip2').transition().duration(200).style('opacity', 1).text(date);
//        d3.select('#tooltip2').transition().duration(200).style('opacity', 1).text(time_convert(date));
//        d3.select('#tooltip3').transition().duration(200).style('opacity', 1).style('color', color).text("AQI: " + aqi); // this colors the AQI, but that's hard to read.
        d3.select('#tooltip3').transition().duration(200).style('opacity', 1).text("AQI: " + aqi);
    })
    .on("mouseout", function (d,i) {
    unhighlight(this,d);
       d3.select('#tooltip').style('opacity', 0);
       d3.select('#tooltip2').style('opacity', 0);
       d3.select('#tooltip3').style('opacity', 0);
    })
   .on('mousemove', function() {
   d3.select('#tooltip').style('left', (d3.event.pageX+10) + 'px').style('top', (d3.event.pageY+10) + 'px');
      d3.select('#tooltip2').style('left', (d3.event.pageX+10) + 'px').style('top', (d3.event.pageY+25) + 'px');
         d3.select('#tooltip3').style('left', (d3.event.pageX+10) + 'px').style('top', (d3.event.pageY+40) + 'px');
     })

});
}

// function to assign AQI colors per EPA's colorscale
function colorize (aqi) {

    if (aqi <= 50) {
        color = "green"
        }
    else if (aqi > 50 && aqi <= 100) {
        color = "yellow"
        }
    else if (aqi > 100 && aqi <= 150) {
        color = "orange"
        }
    else if (aqi > 150 && aqi <= 200) {
        color = "red"
        }
    else if (aqi > 200 && aqi <= 300) {
        color = "purple"
        }
    else if (aqi > 300 && aqi <= 500) {
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
        stations(startDate);
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