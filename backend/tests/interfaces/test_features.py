from io import BytesIO
from pathlib import Path
import tempfile
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from beanie import PydanticObjectId
from fastapi import UploadFile
from httpx import AsyncClient

from api.common.audit_logs_repository import AuditLogRepository
from api.core.container import get_local_ai_service, get_user_preference_service
from api.core.exceptions import S3StorageException
from api.domain.dtos.audit_logs_dto import AuditLogDto
from api.domain.entities.ai import ChatHistoryAI, ChatSessionAI
from api.domain.entities.branding import Branding
from api.domain.entities.user_preference import UserPreference
from api.domain.enum.permission import Permission
from api.infrastructure.externals.azure_storage import AzureBlobStorage
from api.infrastructure.externals.file_upload import build_object_key
from api.infrastructure.externals.local_ai_model import OllamaChat
from api.infrastructure.externals.s3_storage import S3Storage
from api.common.utils import capture_audit_log
from api.usecases.file_service import FileService
from tests.factories import make_user, seed_user

STORAGE_CONFIG = {"provider": "s3", "is_enabled": True, "region": "eu-central-1"}
FAKE_ACCOUNT_KEY = "dGVzdC1rZXktdGVzdC1rZXktdGVzdC1rZXktdGVzdC1rZXk="


# ---------------------------------------------------------------- storage settings

async def test_configuring_storage_outside_a_tenant_fails_honestly(client: AsyncClient):
    """Regression: failures answered 201, with the number 400 as the body."""
    response = await client.post("/storage/configure", json=STORAGE_CONFIG)

    assert response.status_code == 406
    assert response.json()["error"] == "Tenant context is required to configure storage settings."


async def test_tenant_can_configure_storage(client: AsyncClient, act_as):
    act_as(make_user([Permission.MANAGE_STORAGE_SETTINGS], tenant_id=str(PydanticObjectId())))

    response = await client.post("/storage/configure", json=STORAGE_CONFIG)

    assert response.status_code == 201


async def test_resetting_storage_outside_a_tenant_fails_honestly(client: AsyncClient):
    response = await client.patch(f"/storage/{PydanticObjectId()}/reset")

    assert response.status_code == 406


async def test_resetting_missing_storage_is_a_404(client: AsyncClient, act_as):
    act_as(make_user([Permission.MANAGE_STORAGE_SETTINGS], tenant_id=str(PydanticObjectId())))

    response = await client.patch(f"/storage/{PydanticObjectId()}/reset")

    assert response.status_code == 404


# ---------------------------------------------------------------- uploads

@pytest.fixture
def uploaded():
    """Records what would have been stored, instead of talking to S3."""
    stored = {}

    def upload_fileobj(fileobj, bucket, key):
        stored["key"] = key
        stored["content"] = fileobj.read()

    client = MagicMock()
    client.upload_fileobj = upload_fileobj
    client.generate_presigned_url = MagicMock(return_value="https://signed.example.com/logo")
    with patch("api.infrastructure.externals.s3_storage.boto3.client", return_value=client):
        yield stored


async def test_logo_upload_stores_the_file_content(client: AsyncClient, act_as, uploaded):
    """Regression: the file was read for validation first, so an empty object got stored."""
    act_as(make_user([Permission.FULL_ACCESS], tenant_id=str(PydanticObjectId())))

    response = await client.put("/brandings/logo", files={"file": ("logo.png", b"png-bytes", "image/png")})

    assert response.status_code == 202
    assert uploaded["content"] == b"png-bytes"


async def test_logo_upload_works_without_identity(client: AsyncClient, act_as, uploaded):
    """Regression: the service read identity.app_name, which an upload doesn't send."""
    tenant_id = str(PydanticObjectId())
    act_as(make_user([Permission.FULL_ACCESS], tenant_id=tenant_id))

    await client.put("/brandings/logo", files={"file": ("first.png", b"1", "image/png")})
    await client.put("/brandings/logo", files={"file": ("second.png", b"2", "image/png")})

    branding = await Branding.find_one()
    assert branding.logo_url == uploaded["key"]
    assert str(branding.tenant_id) == tenant_id
    assert await Branding.count() == 1


