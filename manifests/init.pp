class ss_graphite_client (
	$graphite_server = "localhost",
	$graphite_port = "2003",
	$relay_port = "2013",
	$use_carbon_c_relay = true,
	$configure_tcp_queue_size_metric = true,
) {

	class { 'ss_graphite_client::install': }

	if $configure_tcp_queue_size_metric == true {
		create_resources(ss_graphite_client::tcp_queue_size, hiera('ss_graphite_client::tcp_queue_size', {}))
	}
}
