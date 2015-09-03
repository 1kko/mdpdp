function loadResultTable(daterange, target_id){
	$.ajax({
		url:"fetch.php?type=ResultTable&daterange="+daterange,
		dataType:"json",
		success: function(data) {
			$(target_id).bootstrapTable('destroy');
			$(target_id).bootstrapTable({data:data});
		}

	});
}