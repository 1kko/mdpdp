function rowStyle(row, index) {
	if (   (row.DICA_Result=="MALICIOUS")
		|| (row.Heimdal_Result=="MALICIOUS")
		|| (row.V3_Result=="MALICIOUS")
		|| (row.VirusTotal_Result=="MALICIOUS")
		|| (row.MDP_VM_Result=="MALICIOUS")
	) return {
		classes: 'danger'
	};

	if (   (row.DICA_Result=="SUSPICIOUS")
		|| (row.Heimdal_Result=="SUSPICIOUS")
		|| (row.V3_Result=="SUSPICIOUS")
		|| (row.VirusTotal_Result=="SUSPICIOUS")
		|| (row.MDP_VM_Result=="SUSPICIOUS")
	) return {
		classes: 'warning'
	};


	return {};
}