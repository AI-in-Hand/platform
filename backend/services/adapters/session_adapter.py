from backend.models.session_config import SessionConfig, SessionConfigForAPI
from backend.repositories.agency_config_storage import AgencyConfigStorage
from backend.services.adapters.agency_adapter import AgencyAdapter


class SessionAdapter:
    """
    Adapter for the SessionConfig model. Transforms the data from the frontend format to the model and vice versa.
    In particular, it fills the `flow_config` field with an AgencyConfigForAPI object based on an agency_id string.
    """

    def __init__(self, agency_config_storage: AgencyConfigStorage, agency_adapter: AgencyAdapter):
        self.agency_config_storage = agency_config_storage
        self.agency_adapter = agency_adapter

    def to_api(self, session_config: SessionConfig) -> SessionConfigForAPI:
        """
        Converts the SessionConfig model to the API model.
        """
        agency_config = self.agency_config_storage.load_by_id(session_config.agency_id)
        if agency_config is None:
            raise ValueError(f"Agency with id {session_config.agency_id} not found")

        agency_config_for_api = self.agency_adapter.to_api(agency_config)

        session_config_dict = session_config.model_dump()
        session_config_dict["flow_config"] = agency_config_for_api
        session_config_new = SessionConfigForAPI.model_validate(session_config_dict)
        return session_config_new