async def test_svg_logos_are_rejected_cleanly(client: AsyncClient, act_as):
    """Regression: the endpoint allowed them but the DTO did not, which was a 500."""
    act_as(make_user([Permission.FULL_ACCESS], tenant_id=str(PydanticObjectId())))

    response = await client.put("/brandings/logo", files={"file": ("logo.svg", b"<svg/>", "image/svg+xml")})

    assert response.status_code == 406


async def test_host_branding_does_not_break_app_configuration(client: AsyncClient):
    """Regression: BrandingDto required a tenant, so host branding 500ed the page every user loads."""
    response = await client.post("/brandings/", json={"identity": {"app_name": "Acme"}})
    assert response.status_code == 204

    configuration = await client.get("/app_configuration/")

    assert configuration.status_code == 200
    assert configuration.json()["branding"]["app_name"] == "Acme"
    assert configuration.json()["branding"]["tenant_id"] == ""


async def test_branding_update_keeps_other_fields(client: AsyncClient):
    await client.post("/brandings/", json={"identity": {"app_name": "Acme"}})

    await client.post("/brandings/", json={"contact_info": {"phone": "123"}})

    branding = await Branding.find_one()
    assert branding.app_name == "Acme"
    assert branding.contact_info.phone == "123"


async def test_a_storage_outage_does_not_break_app_configuration(client: AsyncClient):
    await Branding(logo_url="bucket/logo.png").insert()

    with patch.object(FileService, "get_file_url", AsyncMock(side_effect=S3StorageException("down"))):
        response = await client.get("/app_configuration/")

    assert response.status_code == 200
    assert response.json()["branding"]["logo_url"] is None


async def test_profile_picture_must_be_an_image(client: AsyncClient):
    user = await seed_user()

    response = await client.put(
        f"/users/{user.id}/update_profile_picture",
        files={"file": ("a.txt", b"text", "text/plain")},
    )

    assert response.status_code == 406


async def test_profile_picture_size_is_limited(client: AsyncClient):
    user = await seed_user()

    response = await client.put(
        f"/users/{user.id}/update_profile_picture",
        files={"file": ("a.png", b"x" * (5 * 1024 * 1024 + 1), "image/png")},
    )

    assert response.status_code == 406


async def test_profile_picture_is_stored(client: AsyncClient, uploaded):
    user = await seed_user()

    response = await client.put(
        f"/users/{user.id}/update_profile_picture",
        files={"file": ("me.png", b"png", "image/png")},
    )

    assert response.status_code == 202
    assert response.json()["image_url"] == uploaded["key"]


def test_object_keys_are_unique_and_keep_only_the_file_name():
    """Regression: `bucket/<filename>` let uploads overwrite each other, across tenants too."""
    first, second = build_object_key("bucket", "logo.png"), build_object_key("bucket", "logo.png")

    assert first != second
    assert first.startswith("bucket/") and first.endswith("-logo.png")
    assert build_object_key("bucket", "../../etc/passwd").endswith("-passwd")
    assert build_object_key("bucket", "..\\..\\secret.txt").endswith("-secret.txt")
    assert build_object_key("bucket", None).endswith("-upload")


async def test_azure_read_urls_can_be_generated():
    """Regression: `datetime.utcnow` on the module and a missing key made this always fail."""
    storage = AzureBlobStorage(
        connection_string=f"DefaultEndpointsProtocol=https;AccountName=test;AccountKey={FAKE_ACCOUNT_KEY};EndpointSuffix=core.windows.net",
        container_name="files",
    )

    url = await storage.generate_read_url("files/logo.png")

    assert url.startswith("https://test.blob.core.windows.net/files/files/logo.png?")
    assert "sig=" in url


async def test_azure_upload_returns_the_key_like_s3():
    storage = AzureBlobStorage(
        connection_string=f"DefaultEndpointsProtocol=https;AccountName=test;AccountKey={FAKE_ACCOUNT_KEY};EndpointSuffix=core.windows.net",
        container_name="files",
    )
    storage.container_client = MagicMock()

    key = await storage.upload_file(UploadFile(file=BytesIO(b"data"), filename="a.png"), "files/a.png")

    assert key == "files/a.png"


