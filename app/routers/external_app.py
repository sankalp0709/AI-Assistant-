from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# FIXED IMPORT ✔
from ..core.external_integrations import ExternalIntegrations

router = APIRouter()

class AppRequest(BaseModel):
    app: str  # notion, googlesheets, trello, email, webhook
    action: str
    params: dict = {}

integrations = ExternalIntegrations()

@router.post("/external_app")
async def interact_external_app(request: AppRequest):
    try:
        if request.app == 'notion':
            integration = integrations.get_integration(request.app)
            if request.action == 'create_page':
                result = integration.create_page(**request.params)
            elif request.action == 'update_page':
                result = integration.update_page(**request.params)
            else:
                raise HTTPException(status_code=400, detail=f"Invalid action '{request.action}' for Notion")

        elif request.app == 'googlesheets':
            integration = integrations.get_integration(request.app)
            if request.action == 'append_row':
                result = integration.append_row(**request.params)
            else:
                raise HTTPException(status_code=400, detail=f"Invalid action '{request.action}' for GoogleSheets")

        elif request.app == 'trello':
            integration = integrations.get_integration(request.app)
            if request.action == 'create_card':
                result = integration.create_card(**request.params)
            else:
                raise HTTPException(status_code=400, detail=f"Invalid action '{request.action}' for Trello")

        elif request.app == 'email':
            integration = integrations.get_integration(request.app)
            if request.action in ('send_email', 'send'):
                try:
                    result = integration.send_email(**request.params)
                except Exception:
                    result = {"status": "stub", "email_action": request.action, "message": "Fallback stub"}
            else:
                raise HTTPException(status_code=400, detail=f"Invalid action '{request.action}' for Email")

        elif request.app == 'webhook':
            integration = integrations.get_integration(request.app)
            if request.action == 'post':
                result = integration.post_webhook(**request.params)
            else:
                raise HTTPException(status_code=400, detail=f"Invalid action '{request.action}' for Webhook")

        elif request.app in ('crm', 'erp', 'calendar'):
            result = {"status": "stub", f"{request.app}_action": request.action, "message": "Integration not configured"}

        else:
            raise HTTPException(status_code=400, detail=f"Unsupported app '{request.app}'")

        return {"result": result}

    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"Configuration error: {str(e)}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Integration error: {str(e)}")
