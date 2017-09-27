class graphite::nginx_status {

	file {'/opt/graphite/scripts/nginx-status':
		owner   => root,
		group   => root,
		mode    => 755,
		source  => "puppet:///modules/graphite/graphite-scripts/nginx-status-metrics",
	}

}
