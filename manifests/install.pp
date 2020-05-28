class ss_graphite_client::install inherits ss_graphite_client {

  package {
    'logtail': ensure => installed;
  }
  
  #package names are unstable between releases
  if $facts['lsbdistcodename'] == 'jessie' {
    package {
    'realpath': ensure => installed;
    'logster': ensure => installed;
    }
  }
  #logster no longer included as of buster
  #so we can install via the stretch deb (last possible debian package version)
  if $facts['lsbdistcodename'] == 'buster' {
    file { '/usr/src/logster_0.0.1-2_all.deb':
      mode => '0600',
      owner => root,
      group => root,
      source => 'puppet:///modules/ss_graphite_client/logster_0.0.1-2_all.deb',
    }
    package { 'logster':
      ensure   => latest,
      provider => dpkg,
      source   => '/usr/src/logster_0.0.1-2_all.deb'
    }
    package { 'logsterDeps':
      ensure => installed,
      name => 'python-pkg-resources',
      before => Package['logster']
    }
  }
  file {'/usr/lib/python2.7/dist-packages/logster/parsers':
    recurse => true,
    owner => root,
    group => root,
    mode => '0755',
    source => 'puppet:///modules/ss_graphite_client/logster-parsers',
  }

  file {'/opt/graphite':
    ensure => 'directory',
  }
  file {'/opt/graphite/scripts':
    ensure => 'directory',
  }
  file {'/opt/graphite/scripts-daily':
    ensure => 'directory',
  }

  # Add bash graphite functions
  file {'/opt/graphite/graphite_functions':
    owner   => root,
    group   => root,
    mode    => '0755',
    source  => 'puppet:///modules/ss_graphite_client/graphite_functions',
  }

  file {'/opt/graphite/graphite_functions.php':
      owner   => root,
      group   => root,
      mode    => '0755',
      source  => 'puppet:///modules/ss_graphite_client/graphite_functions.php',
  }

  if $ss_graphite_client::use_carbon_c_relay == true {
    if $facts['lsbdistcodename'] == 'jessie' {
      file { '/usr/src/carbon-c-relay_2.5-1~bpo8+1_amd64.deb':
        ensure => present,
        owner => root,
        group => root,
        mode => '0644',
        source => 'puppet:///modules/ss_graphite_client/carbon-c-relay_2.5-1~bpo8+1_amd64.deb',
      }
      package { 'carbon-c-relay':
        ensure => latest,
        provider => dpkg,
        source => '/usr/src/carbon-c-relay_2.5-1~bpo8+1_amd64.deb',
        require => File['/usr/src/carbon-c-relay_2.5-1~bpo8+1_amd64.deb'],
      }
    } else {
      package { 'carbon-c-relay':
        ensure => latest,
      }
    }

    file { '/etc/carbon-c-relay.conf':
      ensure => present,
      owner => root,
      group => root,
      mode => '0644',
      content => template('ss_graphite_client/carbon-c-relay.conf.erb'),
      require => Package['carbon-c-relay'],
      notify => Service['carbon-c-relay'],
    }
    file { '/etc/default/carbon-c-relay':
      ensure => present,
      owner => root,
      group => root,
      mode => '0644',
      content => template('ss_graphite_client/carbon-c-relay.defaults.erb'),
      require => Package['carbon-c-relay'],
      notify => Service['carbon-c-relay'],
    }

    service { 'carbon-c-relay':
      ensure => running,
      enable => true,
      hasstatus => true,
      hasrestart => true,
    }
  }

  if $ss_graphite_client::use_carbon_c_relay == true {
    $graphite_cron_port = $ss_graphite_client::relay_port
  } else {
    $graphite_cron_port = $ss_graphite_client::graphite_port
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
