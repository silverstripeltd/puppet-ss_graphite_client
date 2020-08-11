# TCP queue size for $name port.
define ss_graphite_client::tcp_queue_size(
  $port = undef,
) {
  $real_port = pick($port, $name)
  validate_integer($real_port)

  file { "/opt/graphite/scripts/tcp_queue_size_${name}":
    ensure  => present,
    owner   => root,
    group   => root,
    mode    => '0755',
    content => template('ss_graphite_client/tcp_queue_size.erb'),
    require => File['/opt/graphite/scripts'],
  }

}
