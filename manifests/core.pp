class ss_graphite_client::core {

	file {'/opt/graphite/scripts/core-metrics':
		owner   => root,
		group   => root,
		mode    => 755,
		source  => "puppet:///modules/ss_graphite_client/graphite-scripts/core-metrics",
	}

}
