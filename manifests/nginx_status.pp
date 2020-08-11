class ss_graphite_client::nginx_status {

  file {'/opt/graphite/scripts/nginx-status':
    owner  => root,
    group  => root,
    mode   => '0755',
    source => 'puppet:///modules/ss_graphite_client/graphite-scripts/nginx-status-metrics',
  }

}
