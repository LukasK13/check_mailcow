Plugin for checking a local Mailcow instance via the Mailcow API using Icinga2 / nagios.

# Usage

* **-d / --domain** The domain and optional port to reach the Mailcow instance
* **-k / --key** The Mailcow API key
* **-s / --ssl** Use SSL for the connection to the Mailcow API
* **-i / --insecure** Don't verify the SSL certificate

# Icinga2 config
## Comand template
```
object CheckCommand "check-mailcow" {
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
        "-s" = {
            description = "Use SSL for the connection."
            set_if = "$mailcow_ssl$"
        }
    }
}
```

## Service template
```
template Service "check-mailcow" {
    check_command = "check-mailcow"
    command_endpoint = host_name
    vars.mailcow_insecure = false
    vars.mailcow_ssl = false
}
