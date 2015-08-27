
function drawPidGraph(behaviorData, CSStarget, width, height, pathDrawType) {
    // draws D3 Graph using pid
    function getIndexOfNode(pid) {
        for (var i = 0; i < nodes.length; i++) {
            if ( (nodes[i].pid===pid) && (nodes[i].type==="Process") ) {
                return i
            }
        }
        return null;
    }

    function getTargetNodeCircumferencePoint(d){
        var t_radius = 10/2; // nodeWidth is just a custom attribute I calculate during the creation of the nodes depending on the node width
        var dx = d.target.x - d.source.x;
        var dy = d.target.y - d.source.y;
        var gamma = Math.atan2(dy,dx); // Math.atan2 returns the angle in the correct quadrant as opposed to Math.atan
        var tx = d.target.x - (Math.cos(gamma) * t_radius);
        var ty = d.target.y - (Math.sin(gamma) * t_radius);
        return [tx,ty]; 
    }


    var myData;

    var processLinks=[];
    var behaviorLinks=[];
    var links=[];
    var nodes=[];

    // var width = 1024,
    //     height = 768;

    var color = d3.scale.category20();

    var force = d3.layout.force()
        .charge(-1000)
        .linkDistance(200)
        .size([width, height]);

    var svg = d3.select(CSStarget).append("svg")
        .attr("width", width)
        .attr("height", height);

    var refinedData=[];
    for (var i = 0; i < behaviorData.length; i++) {
        // console.log(i, behaviorData[i].currentProcess);
        if ( behaviorData[i].currentProcess !== undefined ) {
            var d=behaviorData[i];
            var category="["+d.target["@category"]+"] "+"("+d.currentProcess.pid+")";
            switch (d.target["@category"]) {
                case "Process":
                    group=1;
                    name=category+d.currentProcess.path+"("+d.currentProcess.pid+")";
                    // console.log(d);
                    break;
                case "Registry":
                    group=2;
                    name=category+d.target.keyName+"="+d.target.value;
                    break;
                case "System":
                    if (d.target.api!==undefined) {
                        group=3;
                        name=category+d.target.api;
                    } 
                    else if (d.MdpFlagDescription["#text"]!==undefined) {
                        group=3;
                        name=category+d.MdpFlagDescription["#text"]
                    } 
                    else {
                        group=3;
                        name=category+"bc_id="+d.target["@bc_id"]+" "+d["@behavior_type"];
                        // console.log(d);
                    }
                    break;
                case "File":
                    group=6;
                    name=category+d.target.path;
                    break;
                default:
                    group=7;
                    name=category+"Undefined Type";
                    console.log("Undefined Type", d);
                    break;

            }

            source_pid=behaviorData[i].currentProcess.pid;
            target_pid=behaviorData[i].target.pid;
            type=behaviorData[i].target["@category"];
            refinedData.push({"idx": i, "name": name, "source":source_pid, "target":target_pid, "type":type, "group":group});
        } else {
            console.log(behaviorData[i]);
        }
    };

    // generation of nodes and process links
    for (var i = 0; i < refinedData.length; i++) {

        nodes.push({"name":refinedData[i].name, "group":refinedData[i].group, "pid":refinedData[i].source, "type":refinedData[i].type});
        
        if ( refinedData[i].type === "Process" ) {
            for (var j = 0; j < refinedData.length; j++) {
                if ( refinedData[j].target == refinedData[i].source ) {
                    if (refinedData[j].target !== refinedData[j].source ) {
                        // console.log("match:", "target", refinedData[j].target, j, "source", refinedData[i].source, i);
                        processLinks.push({"source":i, "target":j, "value":1, "source_pid":refinedData[j].source, "target_pid":refinedData[j].target});
                        // processLinks.push({"source":i, "target":j, "value":1});
                    }
                }
            }
        }
        else {
            behaviorLinks.push(refinedData[i]);
        }
    }


    for (var i = 0; i < behaviorLinks.length; i++) {
        var idx=getIndexOfNode(behaviorLinks[i].source);
        if (idx!==null) {
            links.push({"source":idx, "target":i, "value":2});
        } else {
            console.log("idx",idx,behaviorLinks[i]);
        }
    };

    // merge together.
    // console.log(links);
    links=links.concat(processLinks);

    // console.log("behaviorLinks",behaviorLinks);
    // console.log("refinedData",refinedData);
    // links=processLinks;

    // Compute the distinct nodes from the links.
    links.forEach(function(link) {
        link.source = nodes[link.source] || (nodes[link.source] = {name: link.source});
        link.target = nodes[link.target] || (nodes[link.target] = {name: link.target});
    });

    myData={"nodes":nodes, "links":links};




    /// Start D3 Graph HERE

    var graph=myData;
    var radius=20
    if (pathDrawType=="circular") {
        
        force
            .nodes(graph.nodes)
            .links(graph.links)
            .start();
        
        var link = svg.selectAll(".link")
            .data(graph.links)
        .enter().append("line")
            .attr("class", "link")
            .style("stroke-width", function(d) { return Math.sqrt(d.value); });
        

        var path = svg.selectAll("path")
            .data(graph.links)
          .enter().append("svg:path")
            .attr("class",      function(d) { return "link "+ d.type; })
            .attr("marker-mid", function(d) { return "url(#"+d.type+")"; })
      
        // Per-type markers, as they don't inherit styles.
        var marker = svg.selectAll("marker-mid")
            .data(graph.links)
        .enter().append("marker-mid")
            .attr("id", String)
            .attr("viewBox", "0 -5 10 10")
            .attr("refX", 5)
            .attr("markerWidth", 6)
            .attr("markerHeight", 6)
            .attr("orient", "auto")
        .append("path")
            .attr("d", "M0,-5L10,0L0,5");

        
        var node = svg.selectAll(".node")
            .data(graph.nodes)
        .enter().append("circle")
            .attr("class", "node")
            .attr("r", radius)
            .style("fill", function(d) { return color(d.group); })
            .call(force.drag);
            // .text(function(d) {return d;});
        
        var text = svg.selectAll(".text")
            .data(graph.nodes)
        .enter().append("text")
            .text(function(d) { return d.name; })
            // .attr("font-family", "sans-serif")
            // .attr("font-size","10px")
            // .attr("align","center")
            // .attr("fill", "#bbb");
        
        force.on("tick", function() {

            link.attr("x1", function(d) { return d.source.x; })
                .attr("y1", function(d) { return d.source.y; })
                .attr("x2", function(d) { return getTargetNodeCircumferencePoint(d)[0]; })
                .attr("y2", function(d) { return getTargetNodeCircumferencePoint(d)[1]; });

        
            node.attr("cx", function(d) { return d.x; })
                .attr("cy", function(d) { return d.y; });
        

            path.attr("d", function(d) {
                var dx = d.target.x - d.source.x,
                    dy = d.target.y - d.source.y,
                    dr = Math.sqrt( dx*dx + dy*dy )/4,
                    mx = d.source.x + dx,
                    my = d.source.y + dy;

                return [
                    "M", d.source.x, d.source.y,
                    "A", dr, dr, 0, 0, 1, mx, my,
                    "A", dr, dr, 0, 0, 1, d.target.x, d.target.y
                ].join(" ");
            });

        
            text.attr("x", function(d) { return d.x-(radius);})
                .attr("y", function(d) { return d.y+(radius+radius/2);});
        });
    } else {
        force
              .nodes(graph.nodes)
              .links(graph.links)
              .start();

          var link = svg.selectAll(".link")
              .data(graph.links)
            .enter().append("line")
              .attr("class", "link")
              .style("stroke-width", function(d) { return Math.sqrt(d.value); });

          var node = svg.selectAll(".node")
              .data(graph.nodes)
            .enter().append("circle")
              .attr("class", "node")
              .attr("r", radius)
              .style("fill", function(d) { return color(d.group); })
              .call(force.drag);

          // node.append("title")
          //     .text(function(d) { return d.name; });
          var text = svg.selectAll(".text")
                  .data(graph.nodes)
              .enter().append("text")
                  .text(function(d) { return d.name; })

          force.on("tick", function() {
            link.attr("x1", function(d) { return d.source.x; })
                .attr("y1", function(d) { return d.source.y; })
                .attr("x2", function(d) { return d.target.x; })
                .attr("y2", function(d) { return d.target.y; });

            node.attr("cx", function(d) { return d.x; })
                .attr("cy", function(d) { return d.y; });

            text.attr("x", function(d) { return d.x-(radius);})
                .attr("y", function(d) { return d.y+(radius+radius/2);});
          });

    }






}
