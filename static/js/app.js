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

        function addEventsToQueryHistory(){
            $('.usr-dbquery-detail').off('click').on('click',function() {
                query=$(this).attr('alt');
                show_detail_one(query);
            });

            $('.usr-dbquery-list').off('click').on('click',function() {
                query=$(this).parent().prev().find('.usr-dbquery-detail').attr('alt');
                show_list(query);
            });

            $('.remove-entry').off('click').on('click',function(){

                // if checked: uncheck and trigger change event
                $(this).parent().parent().find('input[name=andCheck]:checked').prop('checked',false);
                $('#historyTable input[name=andCheck]').triggerHandler('change');

                // and remove this row.
                $(this).parent().parent().remove();
                storeToLocalStorage(stor_key);
            });

            $('#historyTable input[name=andCheck]').off('change').on('change', function(){
                andQuery=[];
                $('#historyTable input[name=andCheck]').each(function(i, obj) {
                    if ($(obj).prop('checked')) {
                        queryData=$(this).parent().parent().find('.usr-dbquery-detail').attr('alt');
                        console.log("queryData",queryData);
                        andQuery.push(queryData);
                    } 
                });
                // console.log(andQuery);
                $('#andQueryView').html("<ul><li>"+andQuery.join("</li><li>")+"</li></ul>");
                query_count_and(andQuery);
                storeToLocalStorage(stor_key);
            });
        }

        function renderFilelistTable(query, data, notification) {
            // Data from MySQL Query
            $('#filelist').bootstrapTable('destroy');

            $('#filelist').on('post-body.bs.table', function(){
                notification.update({'message':'Data load successful','type':'success'});
                notification.close();

                $('#jsonView').hide();
                $('#tableView').show();

            }).bootstrapTable({data:data});

            $('#filelist').off('click-row.bs.table').on('click-row.bs.table', function(e, row, $element) {
                query="md5sum="+row.MD5_KEY;
                query_count(query);
                show_detail_one(query);
            });
        }


        function query_count(query){
            var notify=$.notify({'message':'Counting...'},{'type':'info'});
            $.ajax({
                // url:"http://192.168.41.1:28017/MDP/behaviorCollection/?filter_"+q,
                url: "./count/",
                type:"POST",
                dataType:"json",
                data:{
                    "query": query
                },
                success: function(data) {
                    notify.update({'message':'Success','type':'success'});
                    append_query_history(query, data, false);
                    addEventsToQueryHistory();
                    setTimeout(function() { notify.close();},1500);

                },
                error: function (XMLHttpRequest, textStatus, errorThrown) {
                    console.log('error',errorThrown);
                    notify.update({'title':'ERROR', 'message':errorThrown, 'type':'danger'});
                    setTimeout(function() { notify.close();},2000);
                }
            });
        }

        function query_count_and(andQueryArray) {
            if ( andQueryArray.length>0 ) {
                // console.log(andQuery, andQuery.length);
                $.ajax({
                    // url:"http://192.168.41.1:28017/MDP/behaviorCollection/?filter_"+q,
                    url: "./count/and/",
                    type:"POST",
                    dataType:"json",
                    data:{
                        "query": andQueryArray
                    },
                    success: function(data) {
                        // console.log(data);
                        var count=data;
                        $('#andQueryTitle').html('AND Query <small><a href="#/" id="andQueryGetList">Total '+count+' Found </a></small>');

                        $('#andQueryGetList').off('click').on('click', function() {

                            var notify=$.notify({'message':"Loading Data..."},{'type':'info'});

                            $.ajax({
                                url: "./list/and/",
                                type: "POST",
                                dataType:"json",
                                data:{
                                    "query":andQueryArray
                                },
                                success: function(data){
                                    // $.notify({'message':"Rendering Data..."},{'type':'info'});

                                    // $('#jsonView').hide();
                                    // $('#tableView').show();

                                    renderFilelistTable(andQueryArray, data, notify);
                                },
                                error: function (XMLHttpRequest, textStatus, errorThrown) {
                                    console.log('error',errorThrown);
                                    notify.update({'title':'ERROR', 'message':errorThrown, 'type':'danger'});
                                    setTimeout(function() { notify.close();},2000);
                                }
                            });
                        });
                    },
                    error: function (XMLHttpRequest, textStatus, errorThrown) {
                        console.log('error',errorThrown);
                        notify.update({'title':'ERROR', 'message':errorThrown, 'type':'danger'});
                        setTimeout(function() { notify.close();},2000);
                        // $.notify({'message':"Error "+errorThrown},{'type':'danger'});
                    }
                });
            }
        }

        function append_query_history(query, count, state){
            if (state==true) { checked="checked"; } else { checked=""; }

            var disp_query="";

            if (query.length>=50) {
                disp_query="..."+query.substr(query.length-50,query.length);
            } else { 
                disp_query=query;
            }

            $('#historyTable>tbody').append(
                '<tr>'+
                    '<td>'+
                        '<a href="#/" class="remove-entry"><i class="axi axi-highlight-remove"></i></a>'+
                    '</td>'+
                    '<td>'+
                        '<input type="checkbox" class="andCheck" name="andCheck" '+checked+' >'+
                    '</td>'+
                    '<td>'+
                        '<a href="#/" class="usr-dbquery-detail" alt="'+query+'">'+disp_query+'</a>'+
                    '</td>'+
                    '<td align="right">'+
                        '<a href="#/" class="usr-dbquery-list" alt="'+count+'">'+count+'</a>'+
                    '</td>'+
                '</tr>'
            );
            storeToLocalStorage(stor_key);
        }

        function show_detail_one(query){

            var notify=$.notify({'message':"Loading Data..."},{'type':'info'});
            // notify.update({'type':'info', 'message':'Loading Data...'});

            $.ajax({
                url: "./detail_one/",
                type:"POST",
                dataType:"json",
                data:{
                    "query":query
                },
                success: function(data) {
                    notify.update({'message':'Rendering Data'});
                    $('#jsonView').html("");
                    $('#jsonView').append(
                        '<div class="row" id="btnrow">'+
                            '<button class="btn btn-primary" id="btnDrawChart">'+
                                'Chart/Tree'+
                            '</button>'+
                        '</div>'+
                        '<div id="jsonChartArea">'+
                        '</div>'
                    ).jsonView(data);

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
                    $('#btnDrawChart').on('click', function(){
                        $('.json-view').toggle()
                        $('#jsonChartArea').html("").toggle();

                        /// GRAPH HERE ///
                        graphWidth=$('#jsonChartArea').width()-30 //-$('.float-div').width();
                        graphHeight=$(window).height()-150 // -$('nav').height()-$('div#btnrow').height();
                        console.log("width",graphWidth, "height", graphHeight);
                        drawPidGraph(data.mdpLog.behavior.behaviorData, "#jsonChartArea", graphWidth, graphHeight, "linear");
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
            // $('#jsonView').hide();
            // $('#tableView').show();
            var notify=$.notify({'message':"Loading Data..."},{'type':'info'});
            // notify.update({'type':'info', 'message':'Loading Data...'});

            $.ajax({
                url: "./list/",
                type:"POST",
                dataType:"json",
                data:{
                    "query":query
                },
                success: function(data){
                    // notify.update({'message':'Rendering Data'});
                    renderFilelistTable(query, data, notify);
                   
                },
                error: function (XMLHttpRequest, textStatus, errorThrown) {
                    console.log('error',errorThrown);
                    notify.update({'title':'Error', 'message':errorThrown, 'type':'danger'});
                    setTimeout(function() { notify.close();},2000);
                }
            });
        }


        //// Main ////

        $('#tableView').hide();
        $('#jsonView').hide();

        loadFromLocalStorage(stor_key)
        addEventsToQueryHistory();

        $('#btn-search').on('click',function(){
            var query = $('#text-search').val();
            query_count(query);
        });

        $('#btn_toggle_tree').on('click',function() {
            if ($('.left_pane').hasClass('show'))
            {
                $('.left_pane').removeClass('show');
                $('.left_pane').addClass('hide');
                $('#editor_pane').removeClass('col-md-7');
                $('#editor_pane').addClass('col-md-12');
                // $('#div_footer').hide();
                // $('nav').hide();
                $(this).text(">");
            } else {
                $('.left_pane').removeClass('hide');
                $('.left_pane').addClass('show');
                $('#editor_pane').addClass('col-md-7');
                $('#editor_pane').removeClass('col-md-12');
                // $('#div_footer').show();
                // $('nav').show();
                $(this).text("<");
            }
        });

        // After Page Load, trigger "change" event to historyTable.
        $('#historyTable input[name=andCheck]').triggerHandler('change');
    });
