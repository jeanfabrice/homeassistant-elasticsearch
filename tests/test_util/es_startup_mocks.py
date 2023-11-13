"""ES Startup Mocks."""
from homeassistant.const import CONF_URL, CONTENT_TYPE_JSON
from pytest_homeassistant_custom_component.test_util.aiohttp import AiohttpClientMocker
from custom_components.elasticsearch.config_flow import DEFAULT_ALIAS, DEFAULT_ILM_POLICY_NAME, DEFAULT_INDEX_FORMAT

from tests.const import (
    CLUSTER_HEALTH_RESPONSE_BODY,
    CLUSTER_INFO_RESPONSE_BODY,
    CLUSTER_INFO_UNSUPPORTED_RESPONSE_BODY,
    MOCK_COMPLEX_LEGACY_CONFIG,
)


def mock_es_initialization(
    aioclient_mock: AiohttpClientMocker,
    url=MOCK_COMPLEX_LEGACY_CONFIG.get(CONF_URL),
    mock_template_setup=True,
    mock_index_creation=True,
    mock_health_check=True,
    mock_ilm_setup=True,
    mock_unsupported_version=False,
    mock_authentication_error=False,
    mock_connection_error=False,
    alias_name=DEFAULT_ALIAS,
    index_format=DEFAULT_INDEX_FORMAT,
    ilm_policy_name=DEFAULT_ILM_POLICY_NAME
):
    """Mock for ES initialization flow."""

    if mock_unsupported_version:
        aioclient_mock.get(url, status=200, json=CLUSTER_INFO_UNSUPPORTED_RESPONSE_BODY)
    elif mock_authentication_error:
        aioclient_mock.get(url, status=401, json={"error": "unauthorized"})
    elif mock_connection_error:
        aioclient_mock.get(url, status=500, json={"error": "idk"})
    else:
        aioclient_mock.get(url, status=200, json=CLUSTER_INFO_RESPONSE_BODY)

    aioclient_mock.post(url + "/_bulk", status=200, json={"items": []})

    if mock_template_setup:
        aioclient_mock.get(
            url + "/_template/hass-index-template-v4_2",
            status=404,
            headers={"content-type": CONTENT_TYPE_JSON},
            json={"error": "template missing"},
        )
        aioclient_mock.put(
            url + "/_template/hass-index-template-v4_2",
            status=200,
            headers={"content-type": CONTENT_TYPE_JSON},
            json={"hi": "need dummy content"},
        )

    if mock_index_creation:
        aioclient_mock.get(
            url + f"/_alias/{alias_name}-v4_2",
            status=404,
            headers={"content-type": CONTENT_TYPE_JSON},
            json={"error": "alias missing"},
        )
        aioclient_mock.get(
            url + "/_cluster/health",
            status=200,
            headers={"content-type": CONTENT_TYPE_JSON},
            json=CLUSTER_HEALTH_RESPONSE_BODY,
        )

    if mock_health_check:
        aioclient_mock.put(
            url + f"/{index_format}-v4_2-000001",
            status=200,
            headers={"content-type": CONTENT_TYPE_JSON},
            json={"hi": "need dummy content"},
        )

    if mock_ilm_setup:
        aioclient_mock.get(
            url + f"/_ilm/policy/{ilm_policy_name}",
            status=404,
            headers={"content-type": CONTENT_TYPE_JSON},
            json={"error": "policy missing"},
        )
        aioclient_mock.put(
            url + f"/_ilm/policy/{ilm_policy_name}",
            status=200,
            headers={"content-type": CONTENT_TYPE_JSON},
            json={"hi": "need dummy content"},
        )
