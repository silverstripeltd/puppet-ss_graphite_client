class ss_graphite_client::postfix {

	file {'/opt/graphite/scripts/postfix-metrics':
		owner   => root,
		group   => root,
		mode    => 755,
		source  => "puppet:///modules/ss_graphite_client/graphite-scripts/postfix-metrics",
	}

}
