# Graphite library

## Installing

Add the following to your manifest:

```puppet
class {'ss_graphite_client':
	graphite_server => 'metrics.my.com',
}
```

## Customising the prefix

By default, *graphite-functions* library will try to figure out a prefix that makes some sense. However it's rather likely you will need to customise it. In that case, write the custom prefix to `/opt/graphite/prefix` and it will be automatically picked up.

## Enabling particular metrics

Metrics are grouped in classes. You enable them by including the relevant class:

```puppet
include ss_graphite_client::core
```

## Adding custom metrics

We recommend the following approach when defining new metrics.

First, copy one of the following templates as your base:

* [PHP template](docs/php-template)
* [Bash template](docs/bash0template)

These show you how to include the *graphite-functions* library. This library allows you to easily send metrics to graphite using the functions they expose (such as `send` or `sendHash`). By convention, the metric key is built by applying the prefix (also exposed from the library).

The metrics are enabled by simply adding them to `/opt/graphite/scripts`, `/opt/graphite/scripts-hourly` or `/opt/graphite/scripts-daily`. Bundle the file resources in a metric class, for example:

```puppet

class my_metrics::filesystem {
	file {'/opt/graphite/scripts/inodes':
		owner   => root,
		group   => root,
		mode    => 755,
		source  => 'puppet:///modules/my_metrics/graphite-scripts/inodes',
	}
	
	# ... could contain more metrics
}
```

Once this is done, the metric can be added thus:

```puppet
include my_metrics::filesystem
```
