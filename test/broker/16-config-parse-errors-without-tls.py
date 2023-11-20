#!/usr/bin/env python3

# Test whether config parse errors are handled

from mosq_test_helper import *

vg_index = 0

def write_config(filename, port, config_str):
    with open(filename, 'w') as f:
        f.write(f"{config_str}")


def do_test(config_str, rc_expected, error_log_entry):
    rc = 1
    port = mosq_test.get_port()

    conf_file = os.path.basename(__file__).replace('.py', '.conf')
    write_config(conf_file, port, config_str)

    try:
        broker = mosq_test.start_broker(conf_file, check_port=False)
        mosq_test.wait_for_subprocess(broker,timeout=1)

        if broker.returncode != rc_expected:
            (stdo, stde) = broker.communicate()
            print(stde.decode('utf-8'))
            return

        (_, stde) = broker.communicate()
        error_log = stde.decode('utf-8')
        if error_log_entry in error_log:
            rc = 0
        else:
            print(f"Error log entry: '{error_log_entry}' not found in '{error_log}'")
    except mosq_test.TestError:
        pass
    except subprocess.TimeoutExpired:
        broker.terminate()
    except Exception as e:
        print(e)
    finally:
        os.remove(conf_file)
        if rc:
            print(f"While testing invalid config entry '{config_str}'")
            exit(rc)

do_test("unknown_option unknown\n", 3, 'Error: Unknown configuration variable "unknown_option"')

do_test("user\n", 3, 'Error: Empty user value in configuration.') # Empty string, no space
do_test("user \n", 3, 'Error: Empty user value in configuration.') # Empty string, single space
do_test("user  \n", 3, 'Error: Empty user value in configuration.') # Empty string, double space
do_test("pid_file /tmp/pid\npid_file /tmp/pid\n", 3, 'Error: Duplicate pid_file value in configuration.') # Duplicate string

do_test("memory_limit\n", 3, 'Empty memory_limit value in configuration.') # Empty ssize_t

do_test("accept_protocol_versions 3\n", 3, 'Error: You must define a listener before using the accept_protocol_versions option.') # Missing listener
do_test("listener 1888\naccept_protocol_versions\n", 3, 'Error: Empty accept_protocol_versions value in configuration.') # Empty value

do_test("allow_anonymous\n", 3, 'Error: Empty allow_anonymous value in configuration.') # Empty bool
do_test("allow_anonymous falst\n", 3, 'Error: Invalid allow_anonymous value (falst).') # Invalid bool

do_test("autosave_interval\n", 3, 'Error: Empty autosave_interval value in configuration.') # Empty int
#do_test("autosave_interval string\n", 3, 'bla') # Invalid int

do_test("listener\n", 3, 'Error: Empty listener value in configuration.') # Empty listener
do_test("mount_point test/\n", 3, 'Error: You must use create a listener before using the mount_point option in the configuration file.') # Missing listener config
do_test("listener 1888\nmount_point test/+/\n", 3, "Error: Invalid mount_point 'test/+/'. Does it contain a wildcard character?") # Wildcard in mount point.
do_test("listener 1888\nprotocol\n", 3, 'Error: Empty protocol value in configuration.') # Empty proto
do_test("listener 1888\nprotocol test\n", 3, 'Error: Invalid protocol value (test).') # Invalid proto

do_test("plugin_opt_inval string\n", 3, 'Error: A plugin_opt_ option exists in the config file without a plugin.') # plugin_opt_ without plugin
do_test("plugin c/auth_plugin.so\nplugin_opt_ string\n", 3, 'Error: Invalid plugin_opt_ config option.') # Incomplete plugin_opt_
do_test("plugin c/auth_plugin.so\nplugin_opt_test\n", 3, 'Error: Empty test value in configuration.') # Empty plugin_opt_

