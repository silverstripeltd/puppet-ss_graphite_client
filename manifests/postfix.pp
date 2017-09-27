class graphite::postfix {

	file {'/opt/graphite/scripts/postfix-metrics':
		owner   => root,
		group   => root,
		mode    => 755,
		source  => "puppet:///modules/graphite/graphite-scripts/postfix-metrics",
	}

}
