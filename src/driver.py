#!/usr/bin/python
# -*- coding: utf-8 -*-


from cloudshell.devices.driver_helper import get_logger_with_thread_id, get_api, get_cli
from cloudshell.devices.standards.networking.configuration_attributes_structure import create_networking_resource_from_context
# from cloudshell.networking.cisco.runners.cisco_connectivity_runner import \
#     CiscoConnectivityRunner as ConnectivityRunner
# from cloudshell.networking.cisco.runners.cisco_configuration_runner import \
#     CiscoConfigurationRunner as ConfigurationRunner
from cloudshell.networking.alcatel.runners.alcatel_autoload_runner import AlcatelAutoloadRunner as AutoloadRunner
# from cloudshell.networking.cisco.runners.cisco_firmware_runner import CiscoFirmwareRunner as FirmwareRunner
# from cloudshell.networking.cisco.runners.cisco_run_command_runner import CiscoRunCommandRunner as CommandRunner
# from cloudshell.networking.cisco.runners.cisco_state_runner import CiscoStateRunner as StateRunner
from cloudshell.networking.networking_resource_driver_interface import NetworkingResourceDriverInterface
from cloudshell.shell.core.context import ResourceCommandContext
from cloudshell.shell.core.driver_utils import GlobalLock
from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface


class AlcatelTimetrashellDriver(ResourceDriverInterface, NetworkingResourceDriverInterface, GlobalLock):
    SUPPORTED_OS = [r"TiMOS"]
    # SHELL_NAME = "Alcatel TimOS Switch 2G"
    SHELL_NAME = ""

    def __init__(self):
        super(AlcatelTimetrashellDriver, self).__init__()
        self._cli = None

    def initialize(self, context):
        """Initialize method

        :type context: cloudshell.shell.core.context.driver_context.InitCommandContext
        """

        resource_config = create_networking_resource_from_context(shell_name=self.SHELL_NAME,
                                                                  supported_os=self.SUPPORTED_OS,
                                                                  context=context)

        session_pool_size = int(resource_config.sessions_concurrency_limit)
        self._cli = get_cli(session_pool_size)
        return 'Finished initializing'

    @GlobalLock.lock
    def get_inventory(self, context):
        """Return device structure with all standard attributes

        :param ResourceCommandContext context: ResourceCommandContext object with all Resource Attributes inside
        :return: response
        :rtype: str
        """

        logger = get_logger_with_thread_id(context)
        api = get_api(context)

        resource_config = create_networking_resource_from_context(shell_name=self.SHELL_NAME,
                                                                  supported_os=self.SUPPORTED_OS,
                                                                  context=context)

        autoload_operations = AutoloadRunner(cli=self._cli,
                                             logger=logger,
                                             resource_config=resource_config,
                                             api=api)
        logger.info('Autoload started')
        response = autoload_operations.discover()
        logger.info('Autoload completed')
        return response

    def run_custom_command(self, context, custom_command):
        """Send custom command

        :param ResourceCommandContext context: ResourceCommandContext object with all Resource Attributes inside
        :return: result
        :rtype: str
        """

        pass

    def run_custom_config_command(self, context, custom_command):
        """Send custom command in configuration mode

        :param ResourceCommandContext context: ResourceCommandContext object with all Resource Attributes inside
        :return: result
        :rtype: str
        """

        pass

    def ApplyConnectivityChanges(self, context, request):
        """
        Create vlan and add or remove it to/from network interface

        :param ResourceCommandContext context: ResourceCommandContext object with all Resource Attributes inside
        :param str request: request json
        :return:
        """

        pass

    def save(self, context, folder_path, configuration_type, vrf_management_name):
        """Save selected file to the provided destination

        :param ResourceCommandContext context: ResourceCommandContext object with all Resource Attributes inside
        :param configuration_type: source file, which will be saved
        :param folder_path: destination path where file will be saved
        :param vrf_management_name: VRF management Name
        :return str saved configuration file name:
        """

        pass

    @GlobalLock.lock
    def restore(self, context, path, configuration_type, restore_method, vrf_management_name):
        """Restore selected file to the provided destination

        :param ResourceCommandContext context: ResourceCommandContext object with all Resource Attributes inside
        :param path: source config file
        :param configuration_type: running or startup configs
        :param restore_method: append or override methods
        :param vrf_management_name: VRF management Name
        """

        pass

    def orchestration_save(self, context, mode, custom_params):
        """

        :param ResourceCommandContext context: ResourceCommandContext object with all Resource Attributes inside
        :param mode: mode
        :param custom_params: json with custom save parameters
        :return str response: response json
        """

        pass

    def orchestration_restore(self, context, saved_artifact_info, custom_params):
        """

        :param ResourceCommandContext context: ResourceCommandContext object with all Resource Attributes inside
        :param saved_artifact_info: OrchestrationSavedArtifactInfo json
        :param custom_params: json with custom restore parameters
        """

        pass

    @GlobalLock.lock
    def load_firmware(self, context, path, vrf_management_name):
        """Upload and updates firmware on the resource

        :param ResourceCommandContext context: ResourceCommandContext object with all Resource Attributes inside
        :param path: full path to firmware file, i.e. tftp://10.10.10.1/firmware.tar
        :param vrf_management_name: VRF management Name
        """

        pass

    def health_check(self, context):
        """Performs device health check

        :param ResourceCommandContext context: ResourceCommandContext object with all Resource Attributes inside
        :return: Success or Error message
        :rtype: str
        """

        pass

    def cleanup(self):
        pass

    def shutdown(self, context):
        """ Shutdown device

        :param ResourceCommandContext context: ResourceCommandContext object with all Resource Attributes inside
        :return:
        """

        pass
