class graphite (
	$graphite_server = "localhost",
	$graphite_port = "2003",
) {

	class { 'graphite::install': }

}
