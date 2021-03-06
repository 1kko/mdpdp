$(document).ready(function() {
    
    //// Initialize ////
    // Notification Widget default config.
    $.notifyDefaults({
        type: 'danger',
        placement: {
            from:  "top",
            align: "right"
        },
        offset: {
            x:10,
            y:55
        },
        z_index: 2000,
        animate: {
            enter: 'animated fadeInDown',
            exit: 'animated fadeOutRight'
        },
        delay: 60000,
        allow_dismiss: false
    });

    var search_key_timeout=false;
    var andQuery=[];
    var stor_key='query_history';

    $('.bootstrapTable').bootstrapTable();

    //// Functions ////
    
    function loadFromLocalStorage(stor_key) {
        var stored_values = JSON.parse(window.localStorage.getItem(stor_key));
        for ( var i in stored_values ) {
            append_query_history(stored_values[i].query, stored_values[i].count, stored_values[i].state);
        }
    }

    function storeToLocalStorage(stor_key) {
        // target=$(this);
        var values=[];
        $('#historyTable>tbody>tr').each(function() {
            query=$(this).find('.usr-dbquery-detail').attr('alt');
            count=$(this).find('.usr-dbquery-list').attr('alt');
            state=$(this).find('.andCheck').prop('checked');
            values.push({query:query, count:count, state:state});
        });
        // console.log(values);
        window.localStorage.setItem(stor_key, JSON.stringify(values));
    }

    // function renderFilelistTable(query, url) {
    //     var notify=$.notify({'message':"Loading Data..."},{'type':'info'});
    //     $('#filelist').bootstrapTable('destroy');
    //     $('#filelist').bootstrapTable({
    //         url: url, 
    //         method:'get', 
    //         silent:true,
    //         // contentType:'text',
    //         queryParams: function(p) {
    //             return {
    //                 'limit': p.limit,
    //                 'offset': p.offset,
    //                 'sort':p.sort,
    //                 'order':p.order,
    //                 'search':p.search,
    //                 'query':query
    //             };
    //         }
    //     }).on('load-success.bs.table', function(){
    //         notify.update({'message':'Data load successful','type':'success'});
    //         notify.close();
    //         $('#jsonView').hide();
    //         $('#tableView').show();
    //     }).on('page-change.bs.table', function(){
    //         notify=$.notify({'message':"Loading Data..."},{'type':'info'});
    //     });
    //     // $('#filelist').off('click-row.bs.table').on('click-row.bs.table', function(e, row, $element) {
    //     //     query="md5sum="+row.MD5_KEY;
    //     //     append_query_history(query, 1, false);
    //     //     addEventsToQueryHistory();
    //     //     // query_count(query);
    //     //     // show_detail_one(query);
    //     // });
    // }


    // function query_count(query){
    //     var notify=$.notify({'message':'Counting...'},{'type':'info'});
        
    //     return $.ajax({
    //         // url:"http://192.168.41.1:28017/MDP/behaviorCollection/?filter_"+q,
    //         url: "/count/",
    //         type:"POST",
    //         dataType:"json",
    //         async: false,
    //         data:{
    //             "query": query
    //         },
    //         success: function(data) {
    //             // console.log("query_count",query);
    //             notify.update({'message':'Success','type':'success'});
    //             // console.log("data",data);

    //             // append_query_history(query, data, false);
    //             // addEventsToQueryHistory();
    //             setTimeout(function() { notify.close();},1500);
    //             // return data;
    //             // retval=data;
    //             // return retval;

    //         },
    //         error: function (XMLHttpRequest, textStatus, errorThrown) {
    //             console.log('error',errorThrown);
    //             notify.update({'title':'ERROR', 'message':errorThrown, 'type':'danger'});
    //             setTimeout(function() { notify.close();},2000);
    //         }
    //     }).responseJSON;
    //     // console.log(retval.responseJSON);
    //     // return retval.responseJSON;
    // }

    // function query_count_and(andQueryArray) {
    //     if ( andQueryArray.length>0 ) {
    //         // console.log(andQuery, andQuery.length);
    //         $.ajax({
    //             // url:"http://192.168.41.1:28017/MDP/behaviorCollection/?filter_"+q,
    //             url: "/count/and/",
    //             type:"POST",
    //             dataType:"json",
    //             data:{
    //                 "query": andQueryArray
    //             },
    //             success: function(data) {
    //                 // console.log(data);
    //                 var count=data;
    //                 $('#andQueryTitle').html('AND Query <small><a href="#/" id="andQueryGetList">Total '+count+' Found </a></small>');

    //                 $('#andQueryGetList').off('click').on('click', function() {
    //                     renderFilelistTable(andQueryArray, '/list/and/');

    //                 });
    //             },
    //             error: function (XMLHttpRequest, textStatus, errorThrown) {
    //                 console.log('error',errorThrown);
    //                 notify.update({'title':'ERROR', 'message':errorThrown, 'type':'danger'});
    //                 setTimeout(function() { notify.close();},2000);
    //                 // $.notify({'message':"Error "+errorThrown},{'type':'danger'});
    //             }
    //         });
    //     }
    // }

    function append_query_history(query, count, state){
        if (state==true) { checked="checked"; } else { checked=""; }

        var disp_query="";
        var id = Math.max.apply(this,$.map($('#historyTable').bootstrapTable('getData'), function(o){ return o.ID; }))+1;
        if (id==-Infinity) {
            id=1;
        }

        if (query) {
            data={ID:id ,Query:query, Count:count, AND:state};
            // console.log(data);

            $('#historyTable').bootstrapTable('prepend', data)
            
            // disp_query=query;
            // if (query.length>=32) {
            //     disp_query="..."+query.substr(query.length-32,query.length);
            // }

            // $('#historyTable>tbody').prepend(
            //     '<tr>'+
            //         '<td>'+
            //             '<a href="#/" class="remove-entry"><i class="axi axi-highlight-remove"></i></a>'+
            //         '</td>'+
            //         '<td>'+
            //             '<input type="checkbox" class="andCheck" name="andCheck" '+checked+' >'+
            //         '</td>'+
            //         '<td>'+
            //             '<a href="#/" class="usr-dbquery-detail" alt="'+query+'" title="'+query+'">'+disp_query+'</a>'+
            //         '</td>'+
            //         '<td align="right">'+
            //             '<a href="#/" class="usr-dbquery-list" alt="'+count+'">'+count+'</a>'+
            //         '</td>'+
            //     '</tr>'
            // );
            // $('#historyTable').bootstrapTable({'height':$(window).height()-200});
            // $('#historyTable').bootstrapTable();
            // $(window).on('resize', function() {
            //     $('#historyTable').bootstrapTable('resetView',{'height':$(window).height()-200});
            // });
            // storeToLocalStorage(stor_key);
        }
    }

    function show_detail_one(query){

        var notify=$.notify({'message':"Loading Data..."},{'type':'info'});
        // notify.update({'type':'info', 'message':'Loading Data...'});

        $.ajax({
            url: "/detail_one/",
            type:"POST",
            dataType:"json",
            data:{
                "query":query
            },
            success: function(data) {
                notify.update({'message':'Rendering Data'});
                $('#jsonView').html("");
                $('#jsonView').append(
                    '<div id="jsonChartArea">'+
                    '</div>'
                ).jsonView(data);

                $('#jsonView').each(function(event,data){
                    // TODO :Very Dirty and ugly method to collapse  
                    // id
                    $('#jsonView > div.json-view > span > ul > li:nth-child(1) > span.collapser').click();
                    // mdpLog / analysisDevices
                    $('#jsonView > div.json-view > span > ul > li:nth-child(3) > span.block > ul > li:nth-child(1) > span.collapser').click();
                    // mdpLog / references
                    $('#jsonView > div.json-view > span > ul > li:nth-child(3) > span.block > ul > li:nth-child(3) > span.collapser').click();
                    // mdpLog / behavior
                    $('#jsonView > div.json-view > span > ul > li:nth-child(3) > span.block > ul > li:nth-child(4) > span.collapser').click();
                })

                $('#tableView').hide();
                $('#jsonView').show();

                $('a.value').on('click',function(){
                    q=$(this).attr('path')
                    v=$(this).html();
                    // console.log(q,v);
                    $('#text-search').val(q+"="+v);
                    $('#btn-search').click();
                });

                $('#jsonChartArea').hide();
                function toggle_chart_tree(state){
                    if ( state == true ) {
                        $('.json-view').hide();
                        $('#jsonChartArea').html("").show();

                        /// GRAPH HERE ///
                        graphWidth=$('#jsonChartArea').width() //-$('.float-div').width();
                        graphHeight=$(window).height()-100 // -$('nav').height()-$('div#btnrow').height();
                        // console.log("width",graphWidth, "height", graphHeight);
                        drawPidGraph(data.mdpLog.behavior.behaviorData, "#jsonChartArea", graphWidth, graphHeight, "linear");
                    } else {
                        $('.json-view').show();
                        $('#jsonChartArea').html("").hide();
                    }
                }

                toggle_chart_tree($("#tree_chart_toggle").bootstrapSwitch('state'));

                $("#tree_chart_toggle").on('switchChange.bootstrapSwitch', function(event, state){
                    toggle_chart_tree(state);
                });

                notify.update({'type':'success','message':'Data load successful'});
                setTimeout(function() { notify.close();},1500);
            },
            error: function (XMLHttpRequest, textStatus, errorThrown) {
                console.log('error',errorThrown);
                notify.update({'title':'Error', 'message':errorThrown, 'type':'danger'});
                setTimeout(function() { notify.close();},2000);

            }
        });
    }

    function show_list(query){
        renderFilelistTable(query, '/list/');
     }


    //// Main ////

    $('#tableView').show();
    $('#jsonView').hide();


    loadFromLocalStorage(stor_key)
    // addEventsToQueryHistory();

    // $('#btn-search').on('click',function(){
    //     var query = $('#text-search').val();
    //     var count = query_count(query);
    //     append_query_history(query, count, false);
    //     // addEventsToQueryHistory();
    // });

    $("#tree_chart_toggle").bootstrapSwitch({'size':'mini', 'onText':'Chart', 'offText':'Tree', 'onColor':'primary', 'offColor':'info'});

    $('#dragbar').mousedown(function(e){
            e.preventDefault();
            // $('#mousestatus').html("mousedown" + i++);
            $(document).mousemove(function(e){
            // $('#position').html(e.pageX +', '+ e.pageY);
            pageWidth=e.pageX+2;
            columnWidth=$('.usr-dbquery-detail').width();
            $('#editor_pane').css("left",e.pageX+2+30);
        })
           // console.log("leaving mouseDown");
    });


    // $('#btn_toggle_tree').on('click',function() {
    //     if ($('.left_pane').hasClass('show'))
    //     {
    //         $('.left_pane').removeClass('show');
    //         $('.left_pane').addClass('hide');
    //         $('#editor_pane').removeClass('col-md-8');
    //         $('#editor_pane').addClass('col-md-12');
    //         // $('#div_footer').hide();
    //         // $('nav').hide();
    //         $(this).text(">");
    //     } else {
    //         $('.left_pane').removeClass('hide');
    //         $('.left_pane').addClass('show');
    //         $('#editor_pane').addClass('col-md-8');
    //         $('#editor_pane').removeClass('col-md-12');
    //         // $('#div_footer').show();
    //         // $('nav').show();
    //         $(this).text("<");
    //     }
    // });

    // $('#find_common').on('click', function() {

    //     var md5array = $.map($(this).bootstrapTable('getSelections'), function (row) {
    //         return row.MD5_KEY; //.split("=")[1];
    //     });

    //     // var selections=$('#filelistTable').bootstrapTable('getSelections');
    //     // var md5array=[];
    //     // for ( i in selections ) {
    //     //     console.log(selections[i].MD5_KEY);
    //     //     md5array.push(selections[i].MD5_KEY);
    //     // }
    //     $('#myModalTable').bootstrapTable('destroy');
        
    //     var notify=$.notify({'message':"Loading Data..."},{'type':'info'});
    //     var jsonString=
    //     $.ajax({
    //         type: "POST",
    //         url: "/find/common/",
    //         data: {
    //             "query": md5array
    //         },
    //         cache: false,
    //         dataType: 'json',
    //         success: function(data) {
    //             notify.update({'type':'success','message':'Data load successful'});
    //             setTimeout(function() { notify.close();},1500);
    //             // console.log(data);
    //             tbData=[]
    //             for (var key in data) {
    //                 for (var i in data[key]) {
    //                     tbData.push({'key':key, 'value':data[key][i]})
    //                 }
    //             }
    //             $('#myModalTable').bootstrapTable({data:tbData});

    //             $('#btnCloseModal').on('click',function(){
    //                 $('#myModalTable').bootstrapTable('destroy');
    //             });
    //             $('#btnSave').on('click', function(){
    //                 table=$('#myModalTable').bootstrapTable('getSelections');
    //                 for (var i in table) {
    //                     // TODO: BUG HERE !!!
    //                     count=query_count(table[i]['key']+"="+table[i]['value']);
    //                     append_query_history(table[i]['key']+"="+table[i]['value'], count, false);
    //                     addEventsToQueryHistory();
    //                 }
    //                 $('#myModalTable').bootstrapTable('destroy');
    //                 $('#btnCloseModal').click();
    //             });
    //         },
    //         error: function (XMLHttpRequest, textStatus, errorThrown) {
    //             console.log('error',errorThrown);
    //             notify.update({'title':'Error', 'message':errorThrown, 'type':'danger'});
    //             setTimeout(function() { notify.close();},2000);
    //         }
    //     });

    // });

    // var md5list=$('#md5liststr');
    // if (md5list.length>0) {
    //     console.log(md5list);
    //     var md5array=md5list.val().split(";");
    //     var queryArray=[];
    //     if (md5array.length>0) {
    //         for (var i in md5array) {
    //             queryArray.push("md5sum="+md5array[i]);
    //         }
    //         // console.log(md5list);
    //         // console.log(md5array);
    //         renderFilelistTable(queryArray, '/list/or/');
    //         // remove value to avoid futher reload.
    //         md5list.val("");
    //         md5array=[];
    //     }
    // }


    // After Page Load, trigger "change" event to historyTable.
    $('#historyTable input[name=andCheck]').triggerHandler('change');
});
