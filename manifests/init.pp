class ss_graphite_client (
	$graphite_server = "localhost",
	$graphite_port = "2003",
) {

	class { 'ss_graphite_client::install': }

}
