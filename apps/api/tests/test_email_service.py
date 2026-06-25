import os
import time
import pytest
import httpx
from unittest.mock import AsyncMock, patch, MagicMock
from core.config import settings
from services.email_service import EmailService

@pytest.fixture
def email_service():
    # Store original settings to restore later
    orig_env = settings.ENVIRONMENT
    orig_key = settings.RESEND_API_KEY
    
    yield EmailService()
    
    # Restore settings
    settings.ENVIRONMENT = orig_env
    settings.RESEND_API_KEY = orig_key


def test_compile_digest_html(email_service):
    recommendations = [
        {
            "title": "Attention Is All You Need",
            "abstract": "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks.",
            "category": "cs.CL",
            "match_score": 98,
            "url": "http://localhost:3000/digest/2026-06-07"
        },
        {
            "title": "No Abstract Paper",
            "abstract": None, # Test robust abstract slicing
            "category": "cs.LG",
            "match_score": 75,
            "url": "http://localhost:3000/digest/2026-06-07"
        }
    ]
    
    html = email_service.compile_digest_html("Dr. Shouko", recommendations)
    
    assert "Hello <strong>Dr. Shouko</strong>" in html
    assert "Attention Is All You Need" in html
    assert "cs.CL • 98% Matching" in html
    assert "The dominant sequence transduction" in html
    assert "No Abstract Paper" in html
    assert "No abstract available." in html
    assert "http://localhost:3000/digest/2026-06-07" in html


def test_compile_welcome_html(email_service):
    html = email_service.compile_welcome_html("Dr. Shouko")
    
    assert "Welcome to <span style=\"color: #a3e635;\">Shouko-AI</span>" in html
    assert "Hello Dr. Shouko," in html
    assert "Configure Research Interests" in html
    assert "Go to Workspace" in html


@pytest.mark.asyncio
async def test_send_digest_live_success(email_service):
    recommendations = [{"title": "Test Paper", "abstract": "Test abstract"}]
    
    # Configure live delivery conditions
    settings.RESEND_API_KEY = "re_livekey123"
    settings.ENVIRONMENT = "production"
    
    email_service.api_key = "re_livekey123"
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": "email_id_123"}
    
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        
        success = await email_service.send_digest("recipient@example.com", "User", recommendations)
        
        assert success is True
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert args[0] == "https://api.resend.com/emails"
        assert kwargs["headers"]["Authorization"] == "Bearer re_livekey123"
        assert kwargs["json"]["to"] == "recipient@example.com"
        assert "recipient@example.com" in kwargs["json"]["to"]


@pytest.mark.asyncio
async def test_send_digest_live_api_error(email_service):
    recommendations = [{"title": "Test Paper", "abstract": "Test abstract"}]
    
    settings.RESEND_API_KEY = "re_livekey123"
    settings.ENVIRONMENT = "production"
    email_service.api_key = "re_livekey123"
    
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.text = "Bad Request: Invalid Email"
    
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        
        # In live production mode, errors are raised as RuntimeError
        with pytest.raises(RuntimeError) as exc_info:
            await email_service.send_digest("recipient@example.com", "User", recommendations)
            
        assert "Resend API error (Code 400)" in str(exc_info.value)


@pytest.mark.asyncio
async def test_send_welcome_email_live_success(email_service):
    settings.RESEND_API_KEY = "re_livekey123"
    settings.ENVIRONMENT = "production"
    email_service.api_key = "re_livekey123"
    
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.json.return_value = {"id": "welcome_email_123"}
    
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        
        success = await email_service.send_welcome_email("recipient@example.com", "User")
        
        assert success is True
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert kwargs["json"]["to"] == "recipient@example.com"
        assert kwargs["json"]["subject"] == "Welcome to Shouko-AI! 🤖"


@pytest.mark.asyncio
async def test_send_digest_sandbox_fallback(email_service):
    recommendations = [{"title": "Test Sandbox Paper", "abstract": "Test sandbox abstract"}]
    
    # Empty API key triggers sandbox
    email_service.api_key = ""
    settings.ENVIRONMENT = "development"
    
    # Clear any existing sandboxed emails
    if os.path.exists(email_service.sandbox_dir):
        for f in os.listdir(email_service.sandbox_dir):
            if f.startswith("digest_email_"):
                os.remove(os.path.join(email_service.sandbox_dir, f))
                
    success = await email_service.send_digest("sandbox_recipient@example.com", "Sandbox User", recommendations)
    
    assert success is True
    # Verify a sandbox file was written
    files = [f for f in os.listdir(email_service.sandbox_dir) if f.startswith("digest_email_")]
    assert len(files) == 1
    
    filepath = os.path.join(email_service.sandbox_dir, files[0])
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        
    assert "Hello <strong>Sandbox User</strong>" in content
    assert "Test Sandbox Paper" in content
    
    # Cleanup
    os.remove(filepath)


@pytest.mark.asyncio
async def test_send_welcome_email_sandbox_fallback(email_service):
    email_service.api_key = "re_invalid_for_dev"
    # "test" environment forces sandbox fallback even with a key set
    settings.ENVIRONMENT = "test"
    
    # Clear any existing sandboxed welcome emails
    if os.path.exists(email_service.sandbox_dir):
        for f in os.listdir(email_service.sandbox_dir):
            if f.startswith("welcome_email_"):
                os.remove(os.path.join(email_service.sandbox_dir, f))
                
    success = await email_service.send_welcome_email("sandbox_recipient@example.com", "Sandbox User")
    
    assert success is True
    # Verify a sandbox file was written
    files = [f for f in os.listdir(email_service.sandbox_dir) if f.startswith("welcome_email_")]
    assert len(files) == 1
    
    filepath = os.path.join(email_service.sandbox_dir, files[0])
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        
    assert "Welcome to <span style=\"color: #a3e635;\">Shouko-AI</span>" in content
    assert "Hello Sandbox User," in content
    
    # Cleanup
    os.remove(filepath)
