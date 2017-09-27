class graphite::core {

	file {'/opt/graphite/scripts/core-metrics':
		owner   => root,
		group   => root,
		mode    => 755,
		source  => "puppet:///modules/graphite/graphite-scripts/core-metrics",
	}

}
