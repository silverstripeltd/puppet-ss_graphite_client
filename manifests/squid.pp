class graphite::squid {

	file {'/opt/graphite/scripts/squid-metrics':
		owner   => root,
		group   => root,
		mode    => 755,
		source  => "puppet:///modules/graphite/graphite-scripts/squid-metrics",
	}

}
