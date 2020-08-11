class ss_graphite_client::install inherits ss_graphite_client {

  package {
    'realpath': ensure => installed;
    'logtail': ensure => installed;
    'logster': ensure => installed;
  }

  file {'/usr/lib/python2.7/dist-packages/logster/parsers':
    recurse => true,
    owner   => root,
    group   => root,
    mode    => '0755',
    source  => 'puppet:///modules/ss_graphite_client/logster-parsers',
  }

  file {'/opt/graphite':
    ensure => 'directory',
  }
  -> file {'/opt/graphite/scripts':
    ensure => 'directory',
  }
  -> file {'/opt/graphite/scripts-daily':
    ensure => 'directory',
  }

  # Add bash graphite functions
  -> file {'/opt/graphite/graphite_functions':
    owner  => root,
    group  => root,
    mode   => '0755',
    source => 'puppet:///modules/ss_graphite_client/graphite_functions',
  }

  file {'/opt/graphite/graphite_functions.php':
      owner  => root,
      group  => root,
      mode   => '0755',
      source => 'puppet:///modules/ss_graphite_client/graphite_functions.php',
  }

  if $use_carbon_c_relay == true {
    if $lsbdistcodename == 'jessie' {
      file { '/usr/src/carbon-c-relay_2.5-1~bpo8+1_amd64.deb':
        ensure => present,
        owner  => root,
        group  => root,
        mode   => '0644',
        source => 'puppet:///modules/ss_graphite_client/carbon-c-relay_2.5-1~bpo8+1_amd64.deb',
      }
      package { 'carbon-c-relay':
        ensure   => latest,
        provider => dpkg,
        source   => '/usr/src/carbon-c-relay_2.5-1~bpo8+1_amd64.deb',
        require  => File['/usr/src/carbon-c-relay_2.5-1~bpo8+1_amd64.deb'],
      }
    } else {
      package { 'carbon-c-relay':
        ensure => latest,
      }
    }

    file { '/etc/carbon-c-relay.conf':
      ensure  => present,
      owner   => root,
      group   => root,
      mode    => '0644',
      content => template('ss_graphite_client/carbon-c-relay.conf.erb'),
      require => Package['carbon-c-relay'],
      notify  => Service['carbon-c-relay'],
    }
    file { '/etc/default/carbon-c-relay':
      ensure  => present,
      owner   => root,
      group   => root,
      mode    => '0644',
      content => template('ss_graphite_client/carbon-c-relay.defaults.erb'),
      require => Package['carbon-c-relay'],
      notify  => Service['carbon-c-relay'],
    }

    service { 'carbon-c-relay':
      ensure     => running,
      enable     => true,
      hasstatus  => true,
      hasrestart => true,
    }
  }

  if $use_carbon_c_relay == true {
    $graphite_cron_port = $relay_port
  } else {
    $graphite_cron_port = $graphite_port
  }
  file { '/etc/cron.d/graphite-scripts':
    ensure  => present,
    owner   => root,
    group   => root,
    mode    => '0755',
    content => "* * * * *       root    run-parts /opt/graphite/scripts --arg=localhost --arg=${graphite_cron_port} >/dev/null 2>&1\n",
    require => File['/opt/graphite/scripts'],
  }
  file { '/etc/cron.d/graphite-scripts-daily':
    ensure  => present,
    owner   => root,
    group   => root,
    mode    => '0755',
    content => "34 4 * * *       root    run-parts /opt/graphite/scripts-daily --arg=localhost --arg=${graphite_cron_port} >/dev/null 2>&1\n",
    require => File['/opt/graphite/scripts-daily'],
  }
}
