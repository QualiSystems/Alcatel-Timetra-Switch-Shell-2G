#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.devices.driver_helper import get_logger_with_thread_id, get_api, get_cli, \
    parse_custom_commands
from cloudshell.devices.runners.run_command_runner import RunCommandRunner as CommandRunner
from cloudshell.devices.runners.state_runner import StateRunner
from cloudshell.devices.standards.networking.configuration_attributes_structure import \
    create_networking_resource_from_context
from cloudshell.networking.networking_resource_driver_interface import \
    NetworkingResourceDriverInterface
from cloudshell.shell.core.driver_context import InitCommandContext, ResourceCommandContext
from cloudshell.shell.core.driver_utils import GlobalLock
from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface

from cloudshell.networking.alcatel.cli.alcatel_cli_handler import AlcatelCliHandler as CliHandler
from cloudshell.networking.alcatel.runners.alcatel_autoload_runner import AlcatelAutoloadRunner \
    as AutoloadRunner
from cloudshell.networking.alcatel.runners.alcatel_configuration_runner import \
    AlcatelConfigurationRunner as ConfigurationRunner
from cloudshell.networking.alcatel.runners.alcatel_connectivity_runner import \
    AlcatelConnectivityRunner as ConnectivityRunner
from cloudshell.networking.alcatel.runners.alcatel_firmware_runner import AlcatelFirmwareRunner \
    as FirmwareRunner
from cloudshell.networking.alcatel.snmp.alcatel_snmp_handler import AlcatelSnmpHandler as \
    SnmpHandler


