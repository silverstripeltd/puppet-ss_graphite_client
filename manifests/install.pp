class ss_graphite_client::install inherits ss_graphite_client {

  package {
    realpath: ensure => installed;
    logtail: ensure => installed;
    logster: ensure => installed;
  }

  # Remove legacy version of logster (compiled, not packaged)
  file {"/usr/sbin/logster":
    ensure => absent,
  }
  # Remove legacy graphite scripts
  file {'remove-graphite-scripts':
    ensure  => absent,
    path    => '/usr/share/graphite-scripts',
    recurse => true,
    purge   => true,
    force   => true,
  }
  # Install SS Logster parsers
  file {"/usr/lib/python2.7/dist-packages/logster/parsers":
    recurse => true,
    owner => root,
    group => root,
    mode => 0755,
    source => "puppet:///modules/ss_graphite_client/logster-parsers",
  }

  file {'/opt/graphite':
    ensure => 'directory',
  } ->
  file {'/opt/graphite/scripts':
    ensure => 'directory',
  } ->
  file {'/opt/graphite/scripts-daily':
    ensure => 'directory',
  } ->

  # Add bash graphite functions
  file {'/opt/graphite/graphite_functions':
    owner   => root,
    group   => root,
    mode    => 0755,
    source  => "puppet:///modules/ss_graphite_client/graphite_functions",
  }

  file {'/opt/graphite/graphite_functions.php':
      owner   => root,
      group   => root,
      mode    => 0755,
      source  => "puppet:///modules/ss_graphite_client/graphite_functions.php",
  }

  # Metrics always sent to localhost. If graphite_server is external, relay will forward appropriately
  file { "/etc/cron.d/graphite-scripts":
    ensure  => present,
    owner   => root,
    group   => root,
    mode    => 755,
    content => "* * * * *       root    run-parts /opt/graphite/scripts --arg=localhost --arg=2003>/dev/null 2>&1\n",
    require => File['/opt/graphite/scripts'],
  }

  file { "/etc/cron.d/graphite-scripts-daily":
    ensure  => present,
    owner   => root,
    group   => root,
    mode    => 0755,
    content => "34 4 * * *       root    run-parts /opt/graphite/scripts-daily --arg=localhost --arg=2003 >/dev/null 2>&1\n",
    require => File['/opt/graphite/scripts-daily'],
  }

  # Only set up relay if server not localhost
  if $graphite_server != 'localhost' {
    if $lsbdistcodename == 'jessie' {
      file { "/usr/src/carbon-c-relay_2.5-1~bpo8+1_amd64.deb":
        ensure => present,
        owner => root,
        group => root,
        mode => 0644,
        source => 'puppet:///modules/ss_graphite_client/carbon-c-relay_2.5-1~bpo8+1_amd64.deb',
      }
      package { "carbon-c-relay":
        ensure => latest,
        provider => dpkg,
        source => '/usr/src/carbon-c-relay_2.5-1~bpo8+1_amd64.deb',
        require => File['/usr/src/carbon-c-relay_2.5-1~bpo8+1_amd64.deb'],
      }
    } else {
      package { "carbon-c-relay":
        ensure => latest,
      }
    }

    file { "/etc/carbon-c-relay.conf":
      ensure => present,
      owner => root,
      group => root,
      mode => 0644,
      content => template('ss_graphite_client/carbon-c-relay.conf.erb'),
      require => Package['carbon-c-relay'],
      notify => Service['carbon-c-relay'],
    }

    service { "carbon-c-relay":
      enable => true,
      ensure => running,
      hasstatus => true,
      hasrestart => true,
    }

  }

}