do_test("bridge_attempt_unsubscribe true\n", 3, 'Error: Invalid bridge configuration.') # Missing bridge config
do_test("bridge_bind_address string\n", 3, 'Error: Invalid bridge configuration.') # Missing bridge config
do_test("bridge_insecure true\n", 3, 'Error: Invalid bridge configuration.') # Missing bridge config
do_test("bridge_require_oscp true\n", 3, 'Error: Unknown configuration variable "bridge_require_oscp".') # Missing bridge config
do_test("bridge_max_packet_size 1000\n", 3, 'Error: Invalid bridge configuration.') # Missing bridge config
do_test("bridge_max_topic_alias 1000\n", 3, 'Error: Invalid bridge configuration.') # Missing bridge config
do_test("bridge_outgoing_retain false\n", 3, 'Error: Invalid bridge configuration.') # Missing bridge config
do_test("bridge_protocol_version string\n", 3, 'Error: Invalid bridge configuration.') # Missing bridge config
do_test("bridge_receive_maximum 10\n", 3, 'Error: Invalid bridge configuration.') # Missing bridge config
do_test("bridge_reload_type string\n", 3, 'Error: Invalid bridge configuration.') # Missing bridge config
do_test("bridge_session_expiry_interval 10000\n", 3, 'Error: Invalid bridge configuration.') # Missing bridge config
do_test("bridge_tcp_keepalive 10000\n", 3, 'Error: Invalid bridge configuration.') # Missing bridge config
do_test("bridge_tcp_user_timeout 10000\n", 3, 'Error: Invalid bridge configuration.') # Missing bridge config
do_test("local_clientid str\n", 3, 'Error: Invalid bridge configuration.') # Missing bridge config
do_test("local_password str\n", 3, 'Error: Invalid bridge configuration.') # Missing bridge config
do_test("local_username str\n", 3, 'Error: Invalid bridge configuration.') # Missing bridge config
do_test("notifications true\n", 3, 'Error: Invalid bridge configuration.') # Missing bridge config
do_test("notifications_local_only true\n", 3, 'Error: Invalid bridge configuration') # Missing bridge config
do_test("notification_topic true\n", 3, 'Error: Invalid bridge configuration.') # Missing bridge config
do_test("password pw\n", 3, 'Error: Invalid bridge configuration.') # Missing bridge config
do_test("remote_password pw\n", 3, 'Error: Invalid bridge configuration.') # Missing bridge config
do_test("restart_timeout 10\n", 3, 'Error: Invalid bridge configuration.') # Missing bridge config
do_test("round_robin true\n", 3, 'Error: Invalid bridge configuration.') # Missing bridge config
do_test("start_type lazy\n", 3, 'Error: Invalid bridge configuration.') # Missing bridge config
do_test("threshold 10\n", 3, 'Error: Invalid bridge configuration.') # Missing bridge config
do_test("topic topic/10\n", 3, 'Error: Invalid bridge configuration.') # Missing bridge config
do_test("try_private true\n", 3, 'Error: Invalid bridge configuration.') # Missing bridge config
do_test("username un\n", 3, 'Error: Invalid bridge configuration.') # Missing bridge config

do_test("maximum_qos 3\n", 3, 'Error: max_qos must be between 0 and 2 inclusive.') # Invalid maximum qos
do_test("maximum_qos -1\n", 3, 'Error: max_qos must be between 0 and 2 inclusive.') # Invalid maximum qos

do_test("max_inflight_messages 65536\n", 3, 'Error: max_inflight_messages must be <= 65535.') # Invalid value

do_test("max_keepalive 65536\n", 3, 'Error: Invalid max_keepalive value (65536).') # Invalid value
do_test("max_keepalive -1\n", 3, 'Error: Invalid max_keepalive value (-1).') # Invalid value

do_test("max_topic_alias 65536\n", 3, 'Error: Invalid max_topic_alias value in configuration.') # Invalid value
do_test("max_topic_alias -1\n", 3, 'Error: Invalid max_topic_alias value in configuration.') # Invalid value

do_test("max_topic_alias_broker 65536\n", 3, 'Error: Invalid max_topic_alias_broker value in configuration.') # Invalid value
do_test("max_topic_alias_broker -1\n", 3, 'Error: Invalid max_topic_alias_broker value in configuration.') # Invalid value

do_test("websockets_headers_size 65536\n", 3, 'Error: Websockets headers size must be between 0 and 65535 inclusive.') # Invalid value
do_test("websockets_headers_size -1\n", 3, 'Error: Websockets headers size must be between 0 and 65535 inclusive.') # Invalid value

do_test("memory_limit -1\n", 3, 'Error: Invalid memory_limit value (-1).') # Invalid value

do_test("sys_interval -1\n", 3, 'Error: Invalid sys_interval value (-1).') # Invalid value
do_test("sys_interval 65536\n", 3, 'Error: Invalid sys_interval value (65536).') # Invalid value

exit(0)