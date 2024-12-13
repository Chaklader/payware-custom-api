"""
PaywareCustomEndpoint Extension
"""

from q2_sdk.core.http_handlers.caliper_api_custom_handler import (
    Q2CaliperAPICustomHandler,
)
# from q2_sdk.core.q2_logging.filters import StringSecretsFilter
# from q2_sdk.hq.models.db_config.db_config import DbConfig
# from q2_sdk.hq.models.db_config.db_config_list import DbConfigList
# from q2_sdk.hq.models.db_config.db_env_config import DbEnvConfig, EnvValue

from .install.db_plan import DbPlan
from q2_sdk.hq.hq_api.q2_api import AddDomesticWire
from q2_sdk.hq.db.wire_domestic import WireDomestic
from q2_sdk.tools.utils import to_bool


class PaywareCustomEndpointHandler(Q2CaliperAPICustomHandler):
    ## REQUIRED_CONFIGURATIONS is a dictionary of key value pairs that are necessary
    ## for the extension to run. If set, ensures the entries are set in the
    ## extension's settings file or the web server will not start.
    ## Keys are names and values are defaults written into the settings file.
    ## To override the defaults, generate the config (`q2 generate_config`) and
    ## then alter the resulting file

    # REQUIRED_CONFIGURATIONS = {
    #    # 'CONFIG1': 'Default',
    #    # 'CONFIG2': 'Default',
    # }

    # # Behaves the same way as REQUIRED_CONFIGURATIONS, but will not stop the web server
    # # from starting if omitted from the extension's settings file
    # OPTIONAL_CONFIGURATIONS = {}

    # # Behaves in a similar manner to REQUIRED_CONFIGURATIONS,
    # # but stores the data in the database instead of the settings file. Will be
    # # written into the database on `q2 install`
    # WEDGE_ADDRESS_CONFIGS = DbConfigList([
    #     # same default for all environments
    #     DbConfig('enableOptionalLogic', False),
    #
    #     # different defaults for each environment
    #     DbEnvConfig('apiUrl', EnvValue(
    #         dev='https://dev.my-domain.com',
    #         stg='https://stage.my-domain.com',
    #         prod='https://my-domain.com'
    #     ))
    # ])

    # # Use this to filter out any secrets from XML, JSON, or python dicts
    # LOGGING_FILTERS = [StringSecretsFilter(keys=["MySecret",])]

    DESCRIPTION = "Caliper API Custom Endpoint PaywareCustomEndpoint"

    DB_PLAN = DbPlan()

    CONFIG_FILE_NAME = "PaywareCustomEndpoint"  # configuration/PaywareCustomEndpoint.py file must exist if REQUIRED_CONFIGURATIONS exist

    def __init__(self, application, request, **kwargs):
        """
        If you need variables visible through the lifetime of this request,
        feel free to add them in this function
        """
        super().__init__(application, request, **kwargs)
        # self.variable_example = 12345

    # # Uncomment this to allow the IDE to give you better hinting on a specific core (Symitar in this example)
    # from q2_cores.Symitar.core import Core as SymitarCore
    # @property
    # def core(self) -> SymitarCore:

    #     # noinspection PyTypeChecker
    #     return super().core

    async def get(self, *args, **kwargs):
        """
        A single GET method that differentiates logic based on parameters or other conditions.
        """

        # Set response type as JSON
        self.set_header("Content-Type", "application/json")

        # Example: Check if 'getWireDomestic' is present in the request parameters
        wireDomestic = to_bool(self.request_parameters.get("getWireDomestic"))

        if wireDomestic:
            # Handle the logic for WireDomestic retrieval
            object_class = WireDomestic(self.logger, hq_credentials=self.hq_credentials)
            data = await object_class.get()
            wire_domestic_data = []

            # Parse the response and extract relevant fields
            for row in data:
                wire_domestic_data.append({x.tag: x.text for x in row.getchildren()})

            response = self.return_data(wire_domestic_data)

        else:
            # Default GET response (e.g., Hello World)
            data = {"response": "Hello World GET: From payware"}
            response = self.return_data(data, success=True)

        # Log and write the response
        self.logger.info(response)
        self.write(response)

    async def post(self):
        domestic_wire_parameters = AddDomesticWire.ParamsObj(
                    self.logger,
                    self.request_parameters["UserID"],
                    self.request_parameters["HostAccountID"],
                    self.request_parameters["ProcessDate"],
                    self.request_parameters["TransactionAmount"],
                    self.request_parameters["CurrencyCodeId"],
                    self.request_parameters["RecipCountryId"],
                    self.request_parameters["SubsidiaryId"],
                    self.request_parameters["RecipFiCountryId"],
                    self.request_parameters["IntermedCountryId"],
                    self.request_parameters["TemplateId"],
                    hq_credentials=self.hq_credentials,
                )
        hq_response = await AddDomesticWire.execute(domestic_wire_parameters,use_json=True)
        print(hq_response)

        if not hq_response.success:
            self.logger.debug(f"Failed to wire transfer: {hq_response.error_message}")
            errors = [{"code": 500, "message": f"Internal platform error: failed to wire transfer"}]
            to_return = self.return_data({}, success=False, errors=errors)
            self.write(to_return)
            return