async def test_s3_upload_does_not_block_with_the_right_arguments(uploaded):
    storage = S3Storage(bucket_name="b", aws_access_key="k", aws_secret_key="s", region="eu-central-1")

    key = await storage.upload_file(UploadFile(file=BytesIO(b"data"), filename="a.png"), "b/a.png")

    assert key == "b/a.png"
    assert uploaded["content"] == b"data"


# ---------------------------------------------------------------- AI

def chat_for(user_id: str, session_id: str | None) -> OllamaChat:
    return OllamaChat(
        user_id=user_id,
        username="Test",
        model_name="llama",
        current_session=session_id,
        local_ai_service=get_local_ai_service(),
    )


async def test_chat_remembers_the_conversation():
    """Regression: a string/ObjectId mismatch hid a crash, so sessions never had any memory."""
    user_id, session_id = str(PydanticObjectId()), str(PydanticObjectId())
    service = get_local_ai_service()
    await service.save_user_query(user_id, "What is 2+2?", "4", session_id=session_id)

    chat = chat_for(user_id, session_id)
    await chat.feed_previous_conversations(service)

    assert [message.content for message in chat.history[1:]] == ["What is 2+2?", "4"]


async def test_chat_appends_to_an_existing_session():
    user_id, session_id = str(PydanticObjectId()), str(PydanticObjectId())
    service = get_local_ai_service()

    await service.save_user_query(user_id, "one", "1", session_id=session_id)
    await service.save_user_query(user_id, "two", "2", session_id=session_id)

    assert await ChatSessionAI.count() == 1
    assert [h.query for h in (await ChatHistoryAI.find_one()).histories] == ["one", "two"]


async def test_chat_has_no_memory_of_other_users_sessions():
    session_id = str(PydanticObjectId())
    service = get_local_ai_service()
    await service.save_user_query(str(PydanticObjectId()), "secret", "answer", session_id=session_id)

    chat = chat_for(str(PydanticObjectId()), session_id)
    await chat.feed_previous_conversations(service)

    assert len(chat.history) == 1


@pytest.mark.parametrize("session_id", [None, "", "not-an-id"])
async def test_chat_without_a_valid_session_starts_fresh(session_id):
    chat = chat_for(str(PydanticObjectId()), session_id)

    await chat.feed_previous_conversations(get_local_ai_service())

    assert len(chat.history) == 1


async def test_deleting_a_session_removes_its_history():
    """Regression: the lookup used `id` instead of `_id`, which orphaned every history."""
    user_id, session_id = str(PydanticObjectId()), str(PydanticObjectId())
    service = get_local_ai_service()
    await service.save_user_query(user_id, "q", "a", session_id=session_id)

    await service.delete_session(user_id, session_id)

    assert await ChatSessionAI.count() == 0
    assert await ChatHistoryAI.count() == 0


# ---------------------------------------------------------------- preferences and audit logs

async def test_updating_preferences_keeps_the_document_intact():
    """Regression: the update overwrote tenant_id and created_at with defaults."""
    tenant_id, user_id = PydanticObjectId(), PydanticObjectId()
    created = await UserPreference(user_id=user_id, preferences={"a": 1}, tenant_id=tenant_id).insert()

    await get_user_preference_service().set_preferences(str(user_id), {"b": 2})

    updated = await UserPreference.get(created.id)
    assert updated.preferences == {"a": 1, "b": 2}
    assert updated.tenant_id == tenant_id


async def test_audit_logs_are_read_from_where_they_are_written():
    """Regression: writes used the system temp dir, reads a hardcoded /tmp."""
    tenant_id = str(PydanticObjectId())
    await capture_audit_log(AuditLogDto(entity="User", action="create", tenant_id=tenant_id, changes={"name": "Zoë"}))

    result = await AuditLogRepository().list_audit_logs(tenant_id=tenant_id)

    for path in Path(tempfile.gettempdir()).glob(f"audit_logs_for{tenant_id}_*.jsonl"):
        path.unlink()
    assert result.total == 1
    assert result.logs[0].changes == {"name": "Zoë"}