class AlcatelTimetraRouterShell2GDriver(ResourceDriverInterface, NetworkingResourceDriverInterface,
                                        GlobalLock):
    SUPPORTED_OS = [r"TiMOS"]
    SHELL_NAME = "AlcatelTimetraRouterShell2G"

    def __init__(self):
        super(AlcatelTimetraRouterShell2GDriver, self).__init__()
        self._cli = None

    def initialize(self, context):
        """Initialize method

        :param InitCommandContext context: the context the command runs on
        """

        resource_config = create_networking_resource_from_context(
            self.SHELL_NAME, self.SUPPORTED_OS, context)

        session_pool_size = int(resource_config.sessions_concurrency_limit)
        self._cli = get_cli(session_pool_size)
        return 'Finished initializing'

    @GlobalLock.lock
    def get_inventory(self, context):
        """Return device structure with all standard attributes

        :param ResourceCommandContext context: ResourceCommandContext object with all Resource
            Attributes inside
        :return: response
        :rtype: str
        """

        logger = get_logger_with_thread_id(context)
        api = get_api(context)

        resource_config = create_networking_resource_from_context(
            self.SHELL_NAME, self.SUPPORTED_OS, context)
        cli_handler = CliHandler(self._cli, resource_config, logger, api)
        snmp_handler = SnmpHandler(resource_config, logger, api, cli_handler)

        autoload_operations = AutoloadRunner(resource_config, logger, snmp_handler)
        logger.info('Autoload started')
        response = autoload_operations.discover()
        logger.info('Autoload completed')
        return response

    def run_custom_command(self, context, custom_command):
        """Send custom command

        :param custom_command: Command to run
        :param ResourceCommandContext context: ResourceCommandContext object with all Resource
            Attributes inside
        :return: result
        :rtype: str
        """

        logger = get_logger_with_thread_id(context)
        api = get_api(context)

        resource_config = create_networking_resource_from_context(
            self.SHELL_NAME, self.SUPPORTED_OS, context)
        cli_handler = CliHandler(self._cli, resource_config, logger, api)

        command_operations = CommandRunner(logger, cli_handler)
        return command_operations.run_custom_command(parse_custom_commands(custom_command))

    def run_custom_config_command(self, context, custom_command):
        """Send custom command in configuration mode

        :param custom_command: Config command to run
        :param ResourceCommandContext context: ResourceCommandContext object with all Resource
            Attributes inside
        :return: result
        :rtype: str
        """

        logger = get_logger_with_thread_id(context)
        api = get_api(context)

        resource_config = create_networking_resource_from_context(
            self.SHELL_NAME, self.SUPPORTED_OS, context)
        cli_handler = CliHandler(self._cli, resource_config, logger, api)

        command_operations = CommandRunner(logger, cli_handler)
        return command_operations.run_custom_config_command(parse_custom_commands(custom_command))

    def ApplyConnectivityChanges(self, context, request):
        """
        Create vlan and add or remove it to/from network interface

        :param ResourceCommandContext context: ResourceCommandContext object with all Resource
            Attributes inside
        :param str request: request json
        :return:
        """

        logger = get_logger_with_thread_id(context)
        api = get_api(context)

        resource_config = create_networking_resource_from_context(
            self.SHELL_NAME, self.SUPPORTED_OS, context)
        cli_handler = CliHandler(self._cli, resource_config, logger, api)

        connectivity_operations = ConnectivityRunner(logger, cli_handler)
        logger.info('Start applying connectivity changes, request is: {0}'.format(str(request)))
        result = connectivity_operations.apply_connectivity_changes(request)
        logger.info('Finished applying connectivity changes, response is: {0}'.format(str(result)))
        logger.info('Apply Connectivity changes completed')
        return result

    def save(self, context, folder_path, configuration_type, vrf_management_name):
        """Save selected file to the provided destination

        :param ResourceCommandContext context: ResourceCommandContext object with all Resource
            Attributes inside
        :param configuration_type: startup or running
        :param folder_path: destination path where file will be saved
        :param vrf_management_name: VRF management Name
        :return str saved configuration file name:
        """

        logger = get_logger_with_thread_id(context)
        api = get_api(context)

        resource_config = create_networking_resource_from_context(
            self.SHELL_NAME, self.SUPPORTED_OS, context)
        cli_handler = CliHandler(self._cli, resource_config, logger, api)

        configuration_type = configuration_type or 'running'
        vrf_management_name = vrf_management_name or resource_config.vrf_management_name

        configuration_operations = ConfigurationRunner(logger, resource_config, api, cli_handler)
        logger.info('Save started')
        response = configuration_operations.save(
            folder_path=folder_path,
            configuration_type=configuration_type,
            vrf_management_name=vrf_management_name,
        )
        logger.info('Save completed')
        return response

    @GlobalLock.lock
    def restore(self, context, path, configuration_type, restore_method, vrf_management_name):
        """Restore selected file to the provided destination

        :param ResourceCommandContext context: ResourceCommandContext object with all Resource
            Attributes inside
        :param path: source config file
        :param configuration_type: running or startup configs
        :param restore_method: append or override methods
        :param vrf_management_name: VRF management Name
        """

        logger = get_logger_with_thread_id(context)
        api = get_api(context)

        resource_config = create_networking_resource_from_context(
            self.SHELL_NAME, self.SUPPORTED_OS, context)
        cli_handler = CliHandler(self._cli, resource_config, logger, api)

        configuration_type = configuration_type or 'running'
        restore_method = restore_method or 'override'
        vrf_management_name = vrf_management_name or resource_config.vrf_management_name

        configuration_operations = ConfigurationRunner(logger, resource_config, api, cli_handler)
        logger.info('Restore started')
        configuration_operations.restore(
            path=path,
            restore_method=restore_method,
            configuration_type=configuration_type,
            vrf_management_name=vrf_management_name,
        )
        logger.info('Restore completed')

    def orchestration_save(self, context, mode, custom_params):
        """

        :param ResourceCommandContext context: ResourceCommandContext object with all Resource
            Attributes inside
        :param mode: mode
        :param custom_params: json with custom save parameters
        :return str response: response json
        """

        logger = get_logger_with_thread_id(context)
        api = get_api(context)

        resource_config = create_networking_resource_from_context(
            self.SHELL_NAME, self.SUPPORTED_OS, context)
        cli_handler = CliHandler(self._cli, resource_config, logger, api)

        mode = mode or 'shallow'

        configuration_operations = ConfigurationRunner(logger, resource_config, api, cli_handler)
        logger.info('Orchestration save started')
        response = configuration_operations.orchestration_save(
            mode=mode,
            custom_params=custom_params,
        )
        logger.info('Orchestration save completed')
        return response

    def orchestration_restore(self, context, saved_artifact_info, custom_params):
        """

        :param ResourceCommandContext context: ResourceCommandContext object with all Resource
            Attributes inside
        :param saved_artifact_info: OrchestrationSavedArtifactInfo json
        :param custom_params: json with custom restore parameters
        """

        logger = get_logger_with_thread_id(context)
        api = get_api(context)

        resource_config = create_networking_resource_from_context(
            self.SHELL_NAME, self.SUPPORTED_OS, context)
        cli_handler = CliHandler(self._cli, resource_config, logger, api)

        configuration_operations = ConfigurationRunner(logger, resource_config, api, cli_handler)
        logger.info('Orchestration restore started')
        configuration_operations.orchestration_restore(
            saved_artifact_info=saved_artifact_info,
            custom_params=custom_params,
        )
        logger.info('Orchestration restore completed')

    @GlobalLock.lock
    def load_firmware(self, context, path, vrf_management_name):
        """Upload and updates firmware on the resource

        :param ResourceCommandContext context: ResourceCommandContext object with all Resource
            Attributes inside
        :param path: full path to firmware file, i.e. tftp://10.10.10.1/firmware.tar
        :param vrf_management_name: VRF management Name
        """

        logger = get_logger_with_thread_id(context)
        api = get_api(context)

        resource_config = create_networking_resource_from_context(
            self.SHELL_NAME, self.SUPPORTED_OS, context)
        cli_handler = CliHandler(self._cli, resource_config, logger, api)

        vrf_management_name = vrf_management_name or resource_config.vrf_management_name

        logger.info('Start Load Firmware')
        firmware_operations = FirmwareRunner(logger, cli_handler)
        response = firmware_operations.load_firmware(path, vrf_management_name=vrf_management_name)
        logger.info('Finish Load Firmware: {}'.format(response))

    def health_check(self, context):
        """Performs device health check

        :param ResourceCommandContext context: ResourceCommandContext object with all Resource
            Attributes inside
        :return: Success or Error message
        :rtype: str
        """

        logger = get_logger_with_thread_id(context)
        api = get_api(context)

        resource_config = create_networking_resource_from_context(
            self.SHELL_NAME, self.SUPPORTED_OS, context)
        cli_handler = CliHandler(self._cli, resource_config, logger, api)

        state_operations = StateRunner(logger, api, resource_config, cli_handler)
        return state_operations.health_check()

    def cleanup(self):
        pass

    def shutdown(self, context):
        """ Shutdown device

        :param ResourceCommandContext context: ResourceCommandContext object with all Resource
            Attributes inside
        :return:
        """

        logger = get_logger_with_thread_id(context)
        api = get_api(context)

        resource_config = create_networking_resource_from_context(
            self.SHELL_NAME, self.SUPPORTED_OS, context)
        cli_handler = CliHandler(self._cli, resource_config, logger, api)

        state_operations = StateRunner(logger, api, resource_config, cli_handler)
        return state_operations.shutdown()
