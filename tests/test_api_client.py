
from cdp import __version__
from cdp.cdp_api_client import CdpApiClient
from cdp.constants import SDK


def test_api_client_get_correlation_data():
    """Tests _get_correlation_data from the CdpApiClient."""
    cdp_api_client = CdpApiClient(
        api_key = "test",
        private_key = "test",
    )
    expected_result = f"""sdk_version={__version__},sdk_language=python,source={SDK},source_version={__version__}"""
    assert cdp_api_client._get_correlation_data() == expected_result
