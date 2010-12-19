function build_vis(indata){

            /* Scales and sizing. */
//            (function() {
//                var format = pv.Format.date("%d/%m/%y");
//                indata.forEach(function(d) { d.date = format.parse(d.date); });
//            })()
            var w = 720,
                h1 = 400,
                h2 = 100,
                bottom = 10,
                right = 55,
                top = 10,
                // flatten to workout the min/max values accross funds
 
                // convert dates to Date objects
                data = pv.dict(pv.keys(indata), function(k){
                    // fdata will be an array of {ts: timestamp, val: the_data}
                    var fdata = indata[k];
                    var ts_data = series_data.sort(function(a, b){ return a.ts - b.ts;});
 
                    ts_data.forEach(function(value){
                        value.date = new Date(value.ts*1000);
 
                    });
                    return ts_data;
 
                }),
                //fill = pv.colors("lightpink", "darkgray", "lightblue"),
                min_max = pv.blend(pv.values(data)),
                min_val = pv.min(min_max, function(d){ return d['val']}),
                max_val = pv.max(min_max, function(d){ return d['val']}),
//                min_val = pv.min(min_max, function(d){ return d['val']}),
//                max_val = pv.max(min_max, function(d){ return d['val']}),
                start = pv.min(min_max, function(d){ return d.ts;}),
                end = pv.max(min_max, function(d){ return d.ts;}),
                x = pv.Scale.linear(new Date(start*1000), new Date(end*1000)).range(0, w),
                y = pv.Scale.linear(pv.min([min_val, 0]), max_val).range(0, h2),
                ybaseline = y(0),
                ymin = y(min_val),
                line_colors = pv.Colors.category10(),
                zoomed_area_colors = pv.colors.apply(pv.colors,
                                              pv.map(pv.Colors.category10().range(), function(color){
                                                        color.opacity = 0.5;
                                                        return color;
                                                    })),
                area_colors = pv.colors.apply(pv.colors,
                                              pv.map(pv.Colors.category10().range(), function(color){
                                                        color.opacity = 0.2;
                                                        return color;
                                                    }));
            mm = min_max;
            /* Interaction state. Focus scales will have domain set on-render. */
            var i = {x:w - 250, dx:250},
                fy = pv.Scale.linear(min_val, max_val).range(bottom, h1-top),
                fx = pv.Scale.linear().range(0, w-right);
 

            /* Root panel. */
            var vis = new pv.Panel()
                .canvas('vis-target')
                .width(w)
                .height(h1 + 20 + h2)
                .bottom(bottom)
                .left(30)
                .right(right)
                .top(top);
 
            /* Focus panel (zoomed in). */
            var focus = vis.add(pv.Panel)
                .def('highlight_index', -1)
                .event('click', function(){
                        context.highlight_index(-1);
                        this.highlight_index(-1);
                        vis.render();
                    })
                .def("init", function() {
                    var d1 = x.invert(i.x),
                        d2 = x.invert(i.x + i.dx),
                        sliced_values = pv.map(pv.values(data), function(vals){
                                //debugger;
                                return vals.slice(
                                    Math.max(0, pv.search.index(vals, d1,
                                                    function(d){ return d.date; }) - 1),
                                    pv.search.index(vals, d2,
                                                    function(d){ return d.date; }) + 1);
                            });
                    //console.log(dd);
                    fx.domain(d1, d2);
                    var all_vals = pv.blend(sliced_values),
                        min_val = pv.min(all_vals, function(d){ return d.val; }),
                        max_val = pv.max(all_vals, function(d){ return d.val; });
                    fy.domain([(max_val >= 0 & min_val >= 0) ? 0 : min_val,
                               (min_val < 0 & max_val < 0) ? 0 : max_val]);
                    return sliced_values;
                  })
                //.top(0)
                .height(h1);
 

            /* X-axis ticks. */
            focus.add(pv.Rule)
                .data(function(){ return fx.ticks(); } )
                .left(fx)
                .strokeStyle("#eee")
              .anchor("bottom").add(pv.Label)
                .text(fx.tickFormat);
 
            /* Y-axis ticks. */
            focus.add(pv.Rule)
                .data(function(){ return fy.ticks(7)})
                .bottom(fy)
                .strokeStyle(function(d){ return  d ? "#aaa" : "#000";})
              .anchor("left").add(pv.Label)
                .text(fy.tickFormat);
 
            /* Focus area chart. */
            focus.add(pv.Panel)
                .data(function(){
                        return pv.keys(data);
                })
//                //.data(function(){ return focus.init();})
                .overflow("hidden")
              .add(pv.Line)
                .def('zoomed_data', [])
                .data(function(d){
                    //debugger;
                    var data = focus.init()[this.parent.index];
                    this.zoomed_data(data);
                    return data;
                })
                .left(function(d){ return fx(d.date);})
                .bottom(function(d){ return fy(d.val);})
                //.fillStyle(function(d){ return line_colors[this.index];})
                .strokeStyle(function(){
                          var i = this.parent.index;
                          if (focus.highlight_index() == i){
                              return line_colors(i);
                          }
                          return zoomed_area_colors(i)
                        })
                .lineWidth(function(){
                       return focus.highlight_index() == this.parent.index ? 3 : 2;
                    })
                .event('click', function(){
                        var i = this.parent.index;
                        context.highlight_index(i);
                        focus.highlight_index(i);
                        vis.render();
                    })
                .cursor('crosshair')
                .add(pv.Label)
                    .visible(function(){
                                //console.log(this.zoomed_data().length,  this.index);
                                return this.index == this.zoomed_data().length -1;
                            })
                    .textMargin(5)
                    .textBaseline('middle')
                    .font(function(){
                        var font_size = this.parent.index == focus.highlight_index() ?
                                            18 : 14;
                        return 'bold ' + font_size + 'px san-serif';
                    })
                    .textStyle(function(){
                        return this.strokeStyle();
                    })
                    .text(function(){
                            return this.parent.data();
                    });
 
            /* Context panel (zoomed out). */
            var context = vis.add(pv.Panel)
                .def('highlight_index', -1)
                .bottom(0)
                .height(h2);
 
            /* X-axis ticks. */
            context.add(pv.Rule)
                .data(x.ticks())
                .left(x)
                .strokeStyle("#eee")
              .anchor("bottom").add(pv.Label)
                .text(x.tickFormat);
 
            /* Y-axis ticks. */
            context.add(pv.Rule)
                .bottom(y(0))
              .anchor('left').add(pv.Label)
                .text('0');
 

            /* Context line chart. */
            context.add(pv.Panel)
               .data(function(){
                   return pv.keys(data);
                })
               .add(pv.Line)
                    .lineWidth(function(){
 
                                  return context.highlight_index() == this.parent.index ? 2 : 0.5;
                               })
                    .strokeStyle(line_colors.by(pv.parent))
                    .data(function(d){
                        //debugger;
                        return data[d];}
                        )
               .left(function(d){ return x(d.date);})
               .bottom(function(d){ return y(d.val);});
//                    .visible(function(d){
//                                if (this.index >= data[this.parent.data()].length - 1){
//                                    console.log(this.index, d, data[this.parent.data()].length);
//                                }
//                                try {
//                                    return (this.index < data[this.parent.data()].length - 1);
//                                }
//                                catch (e){
//                                    console.log(e);
//                                }
//                            });
 
            /* Context area chart. */
            context.add(pv.Panel)
               .data(function(){
                   return pv.keys(data);
                })
               .add(pv.Area)
                .data(function(d){
                    //debugger;
                    return data[d];}
                    )
                .left(function(d){ return x(d.date);})
                .height(function(d){
                    var val = y(d.val);
                    if (d.val < 0){
                        return ybaseline - val
                    }
                    return val - ybaseline;
                })
                .fillStyle(function(){
                              var i = this.parent.index;
                              if (context.highlight_index() == i){
                                  return zoomed_area_colors(i);
                              }
                              return area_colors(i);
                            })
                .bottom(function(d){
                            var val = y(d.val);
                            if (d.val < 0){
                                return val;
                            }
                            else{
                                return ybaseline;
                            }
                        })
 
 
 
            /* The selectable, draggable focus region. */
            context.add(pv.Panel)
                .data([i])
                .cursor("crosshair")
                .events("all")
                .event("mousedown", pv.Behavior.select())
                .event("select", focus)
              .add(pv.Bar)
                .left(function(d){ return d.x;})
                .width(function(d) { return d.dx;})
                .fillStyle("rgba(100, 100, 100, .2)")
                .cursor("move")
                .event("mousedown", pv.Behavior.drag())
                .event("drag", focus);
 
            vis.render();
            //console.log(focus.init())
            return vis
        }