from cdp import __version__
from cdp.cdp import Cdp
from cdp.cdp_api_client import CdpApiClient
from cdp.constants import SDK_DEFAULT_SOURCE


def test_api_client_get_correlation_data():
    """Tests _get_correlation_data from the CdpApiClient."""
    cdp_api_client = CdpApiClient(
        api_key="test",
        private_key="test",
    )
    expected_result = f"""sdk_version={__version__},sdk_language=python,source={SDK_DEFAULT_SOURCE},source_version={__version__}"""
    assert cdp_api_client._get_correlation_data() == expected_result

    cdp_api_client2 = CdpApiClient(
        api_key="test",
        private_key="test",
        host="https://api.cdp.coinbase.com/platform",
        debugging=False,
        max_network_retries=3,
        source="test",
        source_version="test_ver",
    )
    expected_result2 = (
        f"""sdk_version={__version__},sdk_language=python,source=test,source_version=test_ver"""
    )
    assert cdp_api_client2._get_correlation_data() == expected_result2

    Cdp.configure(api_key_name="test", private_key="test")
    assert Cdp.api_clients._cdp_client._get_correlation_data() == expected_result

    Cdp.configure(api_key_name="test", private_key="test", source="test", source_version="test_ver")
    assert Cdp.api_clients._cdp_client._get_correlation_data() == expected_result2
