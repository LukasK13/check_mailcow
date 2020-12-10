Plugin for checking a local Mailcow instance via the Mailcow API using Icinga2 / nagios.

# Usage

* **-d / --domain** The domain and optional port to reach the Mailcow instance
* **-e / --endpoint** The endpoint to check (status/containers, status/solr, status/vmail)
* **-k / --key** The Mailcow API key
* **-s / --ssl** Use SSL for the connection to the Mailcow API
* **-i / --insecure** Don't verify the SSL certificate
* **-w / --warning** Warning treshold, where applicable. E.g. for vmail storage usage.
* **-c / --critical** Critical treshold, where applicable

# Icinga2 config

## Comand template

```icinga
object CheckCommand "mailcow" {
    import "plugin-check-command"
    command = [ PluginDir + "/check_mailcow.py" ]
    arguments += {
        "-d" = {
            description = "Domain name and optional port number for the Mailcow API."
            value = "$mailcow_domain$"
        }
        "-i" = {
            description = "Insecure connection. Don't verify the SSL certificate."
            set_if = "$mailcow_insecure$"
        }
        "-k" = {
            description = "Key for the Mailcow API."
            required = true
            value = "$mailcow_apikey$"
        }
        "-e" = {
            description = "The endpoint to be used. Defaults to status/containers."
            value = "$mailcow_endpoint$"
        }
        "-s" = {
            description = "Use SSL for the connection."
            set_if = "$mailcow_ssl$"
        }
        "-w" = {
            description = "Warning treshold"
            value = "$mailcow_warning$"
        }
        "-c" = {
            description = "Critical treshold"
            value = "$mailcow_critical$"
        }
    }
}
```

## Service template

```icinga
template Service "check-mailcow" {
    check_command = "check-mailcow"
    command_endpoint = host_name
    vars.mailcow_insecure = false
    vars.mailcow_ssl = false
}
```

## Host object & Apply rule

```icinga
object Host "server.fully.qualified.domain.name" {
    import "generic-host"
    address = "192.168.122.122"
    vars.client_endpoint = name

    vars.mailcow = {
        "containers" = {
            mailcow_apikey    = "mysecretapikey"
            mailcow_domain    = "mail.mydomain.tld"
            mailcow_endpoint  = "status/containers"
        }
        "solr" = {
            mailcow_apikey    = "mysecretapikey"
            mailcow_domain    = "mail.mydomain.tld"
            mailcow_endpoint  = "status/solr"
        }
        "vmail" = {
            mailcow_apikey    = "mysecretapikey"
            mailcow_domain    = "mail.mydomain.tld"
            mailcow_endpoint  = "status/vmail"
        }
    }
}

apply Service "mailcow-" for (service => config in host.vars.mailcow) to Host {
    import "generic-service"
    check_command = "mailcow"

    command_endpoint = host.vars.client_endpoint

    vars += config

    assign where host.address
}
```
