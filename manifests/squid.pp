class ss_graphite_client::squid {

	file {'/opt/graphite/scripts/squid-metrics':
		owner   => root,
		group   => root,
		mode    => 755,
		source  => "puppet:///modules/ss_graphite_client/graphite-scripts/squid-metrics",
	}

}
